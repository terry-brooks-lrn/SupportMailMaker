
import asyncio
from os import environ, getenv
import sys
from datetime import datetime
from typing import Union, Dict, Any, Tuple
import json
import gradio as gr
from loguru import logger
from formatter import Formatter
from utils import log_file, clear_logs
from gradio_log import Log
import aiofiles
import csv
import io

# ── CSV column-header → internal-key mapping ──────────────────────────────
# Real-world CSV files arrive with varying header conventions (mixed case,
# punctuation, abbreviations).  Each internal key maps to a **tuple of
# accepted aliases** so that any reasonable header variant is recognised.
# Matching is case-insensitive and strips leading/trailing whitespace.
CSV_COLUMN_ALIASES: Dict[str, tuple] = {
    "type": (
        "section",
        "type",
        "ticket_type",
    ),
    "topic_domain": (
        "topic_domain",
        "topic/domain",
    ),
    "title": (
        "title",
    ),
    "customer": (
        "customer",
    ),
    "summary": (
        "summary",
        "subject matter/summary",
    ),
    "url": (
        "ticket_link",
        "link",
    ),
    "include": (
        "add_to_edition",
        "add_to_edition?",
        "include",
    ),
}

# Pre-compute a fast lookup: lowercased-alias → internal key
_ALIAS_LOOKUP: Dict[str, str] = {}
for _internal_key, _aliases in CSV_COLUMN_ALIASES.items():
    for _alias in _aliases:
        _ALIAS_LOOKUP[_alias.lower().strip()] = _internal_key


# Truthy string values accepted for the ``add_to_edition`` CSV column.
_TRUTHY_STRINGS = frozenset({"true", "1", "yes", "✅"})


