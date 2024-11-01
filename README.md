# Fast Api Learning Project

## start application
```bash
    python start.py
```
## start docker compose
```bash
    docker-compose up --build
```
## Running Unittests
```bash
    python -m unittest discover -s tests
```
## Running PyTests
```bash
    pytest
```

## Run DB
```bash
docker run --name postgres_db -e POSTGRES_USER=movie_api_user -e POSTGRES_PASSWORD=movie_api_pass -e POSTGRES_DB=movie_api_db -p 5432:5432 -d  postgres:13
```

## Run Black
```bash
black .
```

## Run Isort
```bash
isort .
```
## Install Pre-commit
```bash
pre-commit install
```

## Run Pre-commit
```bash
pre-commit run --all-files
```

## Migration
```bash
alembic revision --autogenerate -m "create table"
alembic upgrade head
```

## Generate gRPC
```bash
 python -m grpc_tools.protoc --proto_path=. ./grpcserver.proto --python_out=. --grpc_python_out=.
```