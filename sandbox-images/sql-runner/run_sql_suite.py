import argparse, json, subprocess, os, sys, textwrap, tempfile

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", choices=["public","hidden"], required=True)
    args = ap.parse_args()

    # We expect these files in /work (mounted job dir):
    # schema.sql, seed.sql, solution.sql, public_tests.sql, hidden_tests.sql
    suite_file = "public_tests.sql" if args.suite == "public" else "hidden_tests.sql"

    db_path = "test.db"
    # Build DB
    for sqlfile in ["schema.sql", "seed.sql"]:
        if os.path.exists(sqlfile):
            code, out, err = run(["sqlite3", db_path, f".read {sqlfile}"])
            if code != 0:
                print(err)
                print(json.dumps({"passed": False, "feedback":[{"message": f"Failed to apply {sqlfile}"}]}))
                sys.exit(1)

    # Apply solution
    if not os.path.exists("solution.sql"):
        print(json.dumps({"passed": False, "feedback":[{"message":"Missing solution.sql"}]}))
        sys.exit(1)

    code, out, err = run(["sqlite3", db_path, ".read solution.sql"])
    if code != 0:
        # For public suite, show parse error; for hidden, keep generic
        msg = "SQL error in your solution." if args.suite == "hidden" else (err.strip() or "SQL error in your solution.")
        print(msg)
        print(json.dumps({"passed": False, "feedback":[{"message": msg}]}))
        sys.exit(1)

    if not os.path.exists(suite_file):
        print(json.dumps({"passed": False, "feedback":[{"message": f"Missing {suite_file}"}]}))
        sys.exit(1)

    # Run tests: tests should output lines like:
    # PASS: ...
    # FAIL: ...
    code, out, err = run(["sqlite3", "-batch", "-noheader", db_path, f".read {suite_file}"])
    raw = (out or "") + (err or "")
    lines = [l.strip() for l in raw.splitlines() if l.strip()]

    fails = [l for l in lines if l.upper().startswith("FAIL")]
    passed = (len(fails) == 0) and (code == 0)

    if args.suite == "hidden":
        # Do not reveal details
        if passed:
            sys.exit(0)
        print("Hidden tests failed.")
        sys.exit(1)

    feedback = []
    for l in lines:
        if l.upper().startswith("FAIL"):
            feedback.append({"message": l})
    result = {"passed": passed, "exit_code": code, "feedback": feedback}
    print(json.dumps(result))
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
