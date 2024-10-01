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