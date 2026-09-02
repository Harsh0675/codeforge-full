import asyncio, json
from redis.asyncio import Redis
from .config import settings
from .queue import dequeue
from .runner import SandboxRunner

async def main():
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    runner = SandboxRunner()
    print("CodeForge worker online")
    while True:
        job = await dequeue(redis)
        if not job:
            continue
        run_id = job["id"]
        try:
            await redis.hset(f"run:{run_id}", mapping={"status": "running"})
            result = await asyncio.to_thread(
                runner.execute, job["language"], job["source"], job["stdin"]
            )
            await redis.hset(f"run:{run_id}", mapping=result)
        except Exception as exc:
            await redis.hset(
                f"run:{run_id}",
                mapping={
                    "status": "runner_error",
                    "stdout": "",
                    "stderr": f"Worker error: {exc}",
                    "exit_code": -1,
                },
            )

if __name__ == "__main__":
    asyncio.run(main())
