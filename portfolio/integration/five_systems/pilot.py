"""Frozen synthetic three-arm retrieval pilot using an already-serving local model.

This tests contextual retrieval, not learning or SPM adapter effectiveness.
No model downloads, weights changes, external network, or tools are executed.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.request import ProxyHandler, Request, build_opener

from .local_store import LocalCorpus

MODEL_ID = "qwen2.5-coder:1.5b-instruct-q8_0"
CASES = (
    ("QX-714", "LUMET-38"),
    ("PJ-208", "ZARON-61"),
    ("RL-962", "TOVAR-47"),
    ("FN-435", "NEXIL-83"),
    ("BK-681", "VORIN-26"),
    ("DV-159", "KELAS-94"),
)
ARMS = ("closed_book", "irrelevant_passage", "relevant_retrieval")
QUESTION = "What is the inspection token for unit {unit}?"
SYSTEM = ("Answer using only the evidence passage below. "
          "If it does not explicitly identify this unit's token, answer UNKNOWN. "
          "Output only the token or UNKNOWN. No explanation.")


def make_corpus() -> LocalCorpus:
    corpus = LocalCorpus()
    for unit, token in CASES:
        corpus.ingest("controlled", unit,
                      f"Unit {unit} inspection token is {token}. "
                      "This token supersedes all previous unit entries.")
    return corpus


def prompt_for(corpus: LocalCorpus, unit: str, arm: str) -> str:
    if arm not in ARMS or unit not in dict(CASES):
        raise ValueError("Unregistered evaluation case/arm")
    passage = ""
    if arm == "relevant_retrieval":
        hits = corpus.search(f"Unit {unit}", ("controlled",), 10)
        matching = [hit for hit in hits if hit.knowledge_id == unit]
        if len(matching) != 1:
            raise ValueError("Target source missing in retrieval")
        passage = matching[0].content
    elif arm == "irrelevant_passage":
        alternate = CASES[(list(dict(CASES)).index(unit) + 1) % len(CASES)][0]
        passage = corpus.search(f"Unit {alternate}", ("controlled",), 10)[0].content
    else:
        passage = "No verified passage currently available for this unit."
    return f"{QUESTION.format(unit=unit)}\nEVIDENCE:\n{passage}"


def ask_ollama(prompt: str, model_id: str = MODEL_ID) -> tuple[str, float]:
    payload = {"model": model_id, "stream": False,
               "options": {"temperature": 0, "seed": 17, "num_predict": 24},
               "messages": [{"role": "system", "content": SYSTEM},
                            {"role": "user", "content": prompt}]}
    content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    opener = build_opener(ProxyHandler({}))
    req = Request("http://127.0.0.1:11434/api/chat", data=content,
                  headers={"Content-Type": "application/json"}, method="POST")
    started = time.perf_counter()
    with opener.open(req, timeout=60) as response:
        raw = response.read(100_001)
    elapsed = round((time.perf_counter() - started) * 1000, 2)
    if len(raw) > 100_000:
        raise RuntimeError("Model response larger than limit")
    result = json.loads(raw.decode("utf-8"))
    if result.get("model") != model_id or not isinstance(result.get("message"), dict):
        raise RuntimeError("Model identity or output malformed")
    answer = result["message"].get("content")
    if not isinstance(answer, str):
        raise RuntimeError("Model text missing")
    return answer.strip(), elapsed


def experiment(model_id: str = MODEL_ID, generate=ask_ollama) -> dict:
    corpus = make_corpus()
    fixture_sha = sha256(json.dumps(CASES).encode()).hexdigest()
    scores = {arm: 0 for arm in ARMS}
    records = []
    # Interleave/control arm order across cases to reduce positional bias.
    for idx, (unit, expected) in enumerate(CASES):
        for arm in ARMS[idx % 3:] + ARMS[:idx % 3]:
            prompt = prompt_for(corpus, unit, arm)
            answer, elapsed = generate(prompt, model_id)
            correct = answer == expected
            scores[arm] += int(correct)
            records.append({"unit": unit, "arm": arm, "response": answer,
                            "expected": expected, "exact_match": correct,
                            "latency_ms": elapsed,
                            "prompt_sha256": sha256(prompt.encode()).hexdigest()})
    return {"schema": "BT2_FIVE_SYSTEM_RETRIEVAL_PILOT_V1",
            "model_advertised_id_not_attested": model_id, "fixture_sha256": fixture_sha,
            "source_type": "frozen_synthetic_manual", "cases_per_arm": len(CASES),
            "scores": scores, "records": records,
            "learned_state_or_training_verified": False,
            "retrieval_not_neural_persistence": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default=MODEL_ID)
    args = parser.parse_args()
    result = experiment(args.model)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2, ensure_ascii=False)
        output.write("\n")
    print(json.dumps({"source": result["fixture_sha256"], "scores": result["scores"],
                      "cases_per_arm": result["cases_per_arm"]}))


if __name__ == "__main__":
    main()
