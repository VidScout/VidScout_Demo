.PHONY: setup test run index

setup:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

test:
	. .venv/bin/activate && pytest -q

run:
	. .venv/bin/activate && python app.py

index:
	. .venv/bin/activate && python generate_clip_db_faiss.py
