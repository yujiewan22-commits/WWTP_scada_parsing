from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Water Plant AI V3"
    database_url: str = "sqlite:///./water_plant_ai.db"
    upload_dir: str = "./data/uploads"

    ai_provider: str = "mock"
    ai_base_url: str | None = None
    ai_api_key: str | None = None
    ai_model: str | None = None
    ai_timeout_seconds: int = 120
    ai_max_pdf_pages: int = 8

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
