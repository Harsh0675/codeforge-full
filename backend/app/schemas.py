from enum import Enum
from pydantic import BaseModel, Field

class Language(str, Enum):
    python = "python"
    c = "c"
    cpp = "cpp"
    java = "java"
    javascript = "javascript"
    typescript = "typescript"
    go = "go"
    rust = "rust"
    php = "php"

class RunRequest(BaseModel):
    language: Language
    source: str = Field(min_length=1, max_length=256_000)
    stdin: str = Field(default="", max_length=64_000)

class RunAccepted(BaseModel):
    id: str
    status: str

class RunResult(BaseModel):
    id: str
    status: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    duration_ms: int | None = None
    memory_kb: int | None = None
