"""Test passes (phase 4): every model of the comparison scored once on the 1,147 test items.

Runs only when the test gate is open (finqa_lora.testgate: check2 and check3 finished and committed);
finqa_lora.infer.run refuses the test split otherwise, before any model is loaded.

Passes (spec D6 and decision 40):
  adapter:<arm>:<seed>   the 10 main-run adapters (2 arms x 5 seeds), base pinned to BASE_REVISIONS
  base:<model>:<shots>   Qwen2.5-1.5B 0-shot and 4-shot, Qwen3-4B 4-shot, no adapter
Two chains, one per T4 (CHAINS). Seed pairs are split across the GPUs and each GPU runs both arms, so
neither arm is tied to one GPU.

Adapters (decision 41, 44) come from a private Kaggle dataset holding only the 10
adapter_model.safetensors files, in any layout and under any names: each is found by its SHA-256,
which must equal the one in the committed results/main/run*/report.json, and is paired with the
committed adapter_config.json of its run. A missing, duplicated or changed file stops the job.

Dev check before test: each chain first scores dev with one adapter (cleaned seed 1 on GPU 0,
random seed 1 on GPU 1) and compares the replies with the committed dev.csv of that run. Same
adapter, base, code and prompt, so replies should repeat; the tolerance is the one fixed before the
main runs (decision 38). jobs/testpass.sh starts the test passes only if both dev checks pass.

Usage:
  python -m finqa_lora.testpass locate --adapters /kaggle/input          (prints what it found)
  python -m finqa_lora.testpass devcheck --gpu 0 --adapters /kaggle/input --out /kaggle/working/testpass
  python -m finqa_lora.testpass run --pass adapter:cleaned:1 --adapters /kaggle/input --out <dir>
  python -m finqa_lora.testpass report --out <dir>
  python -m finqa_lora.testpass chain --gpu 0                            (that GPU's passes, one per line)
"""
import argparse
import csv
import json
import os
import shutil
import time
from pathlib import Path

from finqa_lora import REPO_ROOT
from finqa_lora.mainruns import ARMS, REPEAT_TOLERANCE, SEEDS
from finqa_lora.pilot import MODEL, sha256

MAIN_RESULTS = REPO_ROOT / "results" / "main"
# Hub commits of the base models, as recorded by feasibility run 1 (10 Nov 2026). Training loaded the
# Hub's main; each pass records what main resolves to at test time beside the pinned revision.
BASE_REVISIONS = {"Qwen/Qwen2.5-1.5B-Instruct": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
                  "Qwen/Qwen3-4B-Instruct-2507": "cdbee75f17c01a7cc42f958dc650907174af0554"}
BASES = {"qwen2.5-1.5b": "Qwen/Qwen2.5-1.5B-Instruct", "qwen3-4b": "Qwen/Qwen3-4B-Instruct-2507"}
BASE_PASSES = (("qwen2.5-1.5b", 0), ("qwen2.5-1.5b", 4), ("qwen3-4b", 4))
DEV_CHECK = {0: ("cleaned", 1), 1: ("random", 1)}
# Test-time estimates from the dev timings x 1,147 / 883: adapter about 5.7 min, 1.5B 0-shot 5.4 min,
# 1.5B 4-shot 7.6 min, 4B 4-shot 21 min; the 4B pass goes on the GPU without the two 1.5B base passes.
CHAINS = {0: [f"adapter:{a}:{s}" for a, s in (("cleaned", 1), ("random", 2), ("cleaned", 3), ("random", 4),
                                               ("cleaned", 5))] + ["base:qwen3-4b:4"],
          1: [f"adapter:{a}:{s}" for a, s in (("random", 1), ("cleaned", 2), ("random", 3), ("cleaned", 4),
                                               ("random", 5))] + ["base:qwen2.5-1.5b:0", "base:qwen2.5-1.5b:4"]}


def all_passes():
    return [f"adapter:{a}:{s}" for a in ARMS for s in SEEDS] + [f"base:{m}:{k}" for m, k in BASE_PASSES]


