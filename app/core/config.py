import os

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    app_name: str
    environment: str
    debug: bool
    database_url: str

    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'development')}"  # Load the appropriate .env file

# Instantiate the settings object
settings = Settings()