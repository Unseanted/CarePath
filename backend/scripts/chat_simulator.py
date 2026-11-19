#!/usr/bin/env python3
"""
Interactive CLI simulator for CarePath.
Walks through the full patient journey without WhatsApp or a running server.

Usage:
  python scripts/chat_simulator.py
  python scripts/chat_simulator.py --script fertility_happy_path
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.conversation import (
    process_message,
    reset_session,
    _get_or_create_session,
)

PHONE = "cli-demo-user"


async def interactive() -> None:
    reset_session(PHONE)
    session = _get_or_create_session(PHONE)
    print("=" * 60)
    print("CarePath CLI Simulator")
    print("Type your messages as if you were on WhatsApp.")
    print("Commands:  stop | restart | quit")
    print("=" * 60)
    print()

    # Kick off with a greeting
    reply = await process_message(session, "hello")
    print(f"CarePath: {reply}\n")

    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not user:
            continue
        if user.lower() in ("quit", "q"):
            print("Bye.")
            break
        reply = await process_message(session, user)
        print(f"\nCarePath: {reply}\n")


# Pre-defined demo scripts for quick verification
SCRIPTS = {
    "education_path": [
        "hello",
        "yes",
        "1",           # general
        "2",           # age 25-34
        "2",           # not trying
        "4",           # none of the conditions
        "2",           # no smoking
    ],
    "urgent_path": [
        "hello",
        "yes",
        "3",           # symptoms
        "2",           # age
        "3",           # prefer not
        "1",           # severe pain = yes  → short-circuits to urgent
    ],
    "fertility_path": [
        "hello",
        "yes",
        "2",           # fertility
        "3",           # age 35-44
        "1",           # trying
        "3",           # >12 months
        "2",           # abnormal prior test
    ],
}


async def run_script(name: str) -> None:
    if name not in SCRIPTS:
        print(f"Unknown script: {name}")
        print("Available:", ", ".join(SCRIPTS))
        sys.exit(1)

    reset_session(PHONE)
    session = _get_or_create_session(PHONE)
    print(f"Running script: {name}\n")

    for msg in SCRIPTS[name]:
        print(f"You: {msg}")
        reply = await process_message(session, msg)
        print(f"CarePath: {reply}\n")
        print("-" * 40)

    a = session.get("assessment")
    d = session.get("last_decision")
    if d:
        print("\n=== FINAL DECISION ===")
        print(f"Triage   : {d.triage.value}")
        print(f"Red flag : {d.red_flag}")
        print(f"Factors  : {d.explanation_factors}")
        print(f"Summary  : {d.next_step_summary}")
        print(f"Rules    : {d.rules_version}")
    elif a:
        print(f"\nStatus: {a.status.value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="CarePath CLI chat simulator")
    parser.add_argument(
        "--script",
        choices=list(SCRIPTS.keys()),
        help="Run a pre-defined demo script instead of interactive mode",
    )
    args = parser.parse_args()
    if args.script:
        asyncio.run(run_script(args.script))
    else:
        asyncio.run(interactive())


if __name__ == "__main__":
    main()
