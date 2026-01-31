import os, time, shutil, tempfile, json
import docker
from sanitize import sanitize_logs

PY_IMAGE = os.environ.get("EDGELAB_PY_IMAGE", "edgelab-sandbox-python:0.1")
JAVA_IMAGE = os.environ.get("EDGELAB_JAVA_IMAGE", "edgelab-sandbox-java:0.1")
SQL_IMAGE = os.environ.get("EDGELAB_SQL_IMAGE", "edgelab-sandbox-sql:0.1")

def _run_container(image: str, workdir: str, cmd: list[str], time_limit_ms: int, memory_limit_mb: int):
    client = docker.from_env()
    start = time.time()

    # Docker SDK doesn't have perfect "hard timeout" – we enforce it by polling and killing.
    container = client.containers.run(
        image=image,
        command=cmd,
        network_disabled=True,
        mem_limit=f"{memory_limit_mb}m",
        cpu_period=100000,
        cpu_quota=100000,  # ~1 CPU
        pids_limit=128,
        security_opt=["no-new-privileges:true"],
        cap_drop=["ALL"],
        working_dir="/work",
        volumes={workdir: {"bind": "/work", "mode": "rw"}},
        detach=True,
        tty=False,
        stdin_open=False,
        remove=False,
    )

    timed_out = False
    try:
        while True:
            container.reload()
            if container.status in ("exited", "dead"):
                break
            elapsed_ms = int((time.time() - start) * 1000)
            if elapsed_ms > time_limit_ms:
                timed_out = True
                container.kill()
                break
            time.sleep(0.05)

        exit_code = container.attrs.get("State", {}).get("ExitCode", 1)
        logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="ignore")
    finally:
        try:
            container.remove(force=True)
        except Exception:
            pass

    runtime_ms = int((time.time() - start) * 1000)
    if timed_out:
        return 124, f"TIMEOUT after {time_limit_ms}ms\n", runtime_ms
    return exit_code, logs, runtime_ms

def evaluate_submission(language: str, assignment_folder: str, entrypoint: str, files: list[tuple[str,str]],
                        time_limit_ms: int, memory_limit_mb: int, max_output_kb: int, scoring: dict):
    # Create temp working directory
    workdir = tempfile.mkdtemp(prefix="edgelab_job_")
    try:
        # Write user files
        for path, content in files:
            out_path = os.path.join(workdir, path)
            os.makedirs(os.path.dirname(out_path) or workdir, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)

        # Copy assignment test/support files into workdir (NOT templates)
        for name in os.listdir(assignment_folder):
            if name.endswith(".template") or name in ("solution_template.py",):
                continue
            src = os.path.join(assignment_folder, name)
            if os.path.isfile(src):
                shutil.copyfile(src, os.path.join(workdir, name))

        # Decide commands per language
        if language == "python":
            image = PY_IMAGE
            public_cmd = ["python", "-m", "pytest", "-q", "public_tests.py"]
            hidden_cmd = ["python", "-m", "pytest", "-q", "hidden_tests.py"]
        elif language == "java":
            image = JAVA_IMAGE
            public_cmd = ["bash", "-lc", "javac Main.java PublicTests.java && java PublicTests"]
            hidden_cmd = ["bash", "-lc", "javac Main.java HiddenTests.java && java HiddenTests"]
        elif language == "sql":
            image = SQL_IMAGE
            public_cmd = ["python", "run_sql_suite.py", "--suite", "public"]
            hidden_cmd = ["python", "run_sql_suite.py", "--suite", "hidden"]
        else:
            raise ValueError(f"Unsupported language: {language}")

        # Run public
        pub_exit, pub_logs, pub_rt = _run_container(
            image=image, workdir=workdir, cmd=public_cmd,
            time_limit_ms=time_limit_ms, memory_limit_mb=memory_limit_mb
        )

        public = _interpret_public(language, pub_exit, pub_logs)

        # Run hidden
        hid_exit, hid_logs, hid_rt = _run_container(
            image=image, workdir=workdir, cmd=hidden_cmd,
            time_limit_ms=time_limit_ms, memory_limit_mb=memory_limit_mb
        )
        hidden = _interpret_hidden(language, hid_exit)

        # Score
        score = _score(public, hidden, scoring)

        # Sanitize logs: include ONLY public logs + generic hidden info
        combined_logs = "=== Public run ===\n" + (pub_logs or "") + "\n"
        combined_logs += "=== Hidden run ===\n"
        combined_logs += ("Hidden tests passed.\n" if hidden.get("passed") else "Hidden tests failed.\n")

        sanitized = sanitize_logs(combined_logs, max_kb=max_output_kb)

        runtime_ms = pub_rt + hid_rt
        return score, public, hidden, sanitized, runtime_ms

    finally:
        shutil.rmtree(workdir, ignore_errors=True)

def _interpret_public(language: str, exit_code: int, logs: str):
    if language in ("python", "java"):
        passed = (exit_code == 0)
        feedback = []
        if not passed:
            # For v0.1 we keep a short message, not full stack trace parsing.
            # We still return logs (sanitized later).
            feedback.append({"message": "Some public tests failed. See logs."})
        return {
            "passed": passed,
            "exit_code": exit_code,
            "feedback": feedback,
        }
    if language == "sql":
        # SQL runner prints JSON on success/failure
        try:
            data = json.loads(logs.strip().splitlines()[-1])
            return data
        except Exception:
            return {
                "passed": False,
                "exit_code": exit_code,
                "feedback": [{"message": "Could not parse SQL test output. See logs."}]
            }
    return {"passed": False, "exit_code": exit_code, "feedback": [{"message":"Unknown language"}]}

def _interpret_hidden(language: str, exit_code: int):
    return {"passed": exit_code == 0, "note": ("All hidden tests passed." if exit_code == 0 else "Some hidden tests failed.")}

def _score(public: dict, hidden: dict, scoring: dict) -> int:
    pub_w = int(scoring.get("public", 50))
    hid_w = int(scoring.get("hidden", 50))
    score = 0
    if public.get("passed"):
        score += pub_w
    if hidden.get("passed"):
        score += hid_w
    return score
