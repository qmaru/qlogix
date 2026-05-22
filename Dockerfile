FROM python:3.13-slim-trixie AS builder

WORKDIR /build

COPY pyproject.toml README.md ./

COPY src ./src

RUN pip wheel --no-cache-dir --wheel-dir /dist .

RUN pip install --no-cache-dir --prefix /runtime /dist/*.whl

RUN python -m compileall -q /runtime

FROM gcr.io/distroless/python3-debian13 AS prod

WORKDIR /app

ENV PYTHONPATH=/runtime/lib/python3.13/site-packages

COPY --from=builder /runtime /runtime

ENTRYPOINT ["/usr/bin/python3", "/runtime/bin/qlogix-cli"]
