from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Water Plant SCADA Agents V1"
    database_url: str = "sqlite:///./water_plant_scada.db"
    upload_dir: str = "./data/uploads"

    ai_provider: str = "openai_compatible"
    ai_base_url: str | None = None
    ai_api_key: str | None = None
    ai_model: str | None = None
    ai_timeout_seconds: int = 120
    ai_json_mode: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
