import os

import uvicorn
from alembic.config import Config

from alembic import command

alembic_cfg = Config("alembic.ini")


if __name__ == "__main__":
    # Run upgrade command (replace 'head' with your target revision if needed)
    command.upgrade(alembic_cfg, "head")

    environment = os.getenv("ENVIRONMENT", "development")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        env_file=f".env.{environment}",
    )
