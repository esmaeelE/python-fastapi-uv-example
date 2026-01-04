# FastAPI with UV

A new basic FastAPI with uv
This is boilerplate for future projects.

```bash
pre-commit run --all-files
```

## Run

```bash
uv run fastapi run
```

```bash
$ curl -s localhost:8000/ip | jq .
{
  "ip": "5.239.173.67"
}
```

## Install

```bash
docker compose up -d
```

## Develop

```bash
uv run fastapi dev
```
