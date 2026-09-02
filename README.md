# CodeForge — Multi-Language Online Compiler & Code Runner

A production-oriented starter platform for running untrusted source code through isolated Docker containers.

## Features

- Monaco-based React/TypeScript editor
- Python, C, C++, Java, JavaScript, Go, Rust, PHP, Kotlin
- FastAPI backend
- Redis-backed job queue
- Docker execution workers
- CPU, memory, process and wall-clock limits
- stdin/stdout/stderr handling
- Compilation and runtime error reporting
- PostgreSQL-ready persistence layer
- Docker Compose development environment
- Health checks and API documentation

> Security note: arbitrary code execution is dangerous. This project deliberately runs submitted programs in disposable containers with networking disabled and resource limits. For public production deployment, use a dedicated runner host, hardened container runtime, seccomp/AppArmor, read-only filesystems, non-root users, egress controls and continuous security testing.

## Quick start

Requirements:
- Docker Desktop / Docker Engine + Compose
- Node 20+ (only if running frontend outside Docker)

```bash
docker compose up --build
```

Open:
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

## API

`POST /api/v1/runs`

```json
{
  "language": "python",
  "source": "print(input())",
  "stdin": "CodeForge"
}
```

Response:

```json
{
  "id": "uuid",
  "status": "queued"
}
```

Poll `GET /api/v1/runs/{id}`.

## Architecture

Browser -> FastAPI -> Redis -> Runner Worker -> Docker sandbox -> result -> Redis/Postgres -> Browser

## Production hardening checklist

- Never expose the Docker socket to the public API.
- Put workers on separate machines from the API.
- Run containers as a dedicated unprivileged UID.
- Use a minimal read-only root filesystem with a small writable tmpfs.
- Disable networking.
- Set CPU, memory, PID and file-size limits.
- Enforce request body limits and queue quotas.
- Add authentication, rate limiting and abuse detection.
- Use pinned image digests instead of floating tags.
- Keep compiler images patched.


## Runner fixes in this build
- Writable `/workspace` and `/tmp` tmpfs mounts fix Docker archive/file-copy failures.
- Source and stdin are copied before execution.
- Compiled native binaries are written to executable `/tmp` tmpfs.
- Compile and runtime commands have hard timeout guards.
- TypeScript uses a preinstalled `tsc` instead of downloading packages at runtime.
- Kotlin is temporarily disabled until a dedicated pinned Kotlin runner image is added.
