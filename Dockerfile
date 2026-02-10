# syntax=docker/dockerfile:1

# --- Build stage: install dependencies ---
FROM python:3.10-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

COPY requirements.prod.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --prefix=/install -r requirements.prod.txt

# --- Runtime stage: minimal final image ---
FROM python:3.10-slim

LABEL Maintainer="Terry Brooks, Jr. <terry.Brooks@learnosity.com>"
LABEL Name="SupportMail Generator"
LABEL Version="1"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_PORT=7500
ENV GRADIO_NUM_PORTS=1000
ENV GRADIO_NODE_NUM_PORTS=1000
ENV GRADIO_ANALYTICS_ENABLED=True
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV SUPPORTMAIL_HTML_TEMPLATE="/src/templates"

WORKDIR /src

# Install Task (taskfile.dev) runner
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source and Taskfile
COPY support_mail_maker/ /src/
COPY Taskfile.yml /src/

# Create non-root user and switch to it
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --no-create-home appuser \
    && chown -R appuser:appuser /src

USER appuser

EXPOSE 7500

ENTRYPOINT ["task"]
CMD ["start"]
