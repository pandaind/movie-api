import os
import uvicorn

if __name__ == "__main__":
    environment = os.getenv("ENVIRONMENT", "development")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, env_file=f".env.{environment}")