
# SupportMailMaker

SupportMailMaker is an intelligent parser and formatter designed specifically for Learnosity SupportMail. It simplifies the process of structuring support emails by providing efficient parsing, templating, and formatting tools. This project aims to enhance productivity and ensure consistent communication within the support workflow.

## Table of Contents

1. [Features](#features)
2. [Getting Started](#getting-started)
3. [Installation](#installation)
4. [Task Commands](#task-commands)
5. [Usage](#usage)
   - [Gradio Web Interface](#gradio-web-interface)
   - [CLI](#cli)
6. [Testing](#testing)
7. [Docker Support](#docker-support)
8. [Contributing](#contributing)
9. [Roadmap](#roadmap)
10. [License](#license)
11. [Acknowledgments](#acknowledgments)

---

## Features

- **Efficient Parsing:** Automatically extracts and formats key details from Learnosity SupportMail.
- **Customizable Templates:** Allows you to define and use email templates tailored to your workflow.
- **Gradio UI Integration:** Provides a user-friendly web interface for parsing and formatting operations.
- **Typer CLI:** A full-featured command-line interface built with Typer and Rich for headless/scriptable workflows — supports JSON, CSV, trends HTML, and markdown output with branded terminal styling.
- **Dockerized Deployment:** Includes a Docker setup for seamless deployment in any environment.
- **Taskfile Automation:** All common workflows (server, CLI, tests, Docker, linting) managed through a single `Taskfile.yml`.

---

## Getting Started

Follow these instructions to set up the project on your local machine and get it running.

### Prerequisites

Ensure you have the following tools installed:

- Python 3.10 or higher
- [Task](https://taskfile.dev) — task runner (`brew install go-task` on macOS)
- Docker (optional but recommended)
- pip or [Poetry](https://python-poetry.org/) (Python package manager)

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Terry-BrooksJr/SupportMailMaker.git
   cd SupportMailMaker
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or with Poetry:
   ```bash
   poetry install
   ```

3. **Run the Application:**
   ```bash
   task start
   ```

---

## Task Commands

All project workflows are managed through [Taskfile](https://taskfile.dev). Run `task --list` to see every available command.

### Server

| Command | Description |
|---|---|
| `task start` | Start the Gradio server on the default port (7500) |
| `task start -- 8000` | Start the server on a custom port |
| `PORT=8080 task start` | Start the server using an environment variable |

> **Aliases:** `task serve`, `task run`

### CLI

| Command | Description |
|---|---|
| `task cli -- publish --csv data.csv` | Format a CSV file into SupportMail HTML |
| `task cli -- publish --json-file content.json` | Format a JSON file |
| `task cli -- publish --csv data.csv --markdown` | Include Markdown output alongside HTML |
| `task cli -- template` | Export the CSV upload template |
| `task cli -- schema` | Print the JSON validation schema |

> **Alias:** `task publish`

### Testing

| Command | Description |
|---|---|
| `task test` | Run the full test suite |
| `task test:verbose` | Run tests with verbose (`-v`) output |
| `task test:coverage` | Run tests with a coverage report |
| `task test -- -k "test_item"` | Pass additional pytest arguments |

> **Alias:** `task tests`

### Linting & Formatting

| Command | Description |
|---|---|
| `task lint` | Check code style (isort + black) without modifying files |
| `task fmt` | Auto-format code with isort and black |

> **Alias:** `task format`

### Docker

| Command | Description |
|---|---|
| `task docker:build` | Build the Docker image |
| `task docker:run` | Build and run the container (port 7500) |
| `task docker:stop` | Stop the running container |
| `IMAGE_TAG=v2 task docker:build` | Build with a custom tag |

### Utilities

| Command | Description |
|---|---|
| `task clear-logs` | Truncate the main log file |
| `task clean` | Remove caches, `.pyc` files, and clear logs |

> **Alias:** `task clean-logs`

---

## Usage

### Gradio Web Interface

Start the application and open the provided URL in your browser:

```bash
task start
```

The Gradio web interface will be available at `http://localhost:7500`. From there you can:

1. Paste JSON content into the JSON field **or** upload a CSV file via the file upload field. _(These are mutually exclusive.)_
2. Optionally paste HTML into the Trends section.
3. Press **Send To Presses** to format the content into SupportMail format.
4. Download the generated HTML and Markdown files.

### CLI

The CLI provides identical functionality to the web interface, designed for headless environments, scripting, and CI/CD pipelines.

```bash
# Run directly
python support_mail_maker/cli.py publish --csv data.csv --date 2026-02-10 --markdown

# Or via Taskfile
task cli -- publish --csv data.csv --date 2026-02-10 --markdown
```

#### Commands

| Command | Description |
|---|---|
| `publish` | Format support content into branded HTML & Markdown |
| `serve` | Launch the Gradio web UI |
| `template` | Export the CSV upload template |
| `schema` | Print the JSON validation schema |

#### `publish` Options

| Option | Short | Description |
|---|---|---|
| `--json` | `-j` | Inline JSON string with content payload |
| `--json-file` | `-J` | Path to a JSON file containing the content payload |
| `--csv` | `-c` | Path to a CSV file with support mail items |
| `--trends` | `-t` | Inline HTML string for the Trends section |
| `--trends-file` | `-T` | Path to an HTML file for the Trends section |
| `--markdown` | `-m` | Include a Markdown (.md) file alongside HTML |
| `--date` | `-d` | Publish date in YYYY-MM-DD format (defaults to today) |

> **Note:** `--json`, `--json-file`, and `--csv` are mutually exclusive — provide exactly one.

#### Examples

```bash
# Format from CSV with markdown output
python support_mail_maker/cli.py publish --csv data.csv --markdown

# Format from a JSON file with a custom publish date
python support_mail_maker/cli.py publish --json-file content.json --date 2026-03-01

# Include trends from an HTML file
python support_mail_maker/cli.py publish --csv data.csv --trends-file trends.html

# Export the CSV template to see expected columns
python support_mail_maker/cli.py template --output my_template.csv

# View the content validation schema
python support_mail_maker/cli.py schema
```

---

## Testing

The project includes a comprehensive test suite built with **pytest** and **pytest-asyncio**.

### Test Structure

```
support_mail_maker/tests/
    conftest.py          # Shared fixtures
    test_inputs.py       # ItemType enum & Item class tests
    test_formatter.py    # Formatter class tests (sync + async)
    test_utils.py        # Utility function & schema validation tests
```

### Running Tests

```bash
# Run all tests
task test

# Verbose output
task test:verbose

# With coverage
task test:coverage

# Run a specific test file
task test -- support_mail_maker/tests/test_formatter.py

# Run tests matching a keyword
task test -- -k "test_collate"
```

### What's Covered

| Module | Area | Tests |
|---|---|---|
| `formatter.py` | `ItemType` enum values, iteration | 6 |
| `formatter.py` | `Item` creation, validation, dict access, repr, serialization | 22 |
| `formatter.py` | `Formatter` init, dict access, add/get items, `set_raw_content` | 17 |
| `formatter.py` | `collate_content`, `send_to_press_async`, `save_to_file` (async) | 10 |
| `utils.py` | `load_schema` — file, URL fallback, caching, invalid JSON | 7 |
| `utils.py` | `valid_JSON_input` — valid/invalid payloads, missing fields | 9 |
| `utils.py` | `clear_logs`, `StreamToLogger` | 9 |
| | **Total** | **80+** |

---

## Docker Support

SupportMailMaker ships with a multi-stage Dockerfile that includes the [Task](https://taskfile.dev) binary as the entrypoint.

### Build and Run

```bash
# Build the image
task docker:build

# Build and run in one step
task docker:run

# Or run manually with Docker
docker build -t supportmailmaker .
docker run --rm -p 7500:7500 supportmailmaker
```

### Running Other Tasks Inside the Container

Because the container uses `task` as its `ENTRYPOINT`, you can run any Taskfile command:

```bash
# Run the test suite inside the container
docker run --rm supportmailmaker test

# Start on a different port
docker run --rm -p 8080:8080 -e GRADIO_SERVER_PORT=8080 supportmailmaker start
```

### Stop the Container

```bash
task docker:stop
```

Access the Gradio interface at `http://localhost:7500`.

---

## Roadmap

- ~~Full CLI~~ — Shipped via Typer + Rich
- ~~Add ability to upload a template~~ — Available via `cli.py template`

---

## Contributing

We welcome contributions! To get started:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Make your changes and ensure tests pass:
   ```bash
   task test
   task lint
   ```
4. Commit your changes:
   ```bash
   git commit -m "Description of your changes"
   ```
5. Push the branch:
   ```bash
   git push origin feature-name
   ```
6. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Learnosity:** For providing the inspiration and use case for this project.
- **Gradio:** For the powerful web UI framework.
- **Typer & Rich:** For the stylish CLI experience.

Feel free to open an issue or contact us if you have questions or feedback!
