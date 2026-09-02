from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "sqlite+aiosqlite:///./codeforge.db"
    cors_origins: str = "http://localhost:5173"
    max_source_bytes: int = 256_000
    max_stdin_bytes: int = 64_000
    queue_timeout_seconds: int = 5

settings = Settings()
