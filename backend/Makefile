.PHONY: install run test eval report telegram

install:
	pip install -r requirements.txt

run:
	CAREPATH_USE_SQLITE=1 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

eval:
	python scripts/run_synthetic_eval.py

report:
	python scripts/generate_eval_report.py

telegram:
	python scripts/run_telegram_poll.py