def _coerce_bool(value: Any) -> bool:
    """Convert a CSV cell value to a Python bool.

    Accepts ``True`` / ``False`` booleans as-is, and treats common
    truthy strings (case-insensitive) — ``"true"``, ``"1"``, ``"yes"``,
    ``"✅"`` — as ``True``.  Everything else is ``False``.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in _TRUTHY_STRINGS
    return False


def normalize_csv_rows(rows: list[dict]) -> list[dict]:
    """Re-key each CSV row from upload-template headers to internal keys.

    Header matching is **case-insensitive** and supports multiple aliases
    per internal key (see ``CSV_COLUMN_ALIASES``).  Unmapped columns
    (e.g. ``owner``, ``notes``, ``client_number``) are silently dropped.
    The ``include`` field is coerced to a Python ``bool`` so that
    ``collate_content`` can use ``if item.get("include") is True``.

    Args:
        rows: A list of dicts produced by ``csv.DictReader``.

    Returns:
        A new list of dicts with normalised keys.
    """
    normalised = []
    for row in rows:
        new_row: Dict[str, Any] = {key: "" for key in CSV_COLUMN_ALIASES}
        for csv_header, value in row.items():
            if csv_header is None:
                continue
            internal_key = _ALIAS_LOOKUP.get(csv_header.lower().strip())
            if internal_key is not None:
                new_row[internal_key] = value if value is not None else ""
        # Coerce include from string → bool
        new_row["include"] = _coerce_bool(new_row.get("include", ""))
        normalised.append(new_row)
    return normalised


# Initialize current formatter with the current date
now = datetime.now().strftime("%Y-%m-%d")
current_edition = Formatter(publish_date=now)

# Placeholder JSON content
PLACEHOLDER_JSON = """
{
    "publish_date": "null",
    "content": {
        "issues": [],
        "oops": [],
        "wins": [],
        "news": []
    }
}
"""


def build_interface(formatter):
    """Builds the user interface for the application.

    This function creates and arranges the various components of the UI,
    including input fields, buttons, and output displays. It also sets up the
    interaction logic between these elements.

    Returns:
        gr.Blocks: The Gradio Blocks application instance.
    """
    with gr.Blocks() as application:
        create_header()
        inp, inp2 = create_inputs()
        process_btn, markdown_option, output_log = create_actions()
        download_file = create_output()

        process_btn.click(
            fn=is_ready_to_publish_async, inputs=[inp, inp2], outputs=[download_file, inp, inp2]
        )
        markdown_option.select(fn=on_select, inputs=markdown_option)
        inp2.upload(log_file_name_async, inp2)

    return application


def create_header():
    """
    Create the header and instructions for the Gradio app.
    """
    with gr.Column():
        gr.Markdown("# SupportMail Auto Formatter")
        gr.Markdown("### Instructions:")
        gr.Markdown("\1. Enter JSON Content into the JSON field or Upload it Via the File Upload Field. _Note: These Are Mutually Exclusive. Adding a Value To Both Will Cause an Error._ \n")
        gr.Markdown("\2. Press the 'Send To Presses' button to format content into SupportMail Format.\n")
        gr.Markdown("\3. Download the formatted file when completed.")
        gr.Markdown("### Note: If an Error Is received during Processing. Reset UI by reloading browser window.")


def create_inputs():
    """
    Create input fields for JSON content and file upload.
    """
    with gr.Row():
        gr.HTML("<h2>Content Input</h2>")
    with gr.Row():
        inp = gr.Textbox(
            label="JSON Content",
            value=PLACEHOLDER_JSON,
            show_label=True,
            interactive=True,
        )
        inp2 = gr.File(
            file_types=[".csv"], file_count="single", label="Upload File"
        )
    return inp, inp2


def create_actions() -> Tuple[gr.Button, gr.Checkbox, Log]:
    """
    Create the process button and log output display.
    """
    with gr.Row():
        md_option = gr.Checkbox(label="Include Markdown with HTML?")
        process_btn = gr.Button("Send To Presses 🖨️", elem_id="send_to_presses")
    with gr.Row():
        output_log = Log(
            log_file=log_file,
            dark=True,
            label="Formatter Status",
            show_label=True,
            interactive=False,
            every=0.1,
            xterm_log_level="DEBUG",
        )
    return process_btn, md_option, output_log


def create_output():
    with gr.Row():
        output_file = gr.File(label="Download File", visible=False)
    return output_file


async def is_ready_to_publish_async(json_input: str, file_input: Any, progress=gr.Progress(track_tqdm=True)) -> Any:
    """
    Check if content is ready for publishing and trigger formatting.
    """
    try:
        if json_input and json_input != PLACEHOLDER_JSON:
            file_input = None
            current_edition.context['publish_date'] = current_edition.publish_date
            content = json_input
        elif file_input is not None:
            json_input = None
            # Asynchronously read file content
            async with aiofiles.open(file_input, "r") as f:
                csv_data = await f.read()

            # 2) Convert that string data into an in-memory buffer
                data_buffer = io.StringIO(csv_data)

            # 3) Pass the buffer to csv.DictReader
                csv_reader = csv.DictReader(data_buffer)

            # 4) Convert the reader to a list of dictionaries and normalise
            #    CSV column headers to the internal keys collate_content expects.
                content = normalize_csv_rows(list(csv_reader))
                current_edition.context['publish_date'] = current_edition.publish_date
        else:
            logger.warning("No valid input provided!")
            return None

        # Set content in the formatter and initiate publishing
        try:
            current_edition.set_raw_content(content)
            if await current_edition.send_to_press_async():
                return await current_edition.publish_async()
        except ValueError as ve:
            logger.error("Invalid Content File Uploaded. Resetting Press...Please Try Again")
    except Exception as e:
        logger.error(f"Content is not ready for publishing: {e}")
        raise RuntimeError("Content is not ready for publishing.") from e


def on_select(value, evt: gr.EventData):
    current_edition.include_markdown = value


async def log_file_name_async(file):
    logger.info(f"File uploaded: {file.name}")


@logger.catch
def main(app):
    app.launch(
        inbrowser=True,
        debug=True,
        share=True,
        show_error=True,
        state_session_capacity=10000,
        quiet=False,
        enable_monitoring=True,
        server_port=int(getenv('GRADIO_SERVER_PORT', 7500))
    )

if __name__ == "__main__":
    try:
        UI = build_interface(current_edition)
        port = getenv('GRADIO_SERVER_PORT', '7500')
        print(
            f"Starting The Presses at http://127.0.0.1:{port}...\n\n"
        )
        main(UI)
    except KeyboardInterrupt:
        print("\nProgram Terminated By User...\nResetting Logs...")
        clear_logs()
        sys.exit(0)
