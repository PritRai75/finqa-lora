"""Download the FinQA splits at a pinned commit and check them against data/manifest.json.

Usage: python -m finqa_lora.fetch
"""
import hashlib
import json
import sys
import urllib.request

from finqa_lora import DATA_RAW, REPO_ROOT

MANIFEST = REPO_ROOT / "data" / "manifest.json"


def load_manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_valid(path, spec):
    return path.exists() and path.stat().st_size == spec["bytes"] and sha256_of(path) == spec["sha256"]


def main():
    m = load_manifest()
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    for name, spec in m["files"].items():
        dest = DATA_RAW / name
        if is_valid(dest, spec):
            print(f"ok      {name} (already present)")
            continue
        url = m["raw_url"].format(commit=m["commit"], path=spec["path"])
        print(f"fetch   {name} from {url}")
        tmp = dest.with_suffix(".part")
        urllib.request.urlretrieve(url, tmp)
        if not is_valid(tmp, spec):
            tmp.unlink()
            sys.exit(f"FAILED  {name}: size or SHA-256 does not match the manifest")
        tmp.replace(dest)
        print(f"ok      {name}")


if __name__ == "__main__":
    main()
