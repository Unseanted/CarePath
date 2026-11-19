# CarePath backend

Runnable FastAPI prototype for CarePath.

For the full product overview, architecture, challenge alignment, and documentation index, see the **repository root** [`README.md`](../README.md).

## Quick commands

```bash
pip install -r requirements.txt
cp .env.example .env
export CAREPATH_USE_SQLITE=1
make run          # uvicorn on :8000
make test         # pytest
make eval         # synthetic cases
make report       # EVALUATION_REPORT.md
make urgent       # CLI urgent path demo
```

```bash
python scripts/chat_simulator.py
python scripts/http_demo.py   # requires server running
```
