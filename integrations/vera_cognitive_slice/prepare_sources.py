"""Download exact reviewed source SHA bindings into a new directory."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess

def fetch(root: Path) -> None:
    pins = json.loads(Path(__file__).with_name("source_pins.json").read_text(encoding="utf-8"))
    if root.exists():
        raise ValueError("source destination exists; refusing to overwrite")
    root.mkdir(parents=True)
    for name, sha in pins.items():
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError(f"invalid pinned SHA for {name}")
        p = root / name
        p.mkdir()
        for args in (
            ["git", "init", "-q", str(p)],
            ["git", "-C", str(p), "remote", "add", "origin",
             f"https://github.com/thebrazenbeard/{name}.git"],
            ["git", "-C", str(p), "fetch", "-q", "--depth=1", "origin", sha],
            ["git", "-C", str(p), "checkout", "-q", "--detach", "FETCH_HEAD"],
        ):
            subprocess.run(args, check=True, timeout=120)
        head = subprocess.check_output(
            ["git", "-C", str(p), "rev-parse", "HEAD"], text=True, timeout=30
        ).strip()
        if head != sha:
            raise ValueError(f"source checkout mismatch: {name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    fetch(parser.parse_args().out.resolve())
