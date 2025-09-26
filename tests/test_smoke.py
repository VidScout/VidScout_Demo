
import importlib
from pathlib import Path

MODULES = [
    "app",
    "clip_matcher_faiss",
    "generate_clip_db_faiss",
    "process_youtube_batch",
]

def test_imports():
    # Проверяем, что ключевые модули импортируются без побочных запусков
    for m in MODULES:
        importlib.import_module(m)

def test_readme_exists():
    # README.md присутствует в корне
    root = Path(__file__).resolve().parents[1]
    assert (root / "README.md").exists()
