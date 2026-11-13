"""Bounded subscription teacher coordinator. The worker owns supported OAuth."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys

import graft as g
import run_graft as r
from prepare_teacher import envelope

HERE = Path(__file__).resolve().parent


def pincheck():
    contract = r.read(HERE / "CALL-CONTRACT.json")
    for name, expected in contract["sha256"].items():
        if r.sha(HERE / name) != expected:
            raise ValueError("Call contract changed: " + name)
    r.validate_registration(HERE / "data")


def bind(data, seed, case, number, prompt_path, transport):
    """Bind exact portable artifact files; runner independently validates them."""
    record = r.read(transport / "record.json")
    events = r.read(transport / "terminal-events.json")
    terminals = [x for x in events if x.get("type") in ("response.completed", "response.incomplete", "response.failed")]
    actual_model = terminals[-1].get("model") if terminals else None
    artifacts = {
        "original_request": str(prompt_path.relative_to(data)),
        "wire": str((transport / "wire.json").relative_to(data)),
        "response_record": str((transport / "record.json").relative_to(data)),
        "terminal_events": str((transport / "terminal-events.json").relative_to(data)),
    }
    # A pre-wire failure is a consumed opportunity and has an empty wire record.
    if not (transport / "wire.json").exists():
        r.write(transport / "wire.json", [])
    binding = {"seed": seed, "case": case, "round": number,
               "packet_sha256": g.fingerprint(r.read(prompt_path)["packet"]),
               "terminal_model": actual_model}
    for name, rel in artifacts.items():
        binding[name + "_sha256"] = r.sha(data / rel)
    package = {"binding": binding, "artifacts": artifacts,
               "transport_status": record.get("status", "error")}
    if record.get("status") == "parsed" and terminals and terminals[-1].get("type") == "response.completed" and terminals[-1].get("status") == "completed" and actual_model == "gpt-6-astra":
        package["candidates"] = record["parsed_batch"]["candidates"]
    elif record.get("status") == "parsed":
        package["transport_status"] = "terminal_identity_error"
    destination = transport / "bound-response.json"
    r.write(destination, package)
    return destination


def run(hermes_root, python):
    data = HERE / "data"
    pincheck()
    ledger_path = data / "teacher-call-ledger.json"
    ledger = r.read(ledger_path) if ledger_path.exists() else []
    for seed in g.CONFIG["seeds"]:
        exp = r.read(data / "instances" / f"seed-{seed}.json")
        for case in g.CONFIG["cases"]:
            parent = r.parent_deployment(g.packet(exp, case))
            previous = None
            for number in (1, 2):
                record_path = data / "teacher" / r.prefix(seed, case) / f"round-{number}" / "round.json"
                if record_path.exists():
                    result = r.validate_teacher_record(data, exp, case, number, parent, previous)
                    if result["exact_target_reached"]:
                        break
                    parent = result["selected_deployment"]
                    previous = result
                    continue
                if number == 1:
                    prompt_path = data / "prepared/requests" / f"seed-{seed}-{case}-round-1.json"
                else:
                    previous = r.validate_teacher_record(data, exp, case, 1,
                        r.parent_deployment(g.packet(exp, case)), None)
                    if previous["exact_target_reached"]:
                        break
                    prompt_path = data / "teacher-requests" / f"seed-{seed}-{case}-round-2.json"
                    r.write(prompt_path, envelope(g.packet(exp, case), previous["selected_deployment"], 2, r.teacher_feedback(previous)))
                transport = data / "teacher-transport" / f"seed-{seed}-{case}-round-{number}"
                call_id = f"{seed}/{case}/{number}"
                previous_calls = [x for x in ledger if x["call_id"] == call_id]
                if not previous_calls:
                    pincheck()
                    if len(ledger) >= 8:
                        raise ValueError("Eight-opportunity limit reached")
                    if transport.exists():
                        raise ValueError("Unledgered output directory exists")
                    ledger.append({"call_id": call_id, "prompt_sha256": r.sha(prompt_path), "state": "started"})
                    r.write(ledger_path, ledger)
                    env = os.environ.copy()
                    env["PYTHONPATH"] = str(hermes_root)
                    # Explicit Codex provider never needs Platform keys. Do not forward them.
                    for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_ORG_ID", "OPENAI_PROJECT_ID"):
                        env.pop(name, None)
                    portable = lambda text: (text.decode("utf-8", "replace") if isinstance(text, bytes) else (text or "")).replace(str(HERE), "[EXPERIMENT]").replace(str(hermes_root), "[HERMES]").replace(str(Path.home()), "[HOME]")
                    try:
                        completed = subprocess.run([str(python), str(HERE / "oauth_teacher.py"),
                            "--prompt-fixture", str(prompt_path), "--outdir", str(transport)],
                            cwd=HERE, env=env, capture_output=True, text=True, timeout=660)
                    except subprocess.TimeoutExpired as exc:
                        r.write(transport / "process.json", {"state": "timeout", "timeout_seconds": 660,
                            "stdout": portable(exc.stdout), "stderr": portable(exc.stderr),
                            "worker_record_present": (transport / "record.json").exists(),
                            "response_fabricated": False, "retry_allowed": False})
                        ledger[-1]["state"] = "timeout"
                        r.write(ledger_path, ledger)
                        raise ValueError("Worker duration exceeded; manual audit required, no retry") from None
                    r.write(transport / "process.json", {"returncode": completed.returncode,
                        "stdout": portable(completed.stdout), "stderr": portable(completed.stderr)})
                    ledger[-1]["state"] = "returned"
                    ledger[-1]["returncode"] = completed.returncode
                    r.write(ledger_path, ledger)
                else:
                    if len(previous_calls) != 1 or previous_calls[0]["prompt_sha256"] != r.sha(prompt_path):
                        raise ValueError("Call identity or prompt mismatch")
                if not (transport / "record.json").exists():
                    raise ValueError("Worker did not retain a response; manual audit required, no retry")
                package = bind(data, seed, case, number, prompt_path, transport)
                result = r.teacher_round(data, seed, case, number, package)
                print(json.dumps({"seed": seed, "case": case, "round": number,
                                  "adopted": result["adopted"], "exact": result["exact_target_reached"]}), flush=True)
                if result["exact_target_reached"]:
                    break
                parent = result["selected_deployment"]
                previous = result
    r.finish_teacher(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hermes-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    run(args.hermes_root.resolve(), args.python.resolve())
