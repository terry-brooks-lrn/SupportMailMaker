# Docker Guide — SupportMailMaker

This guide covers building, running, testing, and deploying the SupportMailMaker Docker image.

## Architecture

The image uses a **multi-stage build** based on `python:3.10-slim`:

1. **Builder stage** — installs Python dependencies into an isolated prefix.
2. **Runtime stage** — copies only the installed packages, application source, and [Task](https://taskfile.dev) binary into a minimal image running as a non-root user.

The container uses **`task` as its `ENTRYPOINT`** with `start` as the default `CMD`. This means every Taskfile command is available directly through `docker run`.

---

## Quick Start

### Using Taskfile commands (recommended)

```bash
# Build the image
task docker:build

# Build and run in one step (port 7500)
task docker:run

# Stop the running container
task docker:stop
```

### Using Docker directly

```bash
docker build -t supportmailmaker .
docker run --rm -p 7500:7500 --name supportmailmaker supportmailmaker
```

Your application will be available at **http://localhost:7500**.

---

## Running Tasks Inside the Container

Because the entrypoint is `task`, you can run any Taskfile command by passing it as the Docker `CMD`:

```bash
# Start the server (default)
docker run --rm -p 7500:7500 supportmailmaker

# Run the test suite
docker run --rm supportmailmaker test

# Run tests with verbose output
docker run --rm supportmailmaker test:verbose

# Clear logs
docker run --rm supportmailmaker clear-logs

# List all available tasks
docker run --rm supportmailmaker --list
```

---

## Running Tests in Docker

Run the full test suite (80+ tests across `formatter.py`, `utils.py`, `Item`, and `ItemType`):

```bash
docker run --rm supportmailmaker test
```

Verbose output:

```bash
docker run --rm supportmailmaker test:verbose
```

> **Note:** `test:coverage` requires `pytest-cov` to be included in `requirements.prod.txt` if you want to run coverage reports inside the container.

---

## Custom Configuration

### Port

Override the default port (7500) by setting the `GRADIO_SERVER_PORT` environment variable and publishing the matching port:

```bash
docker run --rm -p 8080:8080 -e GRADIO_SERVER_PORT=8080 supportmailmaker start
```

Or with the Taskfile:

```bash
PORT=8080 task docker:run
```

### Image Name and Tag

```bash
# Custom tag
IMAGE_TAG=v2 task docker:build

# Custom image name
IMAGE_NAME=myregistry/supportmail IMAGE_TAG=1.0.0 task docker:build
```

### Overriding the Entrypoint

If you need a shell inside the container:

```bash
docker run --rm -it --entrypoint /bin/bash supportmailmaker
```

---

## Docker Compose

Start the application with Compose:

```bash
docker compose up --build
```

The Gradio interface will be available at **http://localhost:7500**.

---

## Deploying to the Cloud

1. **Build the image** for the target platform:
   ```bash
   docker build --platform=linux/amd64 -t supportmailmaker .
   ```

2. **Tag for your registry:**
   ```bash
   docker tag supportmailmaker myregistry.com/supportmailmaker:latest
   ```

3. **Push:**
   ```bash
   docker push myregistry.com/supportmailmaker:latest
   ```

See Docker's [getting started guide](https://docs.docker.com/go/get-started-sharing/) for more detail on building and pushing.

---

## Environment Variables

The following environment variables are baked into the image with sensible defaults and can be overridden at runtime with `-e`:

| Variable | Default | Description |
|---|---|---|
| `GRADIO_SERVER_PORT` | `7500` | Port the Gradio server listens on |
| `GRADIO_NUM_PORTS` | `1000` | Number of ports Gradio can use |
| `GRADIO_NODE_NUM_PORTS` | `1000` | Number of node ports Gradio can use |
| `GRADIO_ANALYTICS_ENABLED` | `True` | Enable Gradio analytics |
| `GRADIO_SERVER_NAME` | `0.0.0.0` | Bind address |
| `SUPPORTMAIL_HTML_TEMPLATE` | `/src/templates` | Path to the HTML template directory |

---

## References

- [Docker's Python guide](https://docs.docker.com/language/python/)
- [Taskfile documentation](https://taskfile.dev)
- [Gradio deployment docs](https://www.gradio.app/guides/sharing-your-app)
