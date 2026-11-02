"""Load the pinned FinQA splits."""
import json

from finqa_lora import DATA_RAW, SPLITS


def load_split(split):
    if split not in SPLITS:
        raise ValueError(f"unknown split {split!r}, expected one of {SPLITS}")
    path = DATA_RAW / f"{split}.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing. Run: python -m finqa_lora.fetch")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
