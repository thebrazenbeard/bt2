"""Bounded authenticated-client GitHub API collection for offline BT2 signals.

This collector uses the *already connected* gh CLI to obtain read-only PR/run
responses. It validates repository and SHA associations. CLI credential use
does not cryptographically attest stored JSON or authenticate an actor claim.
No GitHub writes, host-task creation, background poller or callback.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import re
import subprocess
import sys
from typing import Any, Callable

from signal_ingest.v1 import _utc
from signal_ingest.provider_bridge.v1 import (
    INPUT_SCHEMA, REPO, HEX64, canonical, reject_duplicate_keys
)


class CollectorError(ValueError):
    """Failure codes exclude original provider JSON and CLI stderr."""


def _parse(raw: str) -> dict[str, Any]:
    try:
        obj=json.loads(raw,object_pairs_hook=reject_duplicate_keys)
    except (ValueError,TypeError,RecursionError) as exc:
        raise CollectorError("INVALID_PROVIDER_JSON") from None
    if type(obj) is not dict:
        raise CollectorError("INVALID_PROVIDER_SHAPE")
    return obj


def _get(repo: str, suffix: str,
         runner: Callable[..., Any]) -> tuple[dict, str]:
    argv=["gh","api",f"repos/{repo}/{suffix}"]
    try:
        result=runner(argv,capture_output=True,text=True,timeout=15,check=True)
    except (subprocess.SubprocessError,OSError) as exc:
        raise CollectorError("PROVIDER_API_UNAVAILABLE") from None
    raw=result.stdout
    if type(raw) is not str or len(raw)>256000:
        raise CollectorError("PROVIDER_RESPONSE_TOO_LARGE")
    return _parse(raw), sha256(raw.encode("utf-8")).hexdigest()


def collect_pr(
    repository: str, pr_number: int, run_id: int | None,
    observed_at: str, host_access_cutoff: str,
    *, previous_head: str | None = None,
    seen_receipt_digests: list[str] | None = None,
    runner: Callable[..., Any] = subprocess.run,
) -> dict:
    """Obtain exactly one PR and optionally one CI run from GitHub.

    All output remains untrusted until an independently rooted receipt verifier
    confirms integrity. The package explicitly does *not* supply that verifier.
    """
    if type(repository) is not str or REPO.fullmatch(repository) is None:
        raise CollectorError("INVALID_REPOSITORY")
    if type(pr_number) is not int or not 1<=pr_number<=999999999:
        raise CollectorError("INVALID_PR_NUMBER")
    if run_id is not None and (type(run_id) is not int or not 1<=run_id<=9999999999999):
        raise CollectorError("INVALID_RUN_ID")
    try:
        _utc(observed_at)
        _utc(host_access_cutoff)
    except ValueError:
        raise CollectorError("INVALID_TIME") from None
    if previous_head is not None and (type(previous_head) is not str or
                                     re.fullmatch(r"[0-9a-f]{40}",previous_head) is None):
        raise CollectorError("INVALID_PREVIOUS_HEAD")
    seen=[] if seen_receipt_digests is None else seen_receipt_digests
    if type(seen) is not list or len(seen)>512 or any(type(x) is not str or
                                                      HEX64.fullmatch(x) is None for x in seen):
        raise CollectorError("INVALID_REPLAY_HISTORY")
    pr,pr_digest=_get(repository,f"pulls/{pr_number}",runner)
    head=pr.get("head")
    base=pr.get("base")
    if (pr.get("number") != pr_number or type(head) is not dict or
        type(base) is not dict or type(head.get("repo")) is not dict or
        type(base.get("repo")) is not dict or
        head["repo"].get("full_name") != repository or
        base["repo"].get("full_name") != repository or
        type(head.get("sha")) is not str or
        re.fullmatch(r"[0-9a-f]{40}",head["sha"]) is None or
        pr.get("html_url") != f"https://github.com/{repository}/pull/{pr_number}"):
        raise CollectorError("PROVIDER_PR_BINDING_MISMATCH")
    current=head["sha"]
    prior=current if previous_head is None else previous_head
    receipts=[
        {
            "event_id":f"github-pr-{pr_number}-{current[:16]}",
            "repository":repository,"subject":f"pr:{pr_number}",
            "kind":"PR_HEAD_CHANGE",
            "status":"CHANGED" if prior!=current else "UNCHANGED",
            "head":current,"previous_head":prior,
            "incident_key":f"github-pr-head-{pr_number}",
            "observed_at":observed_at,
            "source_ref":f"https://github.com/{repository}/pull/{pr_number}",
            "provider_response_sha256":pr_digest,
            "claimed_owner":"github-pr-source-unverified",
            "claimed_reviewer":None,"claims_authenticated":False,
            "transport":"GITHUB_API_SESSION_READONLY"
        }
    ]
    if run_id is not None:
        run,digest=_get(repository,f"actions/runs/{run_id}",runner)
        run_head=run.get("head_sha")
        outcome=run.get("conclusion")
        if (run.get("id") != run_id or type(run.get("repository")) is not dict or
            run["repository"].get("full_name") != repository or
            type(run_head) is not str or
            re.fullmatch(r"[0-9a-f]{40}",run_head) is None or
            run.get("status") != "completed" or
            outcome not in ("success","failure") or
            run.get("html_url") != f"https://github.com/{repository}/actions/runs/{run_id}"):
            raise CollectorError("PROVIDER_RUN_BINDING_MISMATCH")
        receipts.append({
            "event_id":f"github-run-{run_id}-{run_head[:16]}",
            "repository":repository,"subject":f"pr:{pr_number}",
            "kind":"CI_RESULT","status":"PASSED" if outcome=="success" else "FAILED",
            "head":run_head,"incident_key":f"github-ci-run-{run_id}",
            "observed_at":observed_at,
            "source_ref":f"https://github.com/{repository}/actions/runs/{run_id}",
            "provider_response_sha256":digest,
            "claimed_owner":"github-run-source-unverified",
            "claimed_reviewer":None,"claims_authenticated":False,
            "transport":"GITHUB_API_SESSION_READONLY"
        })
    return {
        "schema":INPUT_SCHEMA,
        "snapshot":{
            "observed_at":observed_at,
            "host_access_cutoff":host_access_cutoff,
            "subjects":[{"repository":repository,"subject":f"pr:{pr_number}",
                         "head":current,"runtime_required":False,
                         "reported_runtime_status":"UNKNOWN"}]
        },
        "receipts":receipts,
        "seen_receipt_digests":seen
    }


def main(argv: list[str] | None = None) -> int:
    ap=argparse.ArgumentParser(description="Read-only GitHub PR/run -> BT2 input")
    ap.add_argument("--repo",required=True)
    ap.add_argument("--pr",type=int,required=True)
    ap.add_argument("--run",type=int,default=None)
    ap.add_argument("--observed-at",required=True)
    ap.add_argument("--host-cutoff",required=True)
    ap.add_argument("--previous-head",default=None)
    args=ap.parse_args(argv)
    try:
        receipt=collect_pr(args.repo,args.pr,args.run,args.observed_at,
                           args.host_cutoff,previous_head=args.previous_head)
    except (CollectorError,ValueError) as exc:
        print("GITHUB_COLLECTOR_ERROR:"+str(exc) if isinstance(exc,CollectorError)
              else "GITHUB_COLLECTOR_ERROR:INVALID_SOURCE",file=sys.stderr)
        return 2
    sys.stdout.write(canonical(receipt).decode("utf-8")+"\n")
    return 0


if __name__=="__main__":
    raise SystemExit(main())