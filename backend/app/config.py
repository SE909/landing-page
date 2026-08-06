from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "landing_page_creator"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    upload_dir: str = "uploads"
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
