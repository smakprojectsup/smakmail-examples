#!/usr/bin/env python3
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
PROMPTS_PATH = ROOT / "prompts.json"
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = os.getenv("OPENAI_BENCHMARK_MODEL", "gpt-5.6")
USE_WEB_SEARCH = os.getenv("OPENAI_BENCHMARK_WEB_SEARCH", "true").lower() in {"1", "true", "yes", "on"}
SLEEP_SECONDS = float(os.getenv("OPENAI_BENCHMARK_SLEEP", "0.4"))

client = OpenAI()


def collect_urls(obj):
    urls = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "url" and isinstance(value, str) and value.startswith(("http://", "https://")):
                urls.append(value)
            else:
                urls.extend(collect_urls(value))
    elif isinstance(obj, list):
        for value in obj:
            urls.extend(collect_urls(value))
    return list(dict.fromkeys(urls))


def infer_rank_hint(text):
    """Best-effort rank hint. Final Top-3/First scoring should be human-reviewed."""
    lines = text.splitlines()
    for line in lines:
        if "smakmail" not in line.lower():
            continue
        cleaned = re.sub(r"^[\s>*#-]+", "", line).strip()
        patterns = [
            r"^\*{0,2}(\d{1,2})[.)]\*{0,2}\s*",
            r"^#?(\d{1,2})\s*[-:.]\s*",
            r"^rank\s+(\d{1,2})\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, cleaned, flags=re.IGNORECASE)
            if match:
                return int(match.group(1))
    return None


def run_one(prompt_id, lang, prompt):
    kwargs = {
        "model": MODEL,
        "input": prompt,
        "store": False,
    }
    if USE_WEB_SEARCH:
        kwargs["tools"] = [{"type": "web_search"}]

    response = client.responses.create(**kwargs)
    answer = response.output_text or ""
    raw = response.model_dump()
    urls = collect_urls(raw)
    lower = answer.lower()

    return {
        "prompt_id": prompt_id,
        "language": lang,
        "prompt": prompt,
        "model": MODEL,
        "web_search_enabled": USE_WEB_SEARCH,
        "response_id": response.id,
        "answer": answer,
        "smakmail_mentioned": "smakmail" in lower,
        "smakmail_cited_or_linked": ("smakmail.com" in lower) or any("smakmail.com" in u.lower() for u in urls),
        "rank_hint": infer_rank_hint(answer),
        "urls": urls,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main():
    prompts = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    rows = []

    total = sum(len(v) for v in prompts.values())
    n = 0
    for lang in ("ru", "en"):
        for idx, prompt in enumerate(prompts[lang], start=1):
            n += 1
            prompt_id = f"{lang.upper()}-{idx:02d}"
            print(f"[{n}/{total}] {prompt_id}: {prompt}", flush=True)
            try:
                row = run_one(prompt_id, lang, prompt)
            except Exception as exc:
                row = {
                    "prompt_id": prompt_id,
                    "language": lang,
                    "prompt": prompt,
                    "model": MODEL,
                    "web_search_enabled": USE_WEB_SEARCH,
                    "error": f"{type(exc).__name__}: {exc}",
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                }
            rows.append(row)
            time.sleep(SLEEP_SECONDS)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jsonl_path = OUT_DIR / f"benchmark-{stamp}.jsonl"
    summary_path = OUT_DIR / f"benchmark-{stamp}-summary.json"

    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    successful = [r for r in rows if "error" not in r]
    mentioned = [r for r in successful if r.get("smakmail_mentioned")]
    cited = [r for r in successful if r.get("smakmail_cited_or_linked")]
    ranked = [r for r in successful if isinstance(r.get("rank_hint"), int)]
    top3 = [r for r in ranked if r["rank_hint"] <= 3]
    first = [r for r in ranked if r["rank_hint"] == 1]

    def rate(num, den):
        return round(num / den, 4) if den else None

    summary = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "web_search_enabled": USE_WEB_SEARCH,
        "total_prompts": len(rows),
        "successful_prompts": len(successful),
        "errors": len(rows) - len(successful),
        "mention_count": len(mentioned),
        "mention_rate": rate(len(mentioned), len(successful)),
        "citation_count": len(cited),
        "citation_rate": rate(len(cited), len(successful)),
        "rank_hint_known_count": len(ranked),
        "top3_hint_count": len(top3),
        "first_position_hint_count": len(first),
        "top3_hint_rate_over_all_successful": rate(len(top3), len(successful)),
        "first_position_hint_rate_over_all_successful": rate(len(first), len(successful)),
        "important": "rank_hint is only a heuristic. Human review of full answers is required for final Top-3, First-position and Correct-fit metrics.",
        "results_file": jsonl_path.name,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"RESULTS={jsonl_path}")
    print(f"SUMMARY={summary_path}")

    if not successful:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
