from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    request_timeout: float = 10.0
    max_concurrent_audits: int = 10
    cache_ttl_seconds: int = 300

    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()