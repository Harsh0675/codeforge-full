import json
from redis.asyncio import Redis
from .config import settings

QUEUE = "codeforge:runs"

async def enqueue(redis: Redis, payload: dict):
    await redis.rpush(QUEUE, json.dumps(payload))

async def dequeue(redis: Redis):
    item = await redis.blpop(QUEUE, timeout=settings.queue_timeout_seconds)
    return json.loads(item[1]) if item else None
