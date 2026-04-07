from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "dev-secret"

    # Database
    database_url: str = "sqlite+aiosqlite:///./meal_planner.db"

    # LLM
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    # Recipe APIs
    spoonacular_api_key: str = ""
    edamam_app_id: str = ""
    edamam_app_key: str = ""

    # Recipe cache
    recipe_cache_ttl_days: int = 7


settings = Settings()
