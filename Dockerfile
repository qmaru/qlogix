FROM python:3.13-slim-trixie AS builder

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip wheel --no-cache-dir --wheel-dir /dist .

FROM python:3.13-slim-trixie AS prod

WORKDIR /app

ENV TZ=Asia/Shanghai
ENV PYTHONUNBUFFERED=1

COPY --from=builder /dist /dist

RUN pip install --no-cache-dir /dist/*.whl \
    && rm -rf /dist

CMD ["qlogix"]
