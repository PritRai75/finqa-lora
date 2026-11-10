"""Prompt building and program extraction (no torch needed)."""
import pytest

from finqa_lora.data import load_split
from finqa_lora.prompt import FEW_SHOT_IDS, SYSTEM, extract_program, few_shot_examples, messages, target
from finqa_lora.scoring import exe_correct
from finqa_lora.screen import screen_item

TRAIN = load_split("train")
DEV = load_split("dev")


def test_messages_shape():
    ex = DEV[0]
    m = messages(ex)
    assert [x["role"] for x in m] == ["system", "user"]
    assert m[0]["content"] == SYSTEM
    assert ex["qa"]["question"] in m[1]["content"]
    for _, fact in ex["qa"]["model_input"]:
        assert fact in m[1]["content"]


def test_few_shot_examples_are_clean_train_items():
    shots = few_shot_examples(TRAIN)
    assert [s["id"] for s in shots] == list(FEW_SHOT_IDS)
    assert all(screen_item(s) == "agree" for s in shots)
    dev_test_ids = {e["id"] for e in DEV} | {e["id"] for e in load_split("test")}
    assert not dev_test_ids & set(FEW_SHOT_IDS)
    m = messages(DEV[0], shots)
    assert [x["role"] for x in m] == ["system"] + ["user", "assistant"] * 4 + ["user"]


@pytest.mark.parametrize("reply, program", [
    ("subtract(5829, 5735), divide(#0, 5735)", "subtract(5829, 5735), divide(#0, 5735)"),
    ("Program: subtract(5829 ,5735), divide(#0,5735) because", "subtract(5829, 5735), divide(#0, 5735)"),
    ("```\ntable_average( interest  expense , none )\n```", "table_average(interest expense, none)"),
    ("Let me think.\nadd(1, 2)\nmultiply(#0, 3)", "add(1, 2)"),
    ("no idea", ""),
    ("", ""),
])
def test_extract_program(reply, program):
    assert extract_program(reply) == program


@pytest.mark.parametrize("split", ["dev", "test"])
def test_extract_leaves_every_gold_program_scoring_correct(split):
    data = load_split(split)
    wrong = [ex["id"] for ex in data if not exe_correct(extract_program(target(ex)), ex)]
    assert wrong == []


def test_prompt_fingerprint_is_pinned():
    # Changing SYSTEM, FEW_SHOT_IDS or the message layout changes this. Bump PROMPT_VERSION and
    # update the pinned value in the same commit; results from different versions are not comparable.
    from finqa_lora.prompt import PROMPT_VERSION, prompt_fingerprint
    assert (PROMPT_VERSION, prompt_fingerprint()) == (1, "4139bfc3519c")
