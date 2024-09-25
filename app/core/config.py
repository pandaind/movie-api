from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    app_name: str
    environment: str
    debug: bool
    database_url: str

    class Config:
        env_file = ".env"  # Point to the .env file

# Instantiate the settings object
settings = Settings()
