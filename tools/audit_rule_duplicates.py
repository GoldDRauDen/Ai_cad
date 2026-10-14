#!/usr/bin/env python3
"""Report repeated active-rule paragraphs without rewriting approved formulas.

No rule is automatically deleted. Similar wording may encode different
manufacturing scope, so review is required before any canonical consolidation.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

from audit_rule_coverage import ROOT, audit


def scan(root: Path = ROOT, min_chars: int = 170) -> dict:
    root = Path(root).resolve()
    active = audit(root)["active_modules"]
    index: dict[str, list[str]] = defaultdict(list)
    samples = {}
    for p in active:
        content = (root / p).read_text(encoding="utf-8")
        for para in re.split(r"\n\s*\n", content):
            normalized = re.sub(r"\s+", " ", para).strip().casefold()
            if len(normalized) < min_chars:
                continue
            if p not in index[normalized]:
                index[normalized].append(p)
                samples[normalized] = para[:140].replace("\n", " ")
    duplicates = [
        {"text_chars": len(k), "files": v, "sample": samples[k]}
        for k, v in index.items() if len(v) > 1
    ]
    duplicates.sort(key=lambda x: (-x["text_chars"], x["files"]))
    return {
        "scope": "ACTIVE_RULE_PARAGRAPHS_EXACT_NORMALIZED_ONLY",
        "min_paragraph_chars": min_chars,
        "repeated_cross_module_paragraphs": len(duplicates),
        "duplicate_examples": duplicates,
        "policy": "MANUAL_AUTHORITY_REVIEW_BEFORE_REPLACING_PARAGRAPHS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--min-chars", type=int, default=170)
    args = parser.parse_args()
    print(json.dumps(scan(args.repo_root, args.min_chars), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
