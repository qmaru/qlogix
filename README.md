# qlogix

easy log fetch.

`source -> filter - analyze - sink`

## Installation

```bash
uv tool install git+https://github.com/qmaru/qlogix.git
```

## Usage

```bash
# pipeline by config.toml
qlogix-cli run

# pipeline by command
qlogix-cli pipeline http https://httpbun.com/get safe passthrough stdout

## source
qlogix-cli source http https://httpbun.com/get

## filter
qlogix-cli filter safe http https://httpbun.com/ip

## analyze
qlogix-cli analyze passthrough http https://httpbun.com/get

## sink
qlogix-cli sink stdout http https://httpbun.com/get
```

## hold

Keep the process running without executing any qlogix work, for example when
you need to enter the container shell:

```bash
qlogix-cli hold
```

## docker

```bash
# pipeline by config.toml
# https://raw.githubusercontent.com/qmaru/qlogix/refs/heads/main/config.example.toml
# https://raw.githubusercontent.com/qmaru/qlogix/refs/heads/main/compose.yaml
docker run --rm \
    -e QLOGIX_CONFIG=/app/config.toml \
    -v ./config.toml:/app/config.toml:ro \
    ghcr.io/qmaru/qlogix run

# compose
# local
docker compose run --build --rm qlogix -h

# remote
docker compose run --rm qlogix -h
```

To keep a container alive for shell access:

```bash
docker compose run -d --name qlogix-hold qlogix hold
docker exec -it qlogix-hold /bin/sh
```
