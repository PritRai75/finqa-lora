"""Upload the Hub adapter (decision 46: cleaned seed 3) with its model card, and check the upload.

Without --upload nothing leaves the machine: the script checks the adapter's SHA-256 and size against
the training run's report, takes the card and adapter_config.json from the Git blobs at HEAD (the
committed bytes, whatever the working tree holds), and lists what it would upload.

With --upload it also requires the card to be committed and unchanged and HEAD to be on origin/main,
creates the public model repo if needed, uploads the three files in one Hub commit, downloads them
back from that commit and compares every SHA-256, and writes results/hub/upload.json.

The token comes from the environment (HF_TOKEN) or a previous `hf auth login`; it is never read,
printed or written by this script. Needs huggingface_hub (2.4.0 used), which requirements.txt omits.

Usage:
  python -m finqa_lora.hub --adapter PATH/TO/adapter_model.safetensors            # checks only
  python -m finqa_lora.hub --adapter PATH/TO/adapter_model.safetensors --upload   # upload and verify
"""
import argparse
import datetime
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from finqa_lora import REPO_ROOT

REPO_ID = "PritRai75/qwen2.5-1.5b-finqa-lora"
ARM, SEED, MAIN_RUN = "cleaned", 3, "run1"          # decision 46
CARD = "hub/model_card.md"
CONFIG = f"results/main/{MAIN_RUN}/{ARM}/seed{SEED}/adapter/adapter_config.json"
REPORT = f"results/main/{MAIN_RUN}/report.json"
RECORD = REPO_ROOT / "results" / "hub" / "upload.json"
WEIGHTS = "adapter_model.safetensors"


class HubCheckFailed(Exception):
    pass


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, capture_output=True).stdout


def committed(path):
    """Bytes of path as committed at HEAD."""
    try:
        return git("show", f"HEAD:{path}")
    except subprocess.CalledProcessError:
        raise HubCheckFailed(f"{path} is not committed at HEAD: commit it first") from None


def expected_adapter():
    report = json.loads(committed(REPORT))
    runs = [r for r in report["runs"] if r["arm"] == ARM and r["seed"] == SEED]
    if len(runs) != 1:
        raise HubCheckFailed(f"{REPORT} has {len(runs)} runs for {ARM} seed {SEED}, expected 1")
    return runs[0]["adapter_sha256"], runs[0]["adapter_bytes"]


def local_checks(adapter):
    """Everything that can be checked without the network. Returns {name in repo: bytes or Path}."""
    adapter = Path(adapter)
    if not adapter.is_file():
        raise HubCheckFailed(f"{adapter} is not a file")
    sha, size = expected_adapter()
    if adapter.stat().st_size != size:
        raise HubCheckFailed(f"{adapter} has {adapter.stat().st_size} bytes, the run recorded {size}")
    got = sha256_file(adapter)
    if got != sha:
        raise HubCheckFailed(f"{adapter} SHA-256 {got}, the run recorded {sha}")
    card, config = committed(CARD), committed(CONFIG)
    if sha not in card.decode("utf-8") or sha256_bytes(config) not in card.decode("utf-8"):
        raise HubCheckFailed(f"{CARD} at HEAD does not state the SHA-256 of both files")
    beside = adapter.with_name("adapter_config.json")
    if beside.is_file() and sha256_file(beside) != sha256_bytes(config):
        raise HubCheckFailed(f"{beside} differs from the committed {CONFIG}")
    return {"README.md": card, "adapter_config.json": config, WEIGHTS: adapter}


def publish_checks(paths=(CARD, CONFIG)):
    """The files that go up must be the committed ones, and the commit must be on GitHub."""
    if git("status", "--porcelain", "--", *paths).strip():
        raise HubCheckFailed(f"uncommitted changes in {', '.join(paths)}")
    git("fetch", "--quiet", "origin", "main")
    if subprocess.run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], cwd=REPO_ROOT).returncode:
        raise HubCheckFailed("HEAD is not on origin/main: push the commit first")
    return git("rev-parse", "HEAD").decode().strip()


def stage(files, folder):
    folder = Path(folder)
    for name, content in files.items():
        data = content.read_bytes() if isinstance(content, Path) else content
        (folder / name).write_bytes(data)
    return {name: {"bytes": (folder / name).stat().st_size, "sha256": sha256_file(folder / name)}
            for name in sorted(files)}


def upload_verified(repo_id, repo_type, files, message, description):
    """Upload files ({name: bytes or Path}) in one Hub commit to a public repo, download them back from that
    commit and compare every SHA-256. Shared by the adapter and the dataset upload."""
    import huggingface_hub
    from huggingface_hub import HfApi, hf_hub_download

    api = HfApi()
    owner = repo_id.split("/")[0]
    user = api.whoami()["name"]
    if user != owner:
        raise HubCheckFailed(f"the token belongs to {user!r}, not {owner!r}")
    with tempfile.TemporaryDirectory() as tmp:
        staged = stage(files, tmp)
        api.create_repo(repo_id, repo_type=repo_type, private=False, exist_ok=True)
        info = api.upload_folder(repo_id=repo_id, repo_type=repo_type, folder_path=tmp,
                                 commit_message=message, commit_description=description)
    with tempfile.TemporaryDirectory() as tmp:
        back = {}
        for name in staged:
            path = hf_hub_download(repo_id, name, repo_type=repo_type, revision=info.oid, cache_dir=tmp)
            back[name] = {"bytes": Path(path).stat().st_size, "sha256": sha256_file(path)}
    if back != staged:
        raise HubCheckFailed(f"the Hub copy differs from what was uploaded: {back} != {staged}")
    repo_info = api.model_info if repo_type == "model" else api.dataset_info
    return {
        "repo_id": repo_id,
        "hub_commit": info.oid,
        "hub_commit_url": info.commit_url,
        "visibility": "private" if repo_info(repo_id).private else "public",
        "files": staged,
        "downloaded_back_identical": True,
        "huggingface_hub": huggingface_hub.__version__,
        "uploaded": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def upload(files, head):
    r = upload_verified(REPO_ID, "model", files,
                        f"Adapter (cleaned seed 3) and card from finqa-lora {head[:7]}",
                        f"https://github.com/PritRai75/finqa-lora/tree/{head}")
    return {**{k: r[k] for k in ("repo_id", "hub_commit", "hub_commit_url", "visibility")}, "git_commit": head,
            "arm": ARM, "seed": SEED, "main_run": MAIN_RUN,
            **{k: r[k] for k in ("files", "downloaded_back_identical", "huggingface_hub", "uploaded")}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", required=True, help="path to the adapter_model.safetensors of cleaned seed 3")
    p.add_argument("--upload", action="store_true", help="upload to the Hub and verify (default: checks only)")
    a = p.parse_args()
    try:
        run(a)
    except HubCheckFailed as e:
        raise SystemExit(f"refused: {e}")


def run(a):
    files = local_checks(a.adapter)
    if not a.upload:
        with tempfile.TemporaryDirectory() as tmp:
            for name, f in stage(files, tmp).items():
                print(f"would upload {name:28} {f['bytes']:>11,} bytes  {f['sha256']}")
        print(f"checks passed; nothing uploaded. Add --upload to publish {REPO_ID} (public).")
        return
    head = publish_checks()
    record = upload(files, head)
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    with open(RECORD, "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    print(f"uploaded and verified: {record['hub_commit_url']} ({record['visibility']})")
    print(f"wrote {RECORD.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
