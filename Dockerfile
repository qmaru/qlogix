FROM python:3.13-slim-trixie AS builder

ARG GIT_COMMIT

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src

RUN printf '__commit__ = "%s"\n' "$GIT_COMMIT" > src/qlogix/_build.py

RUN pip install \
    --no-cache-dir \
    --disable-pip-version-check \
    --compile \
    --prefix=/runtime \
    .

FROM gcr.io/distroless/python3-debian13 AS prod

WORKDIR /app

ENV PYTHONPATH=/runtime/lib/python3.13/site-packages

COPY --from=builder /runtime /runtime

ENTRYPOINT ["/usr/bin/python3", "/runtime/bin/qlogix-cli"]
