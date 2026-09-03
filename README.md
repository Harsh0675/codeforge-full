# ⚙️ CodeForge

### A multi-language online code runner built around isolated Docker execution

CodeForge is a full-stack developer tool for writing, compiling, and running code from the browser. It combines a **React + Monaco editor**, **FastAPI API**, **Redis job queue**, **Docker-based language runners**, and **PostgreSQL persistence** into one local development environment.

> **Security:** Code execution is inherently high risk. CodeForge is a development/portfolio project, not a claim of production-grade sandbox security. Public deployment should use dedicated runner infrastructure, hardened container isolation, non-root execution, seccomp/AppArmor, read-only filesystems, strict quotas, egress controls, image pinning, and continuous security testing.

---

## 🧩 What it does

| Capability | Implementation |
|---|---|
| Browser IDE | React + Monaco Editor |
| Code execution API | FastAPI + Uvicorn |
| Async jobs | Redis queue |
| Sandboxed execution | Disposable Docker runner containers |
| Persistence | PostgreSQL-ready SQLAlchemy/asyncpg layer |
| Languages | Python, C, C++, Java, JavaScript/Node, Go, Rust, PHP |
| Developer API | OpenAPI / Swagger docs |
| Environment | Docker Compose |

### Supported language runners

- 🐍 Python
- ⚡ C / C++
- ☕ Java
- 🟨 JavaScript / Node.js
- 🐹 Go
- 🦀 Rust
- 🐘 PHP

Kotlin is intentionally not listed as an active runner until a dedicated pinned Kotlin image is added.

---

## 🏗️ Architecture

```text
React + Monaco IDE
        │ HTTP
        ▼
    FastAPI API
        │ enqueue
        ▼
      Redis
        │ job
        ▼
   Runner Worker
        │ isolated execution
        ▼
 Docker Runner Image
        │ result
        ▼
 Redis / PostgreSQL
```

The API accepts a run request, places the work on Redis, and a worker executes it using the appropriate language-specific Docker image. The client can then retrieve the run result through the API.

---

## 🔌 API surface

### Create a run

`POST /api/v1/runs`

```json
{
  "language": "python",
  "source": "print(input())",
  "stdin": "CodeForge"
}
```

Example response:

```json
{
  "id": "uuid",
  "status": "queued"
}
```

### Retrieve a run

`GET /api/v1/runs/{id}`

### Health check

`GET /health`

Interactive API documentation is available from FastAPI at `/docs` when the stack is running.

---

## 🚀 Run locally

### Requirements

- Docker Desktop or Docker Engine
- Docker Compose
- Node.js 20+ only when running the frontend outside Docker

Start the complete stack:

```bash
docker compose up --build
```

Then open:

- **Web IDE:** `http://localhost:5173`
- **API:** `http://localhost:8000`
- **Swagger:** `http://localhost:8000/docs`
- **Health:** `http://localhost:8000/health`

Stop the stack:

```bash
docker compose down
```

To remove the development PostgreSQL volume as well:

```bash
docker compose down -v
```

---

## 📁 Project structure

```text
codeforge-full/
├── backend/             # FastAPI service + worker
├── frontend/            # React + Monaco web IDE
├── runner-images/       # Language-specific Docker images
├── docker-compose.yml   # Complete local orchestration
└── README.md
```

The runner images are deliberately separated by language so compiler/runtime dependencies can be controlled independently.

---

## 🛡️ Security model

The project is designed around the principle that submitted code should **not execute directly inside the API process**.

Current design includes:

- Disposable Docker execution environments
- Disabled networking for runner execution
- CPU, memory, process, file-size and wall-clock controls
- Compile/runtime timeout guards
- Separate language runner images
- Writable temporary workspaces for execution
- Request body and queue quota considerations

### Before public production use

A real internet-facing deployment should additionally address:

- Never exposing the Docker socket to untrusted users
- Dedicated runner hosts separate from the API
- Non-root container users
- Read-only root filesystems with minimal writable tmpfs
- seccomp/AppArmor or equivalent isolation
- Strict authentication and rate limiting
- Abuse detection and queue quotas
- Pinned image digests
- Compiler/runtime patch management
- Network egress controls
- Continuous sandbox escape/security testing

---

## 🧰 Technology stack

**Frontend**
- React 19
- TypeScript
- Vite
- Monaco Editor

**Backend**
- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- asyncpg

**Infrastructure**
- Redis
- PostgreSQL
- Docker
- Docker Compose

The frontend uses React 19, Vite 6, TypeScript, and `@monaco-editor/react`; the backend pins FastAPI, Redis, SQLAlchemy, asyncpg, and Docker SDK dependencies.

---

## 🎯 What this project demonstrates

CodeForge is primarily a systems-oriented portfolio project. It demonstrates more than a browser editor by combining:

- asynchronous job processing
- API design
- database integration
- container orchestration
- language-specific build environments
- resource limiting
- runtime error handling
- frontend/backend separation
- security-aware execution architecture

The most interesting engineering problem is the boundary between **untrusted source code** and the infrastructure executing it.

---

## ⚠️ Project status

CodeForge is suitable for **local development, learning, demonstrations, and portfolio review**. The repository includes several hardening measures, but arbitrary-code execution should never be exposed publicly without an independently reviewed sandbox architecture.

---

## 📜 License

See the repository license for usage terms.

---

## 👨‍💻 Author

**Harsh0675**

Built as a full-stack systems project focused on developer tooling, APIs, containers, and secure execution design.
