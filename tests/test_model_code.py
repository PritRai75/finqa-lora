"""Inference and LoRA training code on a tiny random-weight model (CPU). Skipped without torch."""
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("trl")

from finqa_lora import tiny  # noqa: E402
from finqa_lora.infer import load_tokenizer, run  # noqa: E402
from finqa_lora.train import RunConfig, arm_ids, chat_ids, train  # noqa: E402


@pytest.fixture(scope="module")
def tiny_model(tmp_path_factory):
    return str(tiny.build(tmp_path_factory.mktemp("tiny") / "qwen2"))


def test_arms_have_equal_size_and_cleaned_has_no_flags():
    from finqa_lora.train import screen_status
    status = screen_status()
    cleaned, rand = arm_ids("cleaned"), arm_ids("random")
    assert len(cleaned) == len(rand) == 6251 - 431
    assert not any(status[i] == "disagree" for i in cleaned)
    assert sum(status[i] == "disagree" for i in rand) > 0
    assert arm_ids("random") == rand  # fixed seed


def test_generation_and_scoring_run(tiny_model):
    rows, summary = run(tiny_model, "dev", shots=4, limit=5, batch_size=2)
    assert len(rows) == 5 and summary["items"] == 5
    assert set(rows[0]) == {"id", "reply", "program", "executes", "value", "exe_correct", "prog_correct"}


def test_training_matches_inference_prompt_and_masks_prompt(tiny_model, tmp_path):
    cfg = RunConfig(model=tiny_model, out=str(tmp_path / "run"), subset=8, batch_size=4, grad_accum=1,
                    epochs=1, save=True)
    metrics, trainer = train(cfg)
    assert metrics["items"] == 8 and metrics["loss_is_finite"]
    assert (tmp_path / "run" / "final" / "adapter_config.json").exists()
    tok = load_tokenizer(tiny_model)
    for row in trainer.train_dataset:
        prompt_ids = chat_ids(tok, row["prompt"], add_generation_prompt=True)
        first_label = next(i for i, t in enumerate(row["labels"]) if t != -100)
        assert row["input_ids"][:len(prompt_ids)] == prompt_ids
        assert first_label == len(prompt_ids)
        label_text = tok.decode([t for t in row["labels"] if t != -100])
        assert label_text.startswith(row["completion"][0]["content"])


def test_adapter_loads_for_inference(tiny_model, tmp_path):
    cfg = RunConfig(model=tiny_model, out=str(tmp_path / "run"), subset=4, batch_size=2, grad_accum=1,
                    epochs=1, save=True)
    train(cfg)
    rows, _ = run(tiny_model, "dev", adapter=str(tmp_path / "run" / "final"), limit=2, batch_size=2)
    assert len(rows) == 2


def test_long_examples_are_dropped_not_truncated(tiny_model, tmp_path):
    from finqa_lora.train import build_dataset
    tok = load_tokenizer(tiny_model)
    ids = arm_ids("cleaned")[:40]
    full, _ = build_dataset(ids, tok, 4096)
    lengths = sorted(len(chat_ids(tok, r["prompt"] + r["completion"])) for r in full)
    cut = lengths[len(lengths) // 2]
    kept, dropped = build_dataset(ids, tok, cut)
    assert len(kept) + len(dropped) == 40 and 0 < len(dropped) < 40
    assert all(len(chat_ids(tok, r["prompt"] + r["completion"])) <= cut for r in kept)