def parse_pass(name):
    kind, x, y = name.split(":")
    if kind == "adapter" and x in ARMS and int(y) in SEEDS:
        return {"kind": "adapter", "arm": x, "seed": int(y), "model": MODEL, "shots": 0}
    if kind == "base" and x in BASES and (x, int(y)) in BASE_PASSES:
        return {"kind": "base", "base": x, "model": BASES[x], "shots": int(y)}
    raise ValueError(f"unknown pass {name!r}; known: {', '.join(all_passes())}")


def expected_adapters(results=MAIN_RESULTS):
    """{(arm, seed): {...}} from the committed main-run reports: SHA-256, bytes, committed run folder."""
    out = {}
    for report in sorted(Path(results).glob("run*/report.json")):
        with open(report, encoding="utf-8") as f:
            rep = json.load(f)
        if rep.get("missing_runs"):
            raise SystemExit(f"{report}: runs missing {rep['missing_runs']}")
        for r in rep["runs"]:
            key = (r["arm"], r["seed"])
            if key in out:
                raise SystemExit(f"{r['arm']}/seed{r['seed']} appears in two main-run reports")
            folder = report.parent / r["arm"] / f"seed{r['seed']}"
            out[key] = {"sha256": r["adapter_sha256"], "bytes": r["adapter_bytes"],
                        "run": report.parent.name, "folder": folder,
                        "config": folder / "adapter" / "adapter_config.json", "dev_csv": folder / "dev.csv"}
    missing = [f"{a}/seed{s}" for a in ARMS for s in SEEDS if (a, s) not in out]
    if missing:
        raise SystemExit(f"the committed main-run reports lack {missing}")
    return out


def locate(root, expected=None):
    """Find each expected adapter under root by its SHA-256. Stops on a missing or duplicated file."""
    expected = expected or expected_adapters()
    sizes = {e["bytes"] for e in expected.values()}
    by_hash = {}
    for path in sorted(Path(root).rglob("*.safetensors")):
        if path.stat().st_size in sizes:
            by_hash.setdefault(sha256(path), []).append(path)
    found, problems = {}, []
    for (arm, seed), e in sorted(expected.items()):
        paths = by_hash.get(e["sha256"], [])
        if not paths:
            problems.append(f"{arm}/seed{seed}: no file under {root} with SHA-256 {e['sha256'][:12]}...")
        elif len(paths) > 1:
            problems.append(f"{arm}/seed{seed}: {len(paths)} copies: {', '.join(map(str, paths))}")
        else:
            found[(arm, seed)] = paths[0]
    if problems:
        raise SystemExit("adapters do not match the committed reports:\n  " + "\n  ".join(problems))
    return found


def assemble(arm, seed, root, work, expected=None):
    """Adapter folder for PEFT: the located weights (hash checked again after the copy) and the
    committed adapter_config.json of that run."""
    expected = expected or expected_adapters()
    e = expected[(arm, seed)]
    src = locate(root, {(arm, seed): e})[(arm, seed)]
    d = Path(work) / arm / f"seed{seed}"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, d / "adapter_model.safetensors")
    shutil.copyfile(e["config"], d / "adapter_config.json")
    if sha256(d / "adapter_model.safetensors") != e["sha256"]:
        raise SystemExit(f"{arm}/seed{seed}: copy of {src} changed on the way")
    return d, src


def hub_main_sha(model_id):
    try:
        from huggingface_hub import model_info
        return model_info(model_id).sha
    except Exception as e:  # offline or the Hub unreachable: recorded, not fatal
        return f"unavailable: {type(e).__name__}"


def _env():
    import torch
    return {"gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")}


def pass_dir(out, p):
    if p["kind"] == "adapter":
        return Path(out) / p["arm"] / f"seed{p['seed']}"
    return Path(out) / "base" / p["base"] / f"{p['shots']}shot"


