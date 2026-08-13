from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    mock_llm: bool = True
    llm_provider: str = "mock"
    embedding_provider: str = "mock"
    hybrid_keyword_weight: float = 0.5
    hybrid_vector_weight: float = 0.5
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)


settings = Settings()
