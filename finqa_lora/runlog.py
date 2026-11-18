"""Run log: every scored run and every per-item prediction in one SQLite file.

The committed result folders are the record; runs.db is an index built from them, so it is not
committed (it is in .gitignore) and can always be rebuilt:

  python -m finqa_lora.runlog build            # scans results/, writes runs.db
  python -m finqa_lora.runlog list             # one line per run

Each run row carries what is needed to say exactly what produced it: model, adapter SHA-256,
config hash (SHA-256 of the canonical training config without its output path), git commit,
prompt version and fingerprint, GPU, and the SHA-256 of its prediction CSV. Building fails if a
CSV's counts differ from the counts its report recorded, or if a CSV names an item that is not in
the split.

Sources read today: results/feasibility/run*/ (base models, zero-shot and 4-shot, dev),
results/pilot/run*/ (fine-tuned, dev after every epoch) and results/main/run*/ (fine-tuned at the
chosen epoch, dev). Later jobs (test passes) add a reader here.
"""
import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

from finqa_lora.data import load_split

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DB = ROOT / "runs.db"

SCHEMA = """
CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,      -- e.g. pilot/run1/lr1e-4/a/epoch2
    source TEXT NOT NULL,         -- folder under results/ it was read from
    kind TEXT NOT NULL,           -- base | finetuned
    model TEXT NOT NULL,
    shots INTEGER NOT NULL,
    split TEXT NOT NULL,
    arm TEXT, seed INTEGER, lr REAL, rep TEXT, epoch INTEGER, step INTEGER,
    adapter_sha256 TEXT,
    config_hash TEXT NOT NULL,
    config_json TEXT NOT NULL,
    git_commit TEXT,
    prompt_version INTEGER,
    prompt_fingerprint TEXT,
    gpu TEXT,
    items INTEGER NOT NULL,
    exe_correct INTEGER NOT NULL,
    prog_correct INTEGER NOT NULL,
    executes INTEGER NOT NULL,
    csv_path TEXT NOT NULL,
    csv_sha256 TEXT NOT NULL
);
CREATE TABLE predictions (
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    item_id TEXT NOT NULL,
    position INTEGER NOT NULL,    -- index of the item in its split, for paired statistics
    reply TEXT NOT NULL,
    program TEXT NOT NULL,
    executes INTEGER NOT NULL,
    value TEXT NOT NULL,
    exe_correct INTEGER NOT NULL,
    prog_correct INTEGER NOT NULL,
    PRIMARY KEY (run_id, item_id)
);
"""

_POSITIONS = {}


def positions(split):
    if split not in _POSITIONS:
        _POSITIONS[split] = {ex["id"]: i for i, ex in enumerate(load_split(split))}
    return _POSITIONS[split]


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def config_hash(config):
    """SHA-256 of the canonical JSON of a config, without its output folder."""
    clean = {k: v for k, v in config.items() if k != "out"}
    canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest(), canonical


def read_predictions(path, split):
    pos = positions(split)
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if r["id"] not in pos:
            raise ValueError(f"{path}: item {r['id']} is not in {split}")
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError(f"{path}: an item appears twice")
    return rows


def _add(con, run, csv_path, recorded, results):
    """Insert one run. recorded = the counts its report wrote; they must match the CSV."""
    rows = read_predictions(csv_path, run["split"])
    counts = {"items": len(rows), **{k: sum(int(r[k]) for r in rows)
                                     for k in ("exe_correct", "prog_correct", "executes")}}
    for k, v in recorded.items():
        if k in counts and counts[k] != v:
            raise ValueError(f"{csv_path}: CSV has {k} {counts[k]}, its report recorded {v}")
    run = {**run, **counts, "csv_path": "results/" + Path(csv_path).relative_to(results).as_posix(),
           "csv_sha256": sha256_file(csv_path)}
    con.execute(f"INSERT INTO runs ({','.join(run)}) VALUES ({','.join('?' * len(run))})", list(run.values()))
    pos = positions(run["split"])
    con.executemany(
        "INSERT INTO predictions VALUES (?,?,?,?,?,?,?,?,?)",
        [(run["run_id"], r["id"], pos[r["id"]], r["reply"], r["program"], int(r["executes"]), r["value"],
          int(r["exe_correct"]), int(r["prog_correct"])) for r in rows])


FEASIBILITY_RUNS = {"dev_base_0shot.csv": ("dev_zero_shot", 0), "dev_base_4shot.csv": ("dev_few_shot", 4),
                    "dev_base_0shot_repeat.csv": ("dev_zero_shot_repeat", 0)}


def add_feasibility(con, folder):
    folder = Path(folder)
    with open(folder / "report.json", encoding="utf-8") as f:
        report = json.load(f)
    env = report.get("environment", {})
    n = 0
    for model, cand in report["candidates"].items():
        model_dir = folder / model.replace("/", "__")
        for name, (key, shots) in FEASIBILITY_RUNS.items():
            path = model_dir / name
            if not path.exists() or key not in cand or "error" in cand[key]:
                continue
            rec = cand[key]
            cfg = {"kind": "base", "model": model, "shots": shots, "split": rec.get("split", "dev")}
            h, canonical = config_hash(cfg)
            _add(con, {
                "run_id": f"{folder.parent.name}/{folder.name}/{model}/{name[:-4]}",
                "source": f"{folder.parent.name}/{folder.name}", "kind": "base", "model": model, "shots": shots,
                "split": cfg["split"], "config_hash": h, "config_json": canonical,
                "git_commit": env.get("git_commit"), "prompt_version": report.get("prompt_version"),
                "prompt_fingerprint": report.get("prompt_fingerprint"), "gpu": env.get("gpu"),
            }, path, rec, folder.parent.parent)
            n += 1
    return n


