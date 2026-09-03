import time, uuid, json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from .config import settings
from .schemas import RunRequest, RunAccepted
from .queue import enqueue

app = FastAPI(title="CodeForge API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
    allow_methods=["*"], allow_headers=["*"]
)

redis = Redis.from_url(settings.redis_url, decode_responses=True)

@app.get("/health")
async def health():
    await redis.ping()
    return {"status": "ok", "service": "codeforge-api"}

@app.post("/api/v1/runs", response_model=RunAccepted)
async def create_run(req: RunRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"rate:runs:{client_ip}"
    request_count = await redis.incr(rate_key)
    if request_count == 1:
        await redis.expire(rate_key, settings.run_rate_window_seconds)
    if request_count > settings.run_rate_limit:
        raise HTTPException(429, "Too many run requests. Try again shortly.", headers={"Retry-After": str(settings.run_rate_window_seconds)})
    if len(req.source.encode()) > settings.max_source_bytes:
        raise HTTPException(413, "Source is too large")
    if len(req.stdin.encode()) > settings.max_stdin_bytes:
        raise HTTPException(413, "stdin is too large")
    run_id = str(uuid.uuid4())
    payload = {
        "id": run_id,
        "language": req.language.value,
        "source": req.source,
        "stdin": req.stdin,
        "created_at": time.time(),
    }
    await redis.hset(f"run:{run_id}", mapping={"status": "queued"})
    await enqueue(redis, payload)
    return {"id": run_id, "status": "queued"}

@app.get("/api/v1/runs/{run_id}")
async def get_run(run_id: str):
    result = await redis.hgetall(f"run:{run_id}")
    if not result:
        raise HTTPException(404, "Run not found")
    for key in ("exit_code", "duration_ms", "memory_kb"):
        if key in result and result[key] not in ("", "None"):
            result[key] = int(result[key])
    return result
