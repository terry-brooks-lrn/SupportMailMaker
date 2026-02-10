"""
SupportMail Auto Formatter — CLI

A Rich + Typer CLI that mirrors every capability of the Gradio web interface:
  * JSON input (inline or from file)
  * CSV file upload with automatic header normalisation
  * Optional trends HTML (inline string or file path)
  * Markdown toggle
  * Real-time Rich console feedback
"""

import asyncio
import csv
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# ── CSV column-header mapping (shared with app.py) ──────────────────
# Duplicated here to avoid importing app.py which pulls in gradio.
_CSV_COLUMN_ALIASES: dict[str, tuple] = {
    "type": ("section", "type", "ticket_type"),
    "topic_domain": ("topic_domain", "topic/domain"),
    "title": ("title",),
    "customer": ("customer",),
    "summary": ("summary", "subject matter/summary"),
    "url": ("ticket_link", "link"),
    "include": ("add_to_edition", "add_to_edition?", "include"),
}

_ALIAS_LOOKUP: dict[str, str] = {}
for _k, _aliases in _CSV_COLUMN_ALIASES.items():
    for _a in _aliases:
        _ALIAS_LOOKUP[_a.lower().strip()] = _k

_TRUTHY_STRINGS = frozenset({"true", "1", "yes", "\u2705"})


def _coerce_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in _TRUTHY_STRINGS
    return False


def _normalize_csv_rows(rows: list[dict]) -> list[dict]:
    """Re-key CSV rows from upload-template headers to internal keys."""
    normalised = []
    for row in rows:
        new_row: dict = {key: "" for key in _CSV_COLUMN_ALIASES}
        for csv_header, value in row.items():
            if csv_header is None:
                continue
            internal_key = _ALIAS_LOOKUP.get(csv_header.lower().strip())
            if internal_key is not None:
                new_row[internal_key] = value if value is not None else ""
        new_row["include"] = _coerce_bool(new_row.get("include", ""))
        normalised.append(new_row)
    return normalised

# ── Brand theme (mirrors Learnosity palette) ────────────────────────
_THEME = Theme(
    {
        "midnight": "bold #00313D",
        "cobalt": "bold #0071CE",
        "ruby": "bold #CE0E2D",
        "honey": "#FFCB00",
        "success": "bold green",
        "warn": "bold yellow",
        "err": "bold red",
        "muted": "dim",
    }
)

console = Console(theme=_THEME)

