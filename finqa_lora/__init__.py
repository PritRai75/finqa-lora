"""FinQA LoRA fine-tuning and label-consistency audit."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"
SPLITS = ("train", "dev", "test")
