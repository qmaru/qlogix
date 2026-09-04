ARG PYTHON_VERSION=3.14

FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-trixie-slim AS builder

ARG GIT_COMMIT

WORKDIR /app

COPY uv.lock pyproject.toml README.md ./

RUN uv sync --frozen --no-install-project

COPY src ./src

RUN printf '__commit__ = "%s"\n' "$GIT_COMMIT" > src/qlogix/_build.py

RUN uv sync --frozen --no-editable --no-dev

FROM cgr.dev/chainguard/wolfi-base AS prod

ARG PYTHON_VERSION

WORKDIR /app

RUN apk add --no-cache python-${PYTHON_VERSION}-base \
    && mkdir /usr/local/bin \
    && ln -s /usr/bin/python${PYTHON_VERSION} /usr/local/bin/python3

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ENTRYPOINT ["qlogix-cli"]