def add_pilot(con, folder):
    folder = Path(folder)
    with open(folder / "report.json", encoding="utf-8") as f:
        report = json.load(f)
    n = 0
    for result_path in sorted(folder.glob("lr*/*/result.json")):
        with open(result_path, encoding="utf-8") as f:
            res = json.load(f)
        train = res["train"]
        h, canonical = config_hash(train["config"])
        for e in res["epochs"]:
            _add(con, {
                "run_id": f"{folder.parent.name}/{folder.name}/{result_path.parent.parent.name}/{res['rep']}/epoch{e['epoch']}",
                "source": f"{folder.parent.name}/{folder.name}", "kind": "finetuned",
                "model": train["config"]["model"], "shots": 0, "split": "dev",
                "arm": train["config"]["arm"], "seed": train["config"]["seed"], "lr": res["lr"], "rep": res["rep"],
                "epoch": e["epoch"], "step": e["step"], "adapter_sha256": e["adapter_sha256"],
                "config_hash": h, "config_json": canonical, "git_commit": train.get("git_commit"),
                "prompt_version": report.get("prompt_version"), "prompt_fingerprint": report.get("prompt_fingerprint"),
                "gpu": res.get("gpu"),
            }, result_path.parent / f"dev_epoch{e['epoch']}.csv", e, folder.parent.parent)
            n += 1
    return n


def add_main(con, folder):
    folder = Path(folder)
    with open(folder / "report.json", encoding="utf-8") as f:
        report = json.load(f)
    n = 0
    for result_path in sorted(folder.glob("*/seed*/result.json")):
        with open(result_path, encoding="utf-8") as f:
            res = json.load(f)
        train = res["train"]
        h, canonical = config_hash(train["config"])
        _add(con, {
            "run_id": f"{folder.parent.name}/{folder.name}/{res['arm']}/seed{res['seed']}/dev",
            "source": f"{folder.parent.name}/{folder.name}", "kind": "finetuned",
            "model": train["config"]["model"], "shots": 0, "split": "dev",
            "arm": res["arm"], "seed": res["seed"], "lr": res["lr"], "epoch": res["epoch"], "step": res["step"],
            "adapter_sha256": res["adapter_sha256"], "config_hash": h, "config_json": canonical,
            "git_commit": train.get("git_commit"), "prompt_version": train.get("prompt_version"),
            "prompt_fingerprint": train.get("prompt_fingerprint"), "gpu": res.get("gpu"),
        }, result_path.parent / "dev.csv", res["dev"], folder.parent.parent)
        n += 1
    if n != len(report.get("runs", [])):
        raise ValueError(f"{folder}: {n} result.json files, its report lists {len(report.get('runs', []))} runs")
    return n


def build(db=DB, results=RESULTS):
    db = Path(db)
    tmp = db.with_suffix(".db.part")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    try:
        con.executescript(SCHEMA)
        counts = {}
        for folder in sorted(Path(results).glob("feasibility/run*")):
            counts[f"feasibility/{folder.name}"] = add_feasibility(con, folder)
        for folder in sorted(Path(results).glob("pilot/run*")):
            counts[f"pilot/{folder.name}"] = add_pilot(con, folder)
        for folder in sorted(Path(results).glob("main/run*")):
            counts[f"main/{folder.name}"] = add_main(con, folder)
        con.commit()
    except Exception:
        con.close()
        tmp.unlink(missing_ok=True)     # a failed build keeps the previous runs.db untouched
        raise
    con.close()
    tmp.replace(db)
    return counts


def connect(db=DB):
    if not Path(db).exists():
        raise FileNotFoundError(f"{db} not found: run python -m finqa_lora.runlog build")
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def vector(con, run_id):
    """Per-item exe_correct in split order, for stats.py. Refuses runs that do not cover the split."""
    run = con.execute("SELECT split, items FROM runs WHERE run_id = ?", (run_id,)).fetchone()
    if run is None:
        raise KeyError(run_id)
    if run["items"] != len(positions(run["split"])):
        raise ValueError(f"{run_id} covers {run['items']} of {len(positions(run['split']))} {run['split']} items")
    return [r[0] for r in con.execute(
        "SELECT exe_correct FROM predictions WHERE run_id = ? ORDER BY position", (run_id,))]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["build", "list"])
    a = p.parse_args()
    if a.cmd == "build":
        for source, n in build().items():
            print(f"{n:3d} runs  {source}")
        print(f"wrote {DB.name}")
    else:
        con = connect()
        for r in con.execute("SELECT run_id, items, exe_correct, git_commit FROM runs ORDER BY run_id"):
            print(f"{r['exe_correct']:4d}/{r['items']:<4d} {(r['git_commit'] or '')[:7]}  {r['run_id']}")


if __name__ == "__main__":
    main()
