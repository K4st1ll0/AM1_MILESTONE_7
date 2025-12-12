# SOURCES/utils.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCES_DIR = PROJECT_ROOT / "SOURCES"
DATA_DIR    = PROJECT_ROOT / "DATA"

INPUT_DIR  = DATA_DIR / "input"
GMAT_DIR   = DATA_DIR / "gmat"
OUTPUT_DIR = DATA_DIR / "output"
PLOTS_DIR  = DATA_DIR / "plots"


def ensure_dirs():
    for d in [INPUT_DIR, GMAT_DIR, OUTPUT_DIR, PLOTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