def compare_replies(rows, committed_csv):
    with open(committed_csv, encoding="utf-8", newline="") as f:
        old = {r["id"]: r for r in csv.DictReader(f)}
    new = {r["id"]: r for r in rows}
    if set(new) != set(old):
        raise ValueError(f"dev check covers different items from {committed_csv}")
    right = lambda r: str(r["exe_correct"]) in ("1", "True")
    same = sum(new[i]["reply"] == old[i]["reply"] for i in new)
    now_only = sum(right(new[i]) and not right(old[i]) for i in new)
    then_only = sum(right(old[i]) and not right(new[i]) for i in new)
    return {"items": len(new), "same_reply": same, "right_now_only": now_only, "right_then_only": then_only,
            "discordant": now_only + then_only,
            "exe_correct_now": sum(right(r) for r in new.values()), "exe_correct_then": sum(right(r) for r in old.values())}


def within_tolerance(cmp):
    """Decision 38's limits, judged on the full dev split only."""
    if cmp["items"] != 883:
        return None
    return cmp["same_reply"] >= REPEAT_TOLERANCE["same_reply_min"] and cmp["discordant"] <= REPEAT_TOLERANCE["discordant_max"]


def _shown(path):
    path = Path(path).resolve()
    return path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else path.as_posix()


def _git_commit():
    from finqa_lora.train import git_commit
    return git_commit()


