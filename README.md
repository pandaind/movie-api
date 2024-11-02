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

## Run Gunicorn
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Add Http to HTTPS Redirection
```python
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import (
    HTTPSRedirectMiddleware,
)
app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)
```

## Run on HTTPS
```bash
unicorn main:app --port 443 --ssl-keyfile keyfile.pem --ssl-certfile cert.pem
```

## To build your project using Hatch, follow these steps:

1. **Ensure Hatch is installed**:
   ```bash
   pip install hatch
   ```

2. **Initialize your project with Hatch** (if not already done):
   ```bash
   hatch new my_project
   ```

3. **Configure your `pyproject.toml` file** (as you have already done).

4. **Create and manage your virtual environment**:
   ```bash
   hatch env create
   ```

5. **Build your project**:
   ```bash
   hatch build
   ```

6. **Run your project**:
   ```bash
   hatch run python start.py
   ```

