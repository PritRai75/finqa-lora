"""The Hub model card (hub/model_card.md) is the committed results: every number, hash and revision is
read back and compared with results/, its prompt code builds exactly the training prompt, and its example
is the adapter's own test reply. Also tests finqa_lora.hub's checks and its upload flow against a fake Hub."""
import csv
import hashlib
import json
import re
import sys
import types
from pathlib import Path

import pytest

from finqa_lora import REPO_ROOT, hub
from finqa_lora.data import load_split
from finqa_lora.prompt import messages, prompt_fingerprint

CARD = (REPO_ROOT / "hub" / "model_card.md").read_text(encoding="utf-8")
README_TEXT = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
FLAT = " ".join(CARD.split())   # line breaks in prose do not matter
EVAL = json.loads((REPO_ROOT / "results/test/run1/evaluation.json").read_text(encoding="utf-8"))
ACC = {v: EVAL["views"][v]["accuracy"] for v in ("official", "consistent", "corrected")}
NAME = "adapter:cleaned:3"


def load(path):
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def cell(a):
    lo, hi = (f"{100 * a[k]:.1f}" for k in ("wilson_low", "wilson_high"))
    return f"{a['correct']} = {100 * a['accuracy']:.1f}% ({lo}–{hi}%)"


def pt(x):
    return f"{100 * x:+.2f}".replace("-", "−")


def test_front_matter():
    head = CARD.split("---\n")[1]
    for line in ("base_model: Qwen/Qwen2.5-1.5B-Instruct", "library_name: peft", "license: apache-2.0"):
        assert line in head.splitlines()
    assert hub.REPO_ID == "PritRai75/qwen2.5-1.5b-finqa-lora" and CARD.count(hub.REPO_ID) == 2


def test_this_adapter_on_test():
    assert (hub.ARM, hub.SEED, hub.MAIN_RUN) == ("cleaned", 3, "run1")   # decision 46
    for view, items in (("official", "1,147"), ("consistent", "1,046"), ("corrected", "1,139")):
        assert f"| {view} | {items} | {cell(ACC[view][NAME])} |" in CARD
    assert f"**{ACC['official'][NAME]['correct']} right = 65.4% (95% interval 62.6–68.1%)**" in CARD
    t = load("results/test/run1/cleaned/seed3/result.json")["test"]
    assert f"executes on {t['executes']:,} of {t['items']:,} items" in FLAT
    assert f"the exact gold program on {t['prog_correct']}" in FLAT


def test_comparison_rows_and_range():
    for label, name in (("`Qwen/Qwen2.5-1.5B-Instruct`, 0-shot", "base:qwen2.5-1.5b:0"),
                        ("`Qwen/Qwen2.5-1.5B-Instruct`, 4-shot", "base:qwen2.5-1.5b:4"),
                        ("`Qwen/Qwen3-4B-Instruct-2507`, 4-shot", "base:qwen3-4b:4")):
        a = ACC["official"][name]
        assert f"| {label} | {a['correct']} = {100 * a['accuracy']:.1f}% |" in CARD
    runs = [ACC["official"][f"adapter:{arm}:{s}"]["accuracy"] for arm in ("cleaned", "random") for s in range(1, 6)]
    assert f"| {100 * min(runs):.1f}–{100 * max(runs):.1f}% |" in CARD
    q = EVAL["views"]["official"]["finetuned_vs_base"]["base:qwen3-4b:4"]["per_adapter"][NAME]
    assert f"right on {q['a_only']} items where Qwen3-4B is wrong and wrong on {q['b_only']}" in FLAT
    assert f"p = {q['p']:.1e}" in FLAT


def test_why_this_run():
    dev = sorted(load(f"results/main/{r}/{'cleaned'}/seed{s}/result.json")["dev"]["exe_correct"]
                 for r, seeds in (("run1", (1, 2, 3)), ("run2", (4, 5))) for s in seeds)
    mine = load("results/main/run1/cleaned/seed3/result.json")["dev"]["exe_correct"]
    assert mine == dev[2] == 585   # the median of the arm
    assert f"seed 3, {mine} of 883 on dev; the arm scored {', '.join(map(str, dev))})" in FLAT
    test = sorted(ACC["official"][f"adapter:cleaned:{s}"]["correct"] for s in range(1, 6))
    assert test.index(ACC["official"][NAME]["correct"]) == 1 and "it is the second lowest" in FLAT
    assert f"({', '.join(map(str, test))})" in FLAT


