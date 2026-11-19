#!/usr/bin/env python3
"""
End-to-end HTTP demo against a running CarePath server.
Usage:
  terminal 1: make run
  terminal 2: python scripts/http_demo.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
API_KEY = "carepath-clinician-dev-key"
PHONE = "http-demo-user"


def post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def get(path: str, api_key: str | None = None) -> dict:
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    req = urllib.request.Request(BASE + path, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def step(label: str, text: str) -> None:
    print(f"\n>>> You: {text}")
    r = post("/admin/demo/message", {"from_number": PHONE, "text": text})
    print(f"CarePath: {r['reply'][:400]}{'…' if len(r.get('reply',''))>400 else ''}")
    s = r.get("session") or {}
    print(f"   [status={s.get('status')} pathway={s.get('pathway')} answers={s.get('answers_count')}]")
    if r.get("decision"):
        d = r["decision"]
        print(f"   [decision triage={d.get('triage')} red_flag={d.get('red_flag')}]")


def main() -> None:
    try:
        health = get("/health")
        print("Health:", health)
    except Exception as exc:
        print("Server not reachable at", BASE)
        print("Start it with: make run")
        print(exc)
        sys.exit(1)

    # Reset
    post("/admin/demo/reset", {})  # body ignored; query param style
    # Actually reset uses query - call properly
    req = urllib.request.Request(BASE + f"/admin/demo/reset?from_number={PHONE}", method="POST")
    urllib.request.urlopen(req, timeout=10)

    print("\n=== Fertility pathway demo ===")
    step("start", "hello")
    step("consent", "yes")
    step("pathway", "2")          # fertility
    step("age", "3")              # 35-44
    step("trying", "1")           # yes
    step("duration", "3")         # >12m
    step("prior test", "2")       # abnormal

    print("\n=== Clinician view ===")
    try:
        metrics = get("/clinician/metrics/summary", api_key=API_KEY)
        print("Metrics:", json.dumps(metrics, indent=2))
        assessments = get("/clinician/assessments?limit=5", api_key=API_KEY)
        print(f"Assessments listed: {assessments.get('count')}")
        if assessments.get("assessments"):
            aid = assessments["assessments"][0]["assessment_id"]
            detail = get(f"/clinician/assessments/{aid}", api_key=API_KEY)
            print("Latest assessment triage:", (detail.get("decision") or {}).get("triage"))
    except urllib.error.HTTPError as e:
        print("Clinician API error:", e.code, e.read().decode()[:200])

    print("\nDemo complete.")


if __name__ == "__main__":
    main()