def devcheck(gpu, root, out, work, model_name=MODEL, limit=None, expected=None):
    """Score dev with this GPU's check adapter and compare with its committed dev.csv. Never touches test."""
    from finqa_lora.infer import run, write_rows
    from finqa_lora.prompt import prompt_fingerprint

    arm, seed = DEV_CHECK[gpu]
    expected = expected or expected_adapters()
    adapter, src = assemble(arm, seed, root, work, expected)
    revision = BASE_REVISIONS.get(model_name)
    rows, summary = run(model_name, "dev", adapter=str(adapter), limit=limit, revision=revision)
    d = Path(out) / "devcheck" / f"{arm}-seed{seed}"
    write_rows(rows, d / "dev.csv")
    committed = expected[(arm, seed)]["dev_csv"]
    if limit:
        with open(committed, encoding="utf-8", newline="") as f:
            keep = [r for r in csv.DictReader(f)][:limit]
        committed = d / "committed_dev_head.csv"
        with open(committed, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(keep[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(keep)
    cmp = compare_replies(rows, committed)
    result = {"arm": arm, "seed": seed, "gpu_slot": gpu, "adapter_source": str(src),
              "adapter_sha256": expected[(arm, seed)]["sha256"], "model": model_name, "revision": revision,
              "dev": summary, "against": _shown(expected[(arm, seed)]["dev_csv"]),
              "comparison": cmp, "tolerance": REPEAT_TOLERANCE, "within_tolerance": within_tolerance(cmp),
              "git_commit": _git_commit(), "prompt_fingerprint": prompt_fingerprint(), **_env()}
    with open(d / "result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"dev check {arm}/seed{seed}: same reply {cmp['same_reply']}/{cmp['items']}, "
          f"discordant {cmp['discordant']}, within tolerance {result['within_tolerance']}", flush=True)
    return result


def run_pass(name, root, out, work, limit=None, model_override=None, expected=None):
    """One test pass. finqa_lora.infer.run opens the test gate first and stores its record."""
    from finqa_lora.infer import run, write_rows
    from finqa_lora.prompt import PROMPT_VERSION, prompt_fingerprint
    from finqa_lora.testgate import open_gate

    p = parse_pass(name)
    open_gate()   # raises GateClosed before any download, copy or model load (infer.run checks again)
    model_id = model_override or p["model"]
    revision = None if model_override else BASE_REVISIONS[p["model"]]
    result = {"pass": name, **p, "model": model_id, "revision": revision, "hub_main_sha": hub_main_sha(model_id)
              if not model_override else None, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "limit": limit}
    adapter = None
    if p["kind"] == "adapter":
        expected = expected or expected_adapters()
        adapter, src = assemble(p["arm"], p["seed"], root, work, expected)
        result.update(adapter_sha256=expected[(p["arm"], p["seed"])]["sha256"], adapter_source=str(src),
                      main_run=expected[(p["arm"], p["seed"])]["run"])
    rows, summary = run(model_id, "test", shots=p["shots"], adapter=str(adapter) if adapter else None,
                        limit=limit, revision=revision)
    d = pass_dir(out, p)
    write_rows(rows, d / "test.csv")
    result.update(test=summary, finished=time.strftime("%Y-%m-%d %H:%M:%S"), git_commit=_git_commit(),
                  prompt_version=PROMPT_VERSION, prompt_fingerprint=prompt_fingerprint(), **_env())
    with open(d / "result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"{name}: test exe_correct {summary['exe_correct']}/{summary['items']} "
          f"({summary['seconds']} s)", flush=True)
    return result


def report(out):
    out = Path(out)
    done = {}
    for path in sorted(out.rglob("result.json")):
        if "devcheck" in path.parts:
            continue
        with open(path, encoding="utf-8") as f:
            r = json.load(f)
        done[r["pass"]] = r
    checks = []
    for path in sorted((out / "devcheck").glob("*/result.json")):
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        checks.append({k: c[k] for k in ("arm", "seed", "gpu_slot", "within_tolerance", "comparison", "gpu")})
    gates = {json.dumps(r["test"].get("test_gate"), sort_keys=True) for r in done.values()}
    rep = {"written": time.strftime("%Y-%m-%d %H:%M:%S"),
           "missing_passes": [n for n in all_passes() if n not in done],
           "dev_checks": checks,
           "one_gate_record": len(gates) == 1,
           "test_gate": next(iter(done.values()))["test"].get("test_gate") if done else None,
           "test": {n: {"exe_correct": r["test"]["exe_correct"], "prog_correct": r["test"]["prog_correct"],
                        "executes": r["test"]["executes"], "items": r["test"]["items"]} for n, r in sorted(done.items())},
           "passes": [{"pass": n, "model": r["model"], "revision": r["revision"], "hub_main_sha": r["hub_main_sha"],
                       "adapter_sha256": r.get("adapter_sha256"), "shots": r["shots"], "gpu": r["gpu"],
                       "cuda_visible_devices": r["cuda_visible_devices"], "seconds": r["test"]["seconds"],
                       "git_commit": r["git_commit"], "prompt_fingerprint": r["prompt_fingerprint"]}
                      for n, r in sorted(done.items())]}
    with open(out / "report.json", "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    return rep


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    lo = sub.add_parser("locate")
    lo.add_argument("--adapters", required=True)
    lo.add_argument("--results", default=str(MAIN_RESULTS))
    dc = sub.add_parser("devcheck")
    dc.add_argument("--gpu", type=int, choices=(0, 1), required=True)
    r = sub.add_parser("run")
    r.add_argument("--pass", dest="name", required=True)
    for s in (dc, r):
        s.add_argument("--adapters", required=True)
        s.add_argument("--out", required=True)
        s.add_argument("--work", default="/tmp/testpass-adapters")
        s.add_argument("--results", default=str(MAIN_RESULTS), help="committed main-run records (dry runs: another)")
        # CPU dry runs with the tiny model only:
        s.add_argument("--limit", type=int)
        s.add_argument("--model")
    rp = sub.add_parser("report")
    rp.add_argument("--out", required=True)
    c = sub.add_parser("chain")
    c.add_argument("--gpu", type=int, choices=(0, 1), required=True)
    a = p.parse_args()
    if a.cmd == "chain":
        print("\n".join(CHAINS[a.gpu]))
    elif a.cmd == "locate":
        for (arm, seed), path in locate(a.adapters, expected_adapters(a.results)).items():
            print(f"{arm}/seed{seed}  {path}")
    elif a.cmd == "devcheck":
        res = devcheck(a.gpu, a.adapters, a.out, a.work, model_name=a.model or MODEL, limit=a.limit,
                       expected=expected_adapters(a.results))
        if res["within_tolerance"] is False:
            raise SystemExit(1)
    elif a.cmd == "run":
        run_pass(a.name, a.adapters, a.out, a.work, limit=a.limit, model_override=a.model,
                 expected=expected_adapters(a.results))
    else:
        rep = report(a.out)
        print(json.dumps({k: rep[k] for k in ("missing_passes", "dev_checks", "one_gate_record", "test")}, indent=2))


if __name__ == "__main__":
    main()