def test_cleaned_against_random():
    r = EVAL["views"]["official"]["cleaned_vs_random"]
    assert r["verdict"] == "no detectable difference" and r["low"] < 0 < r["high"]
    assert f"cleaned is ahead by {pt(r['difference'])} points" in FLAT
    assert f"is {pt(r['low'])} to {pt(r['high'])}, which includes zero: **no detectable difference**" in FLAT
    s = load("results/screen/summary.json")["splits"]["train"]
    assert s["items"] - s["disagree"] == 5820
    assert f"the {s['disagree']} items" in FLAT and f"(5,820 of {s['items']:,} items)" in FLAT


def test_training_table():
    r = load("results/main/run1/cleaned/seed3/result.json")["train"]
    c = r["config"]
    cfg = json.loads(hub.committed(hub.CONFIG))
    assert (cfg["r"], cfg["lora_alpha"], cfg["lora_dropout"]) == (c["lora_r"], c["lora_alpha"], c["lora_dropout"])
    assert f"rank {cfg['r']}, alpha {cfg['lora_alpha']}, dropout {cfg['lora_dropout']}" in FLAT
    assert set(cfg["target_modules"]) == {f"{m}_proj" for m in ("q", "k", "v", "o", "gate", "up", "down")}
    assert "18,464,768 trainable parameters" in FLAT   # computed in tests/test_readme.py
    assert (r["items"], r["steps"], r["dropped_over_max_length"]) == (5820, 1092, [])
    assert c["batch_size"] * c["grad_accum"] == 16 and c["learning_rate"] == 2e-4 and c["epochs"] == 3
    assert f"{r['seconds'] / 3600:.2f} h of training ({r['seconds_per_step']:.3f} s per step), " \
           f"peak {r['peak_gpu_gb']} GB" in FLAT
    assert f"| Final training loss | {r['train_loss']:.4f} |" in CARD
    ids = r["ids_sha256"]
    assert f"ids SHA-256 `{ids[:8]}…{ids[-6:]}`" in CARD
    assert f"repo commit `{r['git_commit'][:7]}`" in CARD
    assert f"commit `{load('data/manifest.json')['commit'][:7]}`" in CARD
    freeze = (REPO_ROOT / "results/main/run1/pip-freeze.txt").read_text(encoding="utf-8").splitlines()
    for pkg in ("torch", "transformers", "peft", "trl"):
        version = next(l.split("==")[1] for l in freeze if l.startswith(f"{pkg}=="))
        assert f"{pkg} {version}" in FLAT


def test_revision():
    passes = {p["pass"]: p for p in load("results/test/run1/report.json")["passes"]}
    rev = passes[NAME]["revision"]
    assert rev == passes[NAME]["hub_main_sha"] == "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
    feas = load("results/feasibility/run1/report.json")
    assert feas["candidates"]["Qwen/Qwen2.5-1.5B-Instruct"]["licence"]["sha"] == rev
    assert feas["candidates"]["Qwen/Qwen2.5-1.5B-Instruct"]["licence"]["license"] == "apache-2.0"
    assert feas["started"].startswith("2026-11-10") and passes[NAME]["git_commit"].startswith("5aa1573")
    assert f'REVISION = "{rev}"' in CARD and f"`main` was `{rev}` when recorded before training (10 Nov 2026)" in FLAT


def code_blocks(lang):
    return re.findall(rf"```{lang}\n(.*?)\n```", CARD, re.S)


def test_prompt_code_is_the_training_prompt():
    assert f"prompt version 1, fingerprint `{prompt_fingerprint()}`" in FLAT
    space = {}
    exec(code_blocks("python")[0], space)
    for split in ("dev", "test"):
        for ex in load_split(split):
            facts = [text for _, text in ex["qa"]["model_input"]]
            assert space["build_messages"](facts, ex["qa"]["question"]) == messages(ex), ex["id"]