# ── Typer app ────────────────────────────────────────────────────────
cli = typer.Typer(
    name="supportmail",
    help="SupportMail Auto Formatter — format support content into branded HTML & Markdown.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _banner() -> None:
    """Print the branded header banner."""
    banner_text = Text()
    banner_text.append("  SupportMail ", style="bold white on #00313D")
    banner_text.append(" Auto Formatter ", style="bold #FFCB00 on #00313D")

    console.print()
    console.print(
        Panel(
            banner_text,
            border_style="cobalt",
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
            subtitle="[muted]Learnosity Internal Tool[/muted]",
        )
    )
    console.print()


def _print_instructions() -> None:
    """Print usage instructions matching the Gradio header."""
    instructions = Table.grid(padding=(0, 2))
    instructions.add_column(style="cobalt", justify="right", width=4)
    instructions.add_column()
    instructions.add_row("1.", "Provide content via [cobalt]--json[/cobalt] / [cobalt]--json-file[/cobalt] or [cobalt]--csv[/cobalt] (mutually exclusive)")
    instructions.add_row("2.", "Optionally add trends HTML via [cobalt]--trends[/cobalt] or [cobalt]--trends-file[/cobalt]")
    instructions.add_row("3.", "Add [cobalt]--markdown[/cobalt] to include a Markdown file alongside HTML")
    instructions.add_row("4.", "Output files are saved to the current directory")

    console.print(
        Panel(
            instructions,
            title="[midnight]Instructions[/midnight]",
            border_style="cobalt",
            box=box.ROUNDED,
        )
    )
    console.print()


def _summary_table(formatter) -> None:
    """Print a summary table of collated items."""
    table = Table(
        title="Collation Summary",
        box=box.SIMPLE_HEAVY,
        header_style="midnight",
        title_style="cobalt",
    )
    table.add_column("Section", style="cobalt", min_width=10)
    table.add_column("Count", justify="right", style="midnight")

    for section in ("issues", "oops", "wins", "news"):
        count = len(formatter.get_items(section))
        style = "success" if count > 0 else "muted"
        table.add_row(section.capitalize(), f"[{style}]{count}[/{style}]")

    console.print(table)
    console.print()


def _result_panel(paths: list[str]) -> None:
    """Print a panel showing the generated output files."""
    listing = Table.grid(padding=(0, 2))
    listing.add_column(style="success", width=3)
    listing.add_column()
    for p in paths:
        listing.add_row("-->", str(p))

    console.print(
        Panel(
            listing,
            title="[success]Files Generated[/success]",
            border_style="success",
            box=box.ROUNDED,
        )
    )
    console.print()


# ── Async core (reuses formatter / app logic directly) ──────────────

async def _run_publish(
    content_data,
    publish_date: str,
    trend_html: str,
    include_markdown: bool,
) -> list[str]:
    """Drive the Formatter through the same pipeline as the Gradio callback.

    ``send_to_press_async`` internally calls ``collate_content`` then
    ``publish_async``, so a single call handles the full pipeline.
    """
    # Suppress tqdm output — we use Rich progress instead
    os.environ["TQDM_DISABLE"] = "1"

    # Pre-configure loguru before importing formatter/utils so that
    # the stdout sink added by utils.py is suppressed in CLI mode.
    from loguru import logger as _logger
    _logger.remove()  # remove default stderr handler
    _log_path = os.path.join(os.getcwd(), "logs", "main.log")
    _logger.add(_log_path, encoding="utf8", level="DEBUG")
    # Patch sys.stdout temporarily so that when utils.py calls
    # logger.add(sys.stdout, ...) it gets a no-op sink.
    import sys as _sys
    _real_stdout = _sys.stdout

    class _NullStream:
        def write(self, *a, **kw): pass
        def flush(self, *a, **kw): pass

    _sys.stdout = _NullStream()

    from formatter import Formatter

    _sys.stdout = _real_stdout

    formatter = Formatter(publish_date=publish_date)
    formatter.include_markdown = include_markdown
    formatter.set_raw_content(content_data)
    formatter.context["publish_date"] = formatter.publish_date
    formatter.context["content"]["trend_html"] = trend_html

    with Progress(
        SpinnerColumn(style="cobalt"),
        TextColumn("[midnight]{task.description}"),
        BarColumn(bar_width=30, style="cobalt", complete_style="success"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing & publishing...", total=None)
        ready = await formatter.send_to_press_async()
        progress.update(task, description="Processing & publishing...", completed=100, total=100)

    if not ready:
        console.print("[err]Publish pipeline failed — see log output above.[/err]")
        raise typer.Exit(code=1)

    _summary_table(formatter)

    # Derive the output file paths that send_to_press_async wrote
    edition = formatter.publish_date.strftime("%l")
    publish_year = formatter.publish_date.strftime("%Y")
    root_filename = f"{publish_year}_support_mail_{edition}"

    import pathlib
    output_paths: list[str] = []
    for ext in ("html", "md"):
        p = pathlib.Path.cwd() / f"{root_filename}.{ext}"
        if p.exists():
            output_paths.append(str(p))

    return output_paths


# ── Main command ─────────────────────────────────────────────────────

@cli.command()
def publish(
    json_input: Optional[str] = typer.Option(
        None,
        "--json", "-j",
        help="Inline JSON string with publish_date and content (issues, oops, wins, news).",
    ),
    json_file: Optional[Path] = typer.Option(
        None,
        "--json-file", "-J",
        help="Path to a JSON file containing the content payload.",
        exists=True,
        readable=True,
        resolve_path=True,
    ),
    csv_file: Optional[Path] = typer.Option(
        None,
        "--csv", "-c",
        help="Path to a CSV file with support mail items.",
        exists=True,
        readable=True,
        resolve_path=True,
    ),
    trends: Optional[str] = typer.Option(
        None,
        "--trends", "-t",
        help="Inline HTML string for the Trends section.",
    ),
    trends_file: Optional[Path] = typer.Option(
        None,
        "--trends-file", "-T",
        help="Path to an HTML file whose contents populate the Trends section.",
        exists=True,
        readable=True,
        resolve_path=True,
    ),
    markdown: bool = typer.Option(
        False,
        "--markdown", "-m",
        help="Include a Markdown (.md) file alongside the HTML output.",
    ),
    publish_date: Optional[str] = typer.Option(
        None,
        "--date", "-d",
        help="Publish date in YYYY-MM-DD format. Defaults to today.",
    ),
) -> None:
    """
    [bold #0071CE]Send To Presses[/bold #0071CE] — format support content into branded HTML & Markdown.

    Provide content via exactly [bold]one[/bold] of --json, --json-file, or --csv.
    """
    _banner()
    _print_instructions()

    # ── Validate mutual exclusivity ──────────────────────────────────
    sources = sum(x is not None for x in (json_input, json_file, csv_file))
    if sources == 0:
        console.print("[err]Error:[/err] Provide content via --json, --json-file, or --csv.")
        raise typer.Exit(code=1)
    if sources > 1:
        console.print("[err]Error:[/err] --json, --json-file, and --csv are mutually exclusive.")
        raise typer.Exit(code=1)

    # ── Resolve publish date ─────────────────────────────────────────
    if publish_date is None:
        publish_date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(publish_date, "%Y-%m-%d")
        except ValueError:
            console.print(f"[err]Error:[/err] Invalid date format '{publish_date}'. Use YYYY-MM-DD.")
            raise typer.Exit(code=1)

    # ── Resolve trends HTML ──────────────────────────────────────────
    trend_html = ""
    if trends is not None:
        trend_html = trends
    elif trends_file is not None:
        trend_html = trends_file.read_text(encoding="utf-8")
        console.print(f"[cobalt]Trends HTML[/cobalt] loaded from [muted]{trends_file}[/muted]")

    # ── Resolve content source ───────────────────────────────────────
    content_data = None

    if json_input is not None:
        console.print("[cobalt]Source:[/cobalt] inline JSON")
        try:
            parsed = json.loads(json_input)
        except json.JSONDecodeError as exc:
            console.print(f"[err]JSON parse error:[/err] {exc}")
            raise typer.Exit(code=1)
        content_data = parsed

    elif json_file is not None:
        console.print(f"[cobalt]Source:[/cobalt] JSON file [muted]{json_file}[/muted]")
        try:
            content_data = json.loads(json_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            console.print(f"[err]JSON parse error:[/err] {exc}")
            raise typer.Exit(code=1)

    elif csv_file is not None:
        console.print(f"[cobalt]Source:[/cobalt] CSV file [muted]{csv_file}[/muted]")
        raw_text = csv_file.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(raw_text))
        content_data = _normalize_csv_rows(list(reader))

        # Quick preview
        included = sum(1 for r in content_data if r.get("include") is True)
        total = len(content_data)
        console.print(f"  [muted]{total} row(s) read, {included} marked for inclusion[/muted]")

    console.print(f"[cobalt]Publish date:[/cobalt] {publish_date}")
    console.print(f"[cobalt]Markdown:[/cobalt] {'yes' if markdown else 'no'}")
    if trend_html:
        console.print(f"[cobalt]Trends HTML:[/cobalt] {len(trend_html)} chars")
    console.print()

    # ── Run the async publish pipeline ───────────────────────────────
    paths = asyncio.run(
        _run_publish(
            content_data=content_data,
            publish_date=publish_date,
            trend_html=trend_html,
            include_markdown=markdown,
        )
    )

    if paths:
        _result_panel(paths)
        console.print("[success]Done![/success] Files are ready for distribution.\n")
    else:
        console.print("[warn]No output files were generated.[/warn]")
        raise typer.Exit(code=1)


# ── Serve command (launches the existing Gradio UI) ──────────────────

@cli.command()
def serve(
    port: int = typer.Option(
        7500,
        "--port", "-p",
        help="Port number for the Gradio web UI.",
    ),
) -> None:
    """
    [bold #0071CE]Launch the Gradio web UI[/bold #0071CE] (same as `task start`).
    """
    _banner()
    console.print(f"[cobalt]Starting web UI[/cobalt] on port [midnight]{port}[/midnight]...")
    console.print()

    os.environ["GRADIO_SERVER_PORT"] = str(port)

    from app import build_interface, main as launch_app, current_edition

    ui = build_interface(current_edition)
    launch_app(ui)


# ── Template command ─────────────────────────────────────────────────

@cli.command()
def template(
    output: Path = typer.Option(
        Path("upload_template.csv"),
        "--output", "-o",
        help="Path to write the CSV template.",
    ),
) -> None:
    """
    [bold #0071CE]Export the CSV upload template[/bold #0071CE] so you know the expected columns.
    """
    _banner()

    src = Path(__file__).parent / "templates" / "upload_template.csv"
    if not src.exists():
        console.print("[err]Template file not found in package.[/err]")
        raise typer.Exit(code=1)

    import shutil
    shutil.copy2(src, output)
    console.print(f"[success]CSV template written to[/success] {output.resolve()}")
    console.print()


# ── Schema command ───────────────────────────────────────────────────

@cli.command()
def schema() -> None:
    """
    [bold #0071CE]Print the JSON validation schema[/bold #0071CE] for the content payload.
    """
    _banner()

    schema_path = Path(__file__).parent / "support_mail.schema.json"
    if not schema_path.exists():
        console.print("[err]Schema file not found.[/err]")
        raise typer.Exit(code=1)

    from rich.syntax import Syntax

    raw = schema_path.read_text(encoding="utf-8")
    syntax = Syntax(raw, "json", theme="monokai", line_numbers=True)
    console.print(
        Panel(
            syntax,
            title="[cobalt]support_mail.schema.json[/cobalt]",
            border_style="cobalt",
            box=box.ROUNDED,
        )
    )
    console.print()


# ── Entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
