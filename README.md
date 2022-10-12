# Hackathon CodeBattle
API for October CodeBattle Hackathon.

## Stack
[Starlite](https://starlite-api.github.io/starlite/),
[SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/en/latest/front.html),
[Postgres](https://www.postgresql.org/), [Redis](https://redis.io/), [Traefik](https://doc.traefik.io/traefik/)

## Configuration
Docker containers:
 1. server
 2. traefik

docker-compose files:
 1. `docker-compose.yml` - for local development.
 2. `docker-compose-dev.yml` - for local development (without traefik).
 3. `tests/functional/docker-compose.yml` - for functional tests.

To run docker containers, you need to create a `.env` file in the root directory.

**`.env` example:**
```shell
cp .env.example .env
```

### Start project:

Locally:
```shell
docker-compose build
docker-compose up
```

## Development
Sync environment with `requirements.txt` / `requirements.dev.txt` (will install/update missing packages, remove redundant ones):
```shell
make sync-requirements
```

Compile requirements.\*.txt files (have to re-compile after changes in requirements.\*.in):
```shell
make compile-requirements
```

Use `requirements.local.in` for local dependencies; always specify _constraints files_ (-c ...)

Example:
```shell
# requirements.local.txt

-c requirements.txt

ipython
```

### Tests
Run unit tests (export environment variables from `.env` file):
```shell
export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst) && make test
```

To run functional tests, you need to create `.env` in ./tests/functional directory

**`.env` example:**
```shell
cd ./tests/functional && cp .env.example .env
```

Run functional tests:
```shell
cd ./tests/functional && docker-compose up test
```

Makefile recipe:
```shell
make dtf
```

### Code style:
Before pushing a commit run all linters:

```shell
make lint
```

### pre-commit:
pre-commit installation:
```shell
pre-commit install
```

## Documentation
OpenAPI 3 documentation:
- `${PROJECT_BASE_URL}/api/v1/docs` - Swagger
- `${PROJECT_BASE_URL}/api/v1/docs/redoc` - ReDoc
- `${PROJECT_BASE_URL}/api/v1/docs/openapi.json` - OpenAPI json