def test_example_is_the_first_test_item_and_its_reply():
    ex = load_split("test")[0]
    row = next(csv.DictReader(open(REPO_ROOT / "results/test/run1/cleaned/seed3/test.csv", encoding="utf-8",
                                   newline="")))
    code = code_blocks("python")[1]
    assert row["id"] == ex["id"] and f"(`{ex['id']}`)" in CARD
    facts = re.search(r"facts = \[\n(.*?)\n\]", code, re.S).group(1)
    assert [json.loads(l.strip().rstrip(",")) for l in facts.splitlines()] == [t for _, t in ex["qa"]["model_input"]]
    assert f'question = "{ex["qa"]["question"]}"' in code
    assert code.endswith(f"# {row['reply']}") and row["exe_correct"] == "1"
    assert "max_new_tokens=96, do_sample=False" in code   # finqa_lora.infer.MAX_NEW_TOKENS, greedy
    dev = load("results/main/run1/cleaned/seed3/result.json")["dev"]["exe_correct"]
    assert f"dev scoring gave {dev} of 883" in FLAT


def test_failure_tags():
    t = load("results/errors/test.json")[NAME]
    tags = t["tags"]
    assert t["failures"] == 1147 - ACC["official"][NAME]["correct"] == 397
    shown = [("other", "none of the rules"), ("wrong_number", "a wrong number"),
             ("wrong_table_row", "a wrong table row"), ("operand_order", "operands in the wrong order"),
             ("step_count", "a wrong number of steps"), ("wrong_operation", "a wrong operation"),
             ("scale_x100", "a percentage scaled"), ("sign", "a sign"), ("invalid", "an invalid program")]
    for tag, words in shown:
        assert f"{tags[tag]} {words}" in FLAT, tag
    assert sum(tags[t] for t, _ in shown) == t["failures"] and tags["near_value"] == 0
    o = load("results/errors/other_tags.json")["tags"]
    ranked = sorted(o, key=lambda k: -o[k]["items"])
    assert ranked[:2] == ["gold_wrong", "wrong_quantity"]


def test_label_problem_counts():
    t = load("results/audit/counts.json")["test_set"]
    assert f"confirmed {t['confirmed']} label problems among the 1,147 items (estimate {t['estimate']:.0f}, " \
           f"95% upper bound {t['upper95']:.0f})" in FLAT


def test_files_table():
    report = load("results/main/run1/report.json")
    run = next(r for r in report["runs"] if (r["arm"], r["seed"]) == ("cleaned", 3))
    assert f"| `adapter_model.safetensors` | {run['adapter_bytes']:,} | `{run['adapter_sha256']}` |" in CARD
    cfg = hub.committed(hub.CONFIG)
    assert f"| `adapter_config.json` | {len(cfg):,} | `{hashlib.sha256(cfg).hexdigest()}` |" in CARD
    assert hub.expected_adapter() == (run["adapter_sha256"], run["adapter_bytes"])


# finqa_lora.hub ------------------------------------------------------------------------------------

@pytest.fixture
def fake_adapter(tmp_path, monkeypatch):
    """A small file standing in for the adapter, with the card's checks pointed at it."""
    data = b"not really an adapter"
    path = tmp_path / "adapter_model.safetensors"
    path.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    monkeypatch.setattr(hub, "expected_adapter", lambda: (sha, len(data)))
    real = hub.committed
    # The card as in the working tree, so the tests pass before the card is committed (pytest runs
    # before every commit); the real committed() is what --upload uses.
    monkeypatch.setattr(hub, "committed",
                        lambda p: (REPO_ROOT / p).read_bytes() + sha.encode() if p == hub.CARD else real(p))
    return path


def test_local_checks_pass_and_use_committed_bytes(fake_adapter):
    files = hub.local_checks(fake_adapter)
    assert sorted(files) == ["README.md", "adapter_config.json", "adapter_model.safetensors"]
    assert files["adapter_config.json"] == hub.committed(hub.CONFIG)
    assert files["README.md"].startswith((REPO_ROOT / hub.CARD).read_bytes())


@pytest.mark.parametrize("change", ["size", "content", "config_beside", "missing"])
def test_local_checks_refuse(fake_adapter, change):
    if change == "size":
        fake_adapter.write_bytes(b"x")
    elif change == "content":
        fake_adapter.write_bytes(b"NOT REALLY AN ADAPTER")   # same length, other bytes
    elif change == "config_beside":
        fake_adapter.with_name("adapter_config.json").write_bytes(b"{}")
    else:
        fake_adapter.unlink()
    with pytest.raises(hub.HubCheckFailed):
        hub.local_checks(fake_adapter)


