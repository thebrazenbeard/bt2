"""Optional read-only HEAD freshness diagnostic for the eight source-bound repos."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent
EXPECTED = frozenset({
    "volition", "pre-active", "meso-crct", "humility",
    "meta", "semiotics", "semanticatlas", "personification",
})
_SHA = re.compile(r"^[0-9a-f]{40}$")


def compare_heads(pins: dict[str, str], resolve: Callable[[str], str]) -> dict[str, dict[str, object]]:
    """Return exact per-repo match evidence without touching source or pins."""
    if not isinstance(pins, dict) or set(pins) != EXPECTED:
        raise ValueError("source pins must name exactly the eight admitted repositories")
    if any(type(sha) is not str or not _SHA.fullmatch(sha) for sha in pins.values()):
        raise ValueError("source pins must contain canonical SHA-1 commit IDs")

    results: dict[str, dict[str, object]] = {}
    for name in sorted(EXPECTED):
        head = resolve(name)
        if type(head) is not str or not _SHA.fullmatch(head):
            raise ValueError(f"invalid live GitHub HEAD for {name}")
        results[name] = {"pinned": pins[name], "live_main": head, "matches": pins[name] == head}
    return results


def _github_head(name: str) -> str:
    # Exact allowlisted repo name is validated by compare_heads before invocation.
    completed = subprocess.run(
        ["gh", "api", f"repos/thebrazenbeard/{name}/commits/HEAD", "--jq", ".sha"],
        capture_output=True, text=True, timeout=30, check=True,
    )
    return completed.stdout.strip()


def main() -> int:
    try:
        pins = json.loads((ROOT / "source_pins.json").read_text(encoding="utf-8"))
        rows = compare_heads(pins, _github_head)
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, sort_keys=True))
        return 2
    current = all(row["matches"] for row in rows.values())
    print(json.dumps({"status": "CURRENT" if current else "STALE", "repositories": rows}, sort_keys=True))
    return 0 if current else 1


if __name__ == "__main__":
    raise SystemExit(main())
