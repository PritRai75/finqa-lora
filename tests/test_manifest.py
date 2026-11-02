"""The data and the vendored scorer are exactly what data/manifest.json pins."""
import pytest

from finqa_lora import DATA_RAW, REPO_ROOT
from finqa_lora.fetch import load_manifest, sha256_of

MANIFEST = load_manifest()


@pytest.mark.parametrize("name", sorted(MANIFEST["files"]))
def test_split_matches_manifest(name):
    path = DATA_RAW / name
    assert path.exists(), f"{path} missing. Run: python -m finqa_lora.fetch"
    spec = MANIFEST["files"][name]
    assert path.stat().st_size == spec["bytes"]
    assert sha256_of(path) == spec["sha256"]


@pytest.mark.parametrize("rel", sorted(MANIFEST["vendored"]))
def test_vendored_file_is_upstream_copy(rel):
    # Fails if Git changed line endings (see .gitattributes) or the file was edited.
    assert sha256_of(REPO_ROOT / rel) == MANIFEST["vendored"][rel]["sha256"]