def test_real_adapter_hash_is_required(tmp_path):
    path = tmp_path / "adapter_model.safetensors"
    path.write_bytes(b"\0" * hub.expected_adapter()[1])   # right size, wrong bytes
    with pytest.raises(hub.HubCheckFailed, match="SHA-256"):
        hub.local_checks(path)


class FakeHub:
    """Enough of huggingface_hub for hub.upload: records what was uploaded and serves it back."""

    def __init__(self, user="PritRai75", corrupt=False):
        self.user, self.corrupt, self.store, self.created = user, corrupt, {}, []

    def module(self):
        fake = self

        class Api:
            def whoami(self):
                return {"name": fake.user}

            def create_repo(self, repo_id, **kw):
                fake.created.append((repo_id, kw))

            def upload_folder(self, repo_id, folder_path, **kw):
                fake.store = {p.name: p.read_bytes() for p in Path(folder_path).iterdir()}
                fake.message = kw["commit_message"]
                return types.SimpleNamespace(oid="c0ffee", commit_url=f"https://huggingface.co/{repo_id}/commit/c0ffee")

            def model_info(self, repo_id):
                return types.SimpleNamespace(private=False)

        def download(repo_id, name, revision, cache_dir):
            assert revision == "c0ffee"
            path = Path(cache_dir) / name
            path.write_bytes(fake.store[name] + (b"!" if fake.corrupt else b""))
            return str(path)

        return types.SimpleNamespace(HfApi=Api, hf_hub_download=download, __version__="fake")


def test_upload_verifies_the_hub_copy(fake_adapter, monkeypatch):
    fake = FakeHub()
    monkeypatch.setitem(sys.modules, "huggingface_hub", fake.module())
    files = hub.local_checks(fake_adapter)
    record = hub.upload(files, "a" * 40)
    assert fake.created == [(hub.REPO_ID, {"repo_type": "model", "private": False, "exist_ok": True})]
    assert fake.store["adapter_config.json"] == hub.committed(hub.CONFIG)
    assert fake.store["adapter_model.safetensors"] == fake_adapter.read_bytes()
    assert "aaaaaaa" in fake.message
    assert record["downloaded_back_identical"] and record["visibility"] == "public"
    assert record["files"]["adapter_model.safetensors"]["sha256"] == hashlib.sha256(fake_adapter.read_bytes()).hexdigest()


@pytest.mark.parametrize("problem", ["wrong_user", "corrupt"])
def test_upload_refuses(fake_adapter, monkeypatch, problem):
    fake = FakeHub(user="someone-else") if problem == "wrong_user" else FakeHub(corrupt=True)
    monkeypatch.setitem(sys.modules, "huggingface_hub", fake.module())
    with pytest.raises(hub.HubCheckFailed):
        hub.upload(hub.local_checks(fake_adapter), "a" * 40)
    if problem == "wrong_user":
        assert fake.store == {} and fake.created == []   # nothing created or uploaded


def test_upload_record():
    """results/hub/upload.json is the upload of this card, config and adapter, checked by download-back.
    The card in the repo must stay the one on the Hub: edit it and this fails until it is uploaded again."""
    u = load("results/hub/upload.json")
    assert (u["repo_id"], u["visibility"], u["downloaded_back_identical"]) == (hub.REPO_ID, "public", True)
    assert (u["arm"], u["seed"], u["main_run"]) == (hub.ARM, hub.SEED, hub.MAIN_RUN)
    assert u["hub_commit"] == "784e802f7e00146ef56f82c95e418a03ce67d5f8"
    assert u["hub_commit_url"] == f"https://huggingface.co/{hub.REPO_ID}/commit/{u['hub_commit']}"
    assert u["git_commit"] == "20dd5e295ebd8cdc6924e5b640fccc4335a6bd9c"
    card = (REPO_ROOT / hub.CARD).read_bytes()
    config = hub.committed(hub.CONFIG)
    sha, size = hub.expected_adapter()
    assert u["files"] == {
        "README.md": {"bytes": len(card), "sha256": hashlib.sha256(card).hexdigest()},
        "adapter_config.json": {"bytes": len(config), "sha256": hashlib.sha256(config).hexdigest()},
        "adapter_model.safetensors": {"bytes": size, "sha256": sha},
    }
    assert f"Hub commit `{u['hub_commit'][:7]}` from repo commit `{u['git_commit'][:7]}`" in README_TEXT
