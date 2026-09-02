import io
import shlex
import tarfile
import time
import uuid

import docker
from docker.errors import APIError, DockerException

from .registry import LANGUAGES

EXECUTION_TIMEOUT = 5
COMPILE_TIMEOUT = 60
OUTPUT_LIMIT = 64 * 1024
WORKSPACE_LIMIT = "64m"


class SandboxRunner:
    """Execute submitted code in a short-lived Docker container.

    This configuration is intended for local/controlled deployments.
    A public arbitrary-code execution service needs stronger isolation
    (dedicated worker hosts/VMs, pinned image digests, seccomp/AppArmor,
    authentication/rate limiting, quotas, and abuse controls).
    """

    def __init__(self):
        self.client = docker.from_env()

    @staticmethod
    def _tar(files: dict[str, str]) -> bytes:
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tar:
            for filename, content in files.items():
                if not filename or filename.startswith("/") or ".." in filename.split("/"):
                    raise ValueError("invalid workspace filename")
                data = content.encode("utf-8")
                info = tarfile.TarInfo(filename)
                info.size = len(data)
                info.mode = 0o644
                info.uid = 10001
                info.gid = 10001
                info.uname = "runner"
                info.gname = "runner"
                tar.addfile(info, io.BytesIO(data))
        return buf.getvalue()

    @staticmethod
    def _decode(data) -> bytes:
        if data is None:
            return b""
        if isinstance(data, tuple):
            return (data[0] or b"") + (data[1] or b"")
        return data or b""

    def _exec(self, container, command, timeout, stdin_file=False):
        """Run one command with a hard timeout enforced inside the container."""
        command_text = shlex.join(command)
        if stdin_file:
            command_text += " < /workspace/stdin.txt"

        # All runner images are Debian/Ubuntu based and provide coreutils
        # `timeout`. Exit 124 is the timeout status; 137 can occur when the
        # process is killed by SIGKILL after the timeout.
        shell = f"timeout -s KILL {int(timeout)}s {command_text}"
        result = container.exec_run(
            ["sh", "-lc", shell],
            workdir="/workspace",
            demux=True,
            environment={
                "HOME": "/tmp",
                "TMPDIR": "/tmp",
                "GOCACHE": "/workspace/.go-cache",
                "GOMODCACHE": "/workspace/.go-mod-cache",
                "CARGO_HOME": "/workspace/.cargo",
                "RUSTUP_HOME": "/workspace/.rustup",
            },
        )

        if isinstance(result.output, tuple):
            out, err = result.output
        else:
            out, err = result.output, b""

        out = (out or b"")[:OUTPUT_LIMIT]
        err = (err or b"")[:OUTPUT_LIMIT]

        if result.exit_code in (124, 137):
            return "timeout", out, err, result.exit_code
        return None, out, err, result.exit_code

    def _result(self, status, out, err, code, started):
        return {
            "status": status,
            "stdout": (out or b"").decode("utf-8", errors="replace"),
            "stderr": (err or b"").decode("utf-8", errors="replace"),
            "exit_code": code,
            "duration_ms": int((time.perf_counter() - started) * 1000),
        }

    def execute(self, language: str, source: str, stdin: str):
        if language not in LANGUAGES:
            return {
                "status": "runner_error",
                "stdout": "",
                "stderr": f"Unsupported language: {language}",
                "exit_code": -1,
                "duration_ms": 0,
            }

        cfg = LANGUAGES[language]
        container = None
        volume = None
        started = time.perf_counter()
        name = f"codeforge-{uuid.uuid4().hex}"

        try:
            volume = self.client.volumes.create(name=f"{name}-workspace", driver="local")
            container = self.client.containers.create(
                image=cfg["image"],
                command=["sleep", "infinity"],
                name=name,
                detach=True,
                # Network is completely disabled for submitted programs.
                network_disabled=True,
                mem_limit="256m",
                nano_cpus=1_000_000_000,
                pids_limit=64,
                # Docker's put_archive API refuses writes when the container
                # rootfs is read-only, even when /workspace is a tmpfs mount.
                # Keep the root writable for the local runner; /workspace and
                # /tmp are isolated tmpfs filesystems and the container is
                # destroyed after every run.
                read_only=False,
                # A dedicated Docker volume gives /workspace a real writable
                # filesystem. We do not rely on tmpfs + put_archive, which can
                # behave differently across Docker Desktop/Engine versions.
                volumes={volume.name: {"bind": "/workspace", "mode": "rw"}},
                tmpfs={
                    "/tmp": "rw,size=64m,nosuid,nodev",
                },
                working_dir="/workspace",
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],
                init=True,
            )
            container.start()

            # Put the archive at the container root using paths that include
            # workspace/. This avoids Docker Desktop edge cases where archive
            # extraction directly into a tmpfs mount reports success but does
            # not create the file. /workspace is backed by the dedicated volume.
            archive = self._tar({
                f"workspace/{cfg['file']}": source,
                "workspace/stdin.txt": stdin,
            })
            ok = container.put_archive("/", archive)
            if ok is False:
                raise RuntimeError("Docker failed to copy source into /workspace")

            # Fail clearly if the copy did not produce the expected source file.
            check = container.exec_run(
                ["sh", "-lc", f"test -f {shlex.quote('/workspace/' + cfg['file'])}"],
                workdir="/workspace",
            )
            if check.exit_code != 0:
                raise RuntimeError(
                    f"Source file was not created: /workspace/{cfg['file']}"
                )

            if cfg["compile"]:
                status, out, err, code = self._exec(
                    container, cfg["compile"], COMPILE_TIMEOUT
                )
                if status == "timeout":
                    return self._result("timeout", out, err, code, started)
                if code != 0:
                    return self._result("compile_error", out, err, code, started)

            status, out, err, code = self._exec(
                container, cfg["run"], EXECUTION_TIMEOUT, stdin_file=True
            )
            if status == "timeout":
                return self._result("timeout", out, err, code, started)

            return self._result(
                "finished" if code == 0 else "runtime_error",
                out,
                err,
                code,
                started,
            )

        except (DockerException, APIError, OSError, ValueError, RuntimeError) as exc:
            return self._result(
                "runner_error", b"", str(exc).encode("utf-8"), -1, started
            )
        except Exception as exc:
            return self._result(
                "runner_error", b"", str(exc).encode("utf-8"), -1, started
            )
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            if volume is not None:
                try:
                    volume.remove(force=True)
                except Exception:
                    pass
