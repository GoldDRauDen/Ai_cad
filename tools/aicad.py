#!/usr/bin/env python3
"""AICad: byte-exact, verifiable rule index over the inherited TrainAiCad rule tree.

Subcommands:
  build   Index every git-tracked file into build/aicad.sqlite (deterministic).
  verify  Rebuild in memory from disk and check every integrity invariant.
          Fails on: lost bytes, unindexed/unrouted rule files not declared in
          KNOWN_GAPS.yaml, stale declared gaps, router paths missing, stale DB.
  search  Full-text search (FTS5 trigram, works for JP/VN/EN substrings) over
          the default rule scope. Every hit reports file, line range and route state.
  rule    Print a chunk by id (path:Lstart-end) or every chunk of a path.

This layer never edits or interprets rules. Routing itself stays in
skills/lispcad/router/ROUTER.yaml and tools/resolve_rules.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "build" / "aicad.sqlite"
GAPS_PATH = ROOT / "KNOWN_GAPS.yaml"
ROUTER_PATH = ROOT / "skills/lispcad/router/ROUTER.yaml"
COVERAGE_PATH = ROOT / "skills/lispcad/router/RULE_COVERAGE.yaml"

ENTRY_FILES = {
    "SKILL.md", "AI_BOOTSTRAP.md", "AI_ENTRYPOINT.md", "AGENTS.md",
    "README.md", "QA_ENTRYPOINT.md", "PROJECT_INSTRUCTIONS_GPT_WEB.md",
}
RULE_PREFIXES = (
    "references/",
    "skills/lispcad/core/",
    "skills/lispcad/modes/",
    "skills/lispcad/features/",
    "skills/lispcad/topology/",
)
ARCHIVE_PREFIXES = (
    "skills/lispcad/versions/",
    "skills/lispcad/portable/",
    "docs/history/",
)
DEFAULT_KINDS = {"entry", "router", "rule", "schema", "tool", "doc"}
PATH_RE = re.compile(r"\.(md|yaml|py)$")


def classify(rel: str) -> str:
    if rel.startswith(ARCHIVE_PREFIXES):
        return "archive"
    if rel.startswith("regression/"):
        return "qa_evidence"
    if rel.startswith("tests/"):
        return "test"
    if rel.startswith(".github/"):
        return "ci"
    if rel.startswith("services/"):
        return "service"
    if rel in ENTRY_FILES:
        return "entry"
    if rel.startswith("skills/lispcad/router/"):
        return "router"
    if rel.startswith(RULE_PREFIXES) and rel.endswith((".md", ".yaml")):
        return "rule"
    if rel.startswith("tools/") and rel.endswith(".py"):
        return "tool"
    if rel.startswith("tools/") and rel.endswith(".md"):
        return "schema"
    if rel.startswith("docs/"):
        return "doc"
    return "other"


def scope_of(kind: str) -> str:
    return "default" if kind in DEFAULT_KINDS else "excluded"


def git_tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True, capture_output=True,
    ).stdout.decode("utf-8")
    return sorted(p for p in out.split("\0") if p)


def source_state() -> tuple[str, bool]:
    commit = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    dirty = bool(subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"],
        check=True, capture_output=True, text=True,
    ).stdout.strip())
    return commit, dirty


def router_paths(node, out: set[str]) -> set[str]:
    if isinstance(node, dict):
        for v in node.values():
            router_paths(v, out)
    elif isinstance(node, list):
        for v in node:
            router_paths(v, out)
    elif isinstance(node, str) and PATH_RE.search(node):
        out.add(node)
    return out


NON_ROUTING_SECTIONS = {"portable_compatibility", "history_policy"}


def load_routed() -> set[str]:
    """Paths the router actually loads. Compatibility/history notices are excluded:
    they name archive files only to forbid or diagnose them, never to route them."""
    router = yaml.safe_load(ROUTER_PATH.read_text(encoding="utf-8"))
    routing = {k: v for k, v in router.items() if k not in NON_ROUTING_SECTIONS}
    return router_paths(routing, set())


def load_gaps() -> dict:
    if not GAPS_PATH.exists():
        return {"rule_gaps": [], "tool_acks": []}
    data = yaml.safe_load(GAPS_PATH.read_text(encoding="utf-8")) or {}
    return {
        "rule_gaps": data.get("rule_gaps") or [],
        "tool_acks": data.get("tool_acks") or [],
    }


def chunk_bounds(rel: str, lines: list[str]) -> list[int]:
    suffix = rel.rsplit(".", 1)[-1]
    bounds = {0}
    if suffix == "md":
        fence = False
        for i, line in enumerate(lines):
            if line.lstrip().startswith("```"):
                fence = not fence
                continue
            if not fence and i > 0 and re.match(r"^#{1,6}\s", line):
                bounds.add(i)
    elif suffix in ("yaml", "yml"):
        for i, line in enumerate(lines):
            if i > 0 and re.match(r"^[A-Za-z_][\w\-]*:", line):
                bounds.add(i)
    elif suffix == "py":
        for i, line in enumerate(lines):
            if i > 0 and re.match(r"^(def |class )", line):
                bounds.add(i)
    return sorted(bounds)


def chunk_text(rel: str, text: str) -> list[dict]:
    lines = text.splitlines(keepends=True)
    if not lines:
        return []
    bounds = chunk_bounds(rel, lines)
    chunks = []
    for idx, start in enumerate(bounds):
        end = bounds[idx + 1] if idx + 1 < len(bounds) else len(lines)
        body = "".join(lines[start:end])
        first = lines[start].strip()
        heading = first[:160] if first.startswith("#") else "(preamble)"
        chunks.append({
            "id": f"{rel}:L{start + 1}-{end}",
            "path": rel,
            "start_line": start + 1,
            "end_line": end,
            "heading": heading,
            "text": body,
        })
    return chunks


def route_state(rel: str, kind: str, routed: set[str], gaps: dict) -> str:
    if kind != "rule":
        return "n/a"
    if rel in routed:
        return "routed"
    if any(g["path"] == rel for g in gaps["rule_gaps"]):
        return "known_gap"
    return "UNROUTED"


def build_rows() -> dict:
    routed = load_routed()
    gaps = load_gaps()
    files, chunks = [], []
    for rel in git_tracked_files():
        raw = (ROOT / rel).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        kind = classify(rel)
        try:
            text = raw.decode("utf-8")
            binary = 0
        except UnicodeDecodeError:
            text, binary = None, 1
        files.append({
            "path": rel,
            "kind": kind,
            "scope": scope_of(kind),
            "route_state": route_state(rel, kind, routed, gaps),
            "sha256": sha,
            "bytes": len(raw),
            "binary": binary,
        })
        if text is not None:
            chunks.extend(chunk_text(rel, text))
    return {"files": files, "chunks": chunks, "routed": sorted(routed), "gaps": gaps}


def write_db(rows: dict, commit: str, dirty: bool) -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE files (
            path TEXT PRIMARY KEY, kind TEXT, scope TEXT, route_state TEXT,
            sha256 TEXT, bytes INTEGER, binary INTEGER);
        CREATE TABLE chunks (
            id TEXT PRIMARY KEY, path TEXT, start_line INTEGER, end_line INTEGER,
            heading TEXT, text TEXT);
        CREATE INDEX chunks_path ON chunks(path);
        CREATE VIRTUAL TABLE chunk_tri USING fts5(
            id UNINDEXED, path UNINDEXED, heading, text, tokenize='trigram');
        CREATE TABLE routes (path TEXT PRIMARY KEY);
    """)
    con.executemany(
        "INSERT INTO files VALUES (?,?,?,?,?,?,?)",
        [(f["path"], f["kind"], f["scope"], f["route_state"], f["sha256"],
          f["bytes"], f["binary"]) for f in rows["files"]],
    )
    con.executemany(
        "INSERT INTO chunks VALUES (?,?,?,?,?,?)",
        [(c["id"], c["path"], c["start_line"], c["end_line"], c["heading"], c["text"])
         for c in rows["chunks"]],
    )
    con.executemany(
        "INSERT INTO chunk_tri VALUES (?,?,?,?)",
        [(c["id"], c["path"], c["heading"], c["text"]) for c in rows["chunks"]],
    )
    con.executemany("INSERT INTO routes VALUES (?)", [(p,) for p in rows["routed"]])
    con.executemany("INSERT INTO meta VALUES (?,?)", [
        ("source_commit", commit),
        ("working_tree_dirty", str(dirty)),
        ("file_count", str(len(rows["files"]))),
        ("chunk_count", str(len(rows["chunks"]))),
        ("files_digest", hashlib.sha256(json.dumps(
            [(f["path"], f["sha256"]) for f in rows["files"]]).encode()).hexdigest()),
    ])
    con.commit()
    con.close()


def cmd_build(_args) -> int:
    commit, dirty = source_state()
    rows = build_rows()
    write_db(rows, commit, dirty)
    counts = {}
    for f in rows["files"]:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    print(json.dumps({
        "db": str(DB_PATH.relative_to(ROOT)),
        "source_commit": commit,
        "working_tree_dirty": dirty,
        "files": len(rows["files"]),
        "chunks": len(rows["chunks"]),
        "files_by_kind": counts,
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_verify(_args) -> int:
    failures, warnings = [], []
    rows = build_rows()
    by_path = {f["path"]: f for f in rows["files"]}
    chunks_by_path: dict[str, list[dict]] = {}
    for c in rows["chunks"]:
        chunks_by_path.setdefault(c["path"], []).append(c)

    # 1. Byte-exact reconstruction for every text file.
    for rel, f in by_path.items():
        if f["binary"]:
            continue
        disk = (ROOT / rel).read_text(encoding="utf-8")
        rebuilt = "".join(c["text"] for c in chunks_by_path.get(rel, []))
        if rebuilt != disk:
            failures.append(f"RECONSTRUCTION_MISMATCH {rel}")
        if disk and rel not in chunks_by_path:
            failures.append(f"NO_CHUNKS {rel}")

    # 2. Chunk ids unique.
    ids = [c["id"] for c in rows["chunks"]]
    if len(ids) != len(set(ids)):
        failures.append("DUPLICATE_CHUNK_ID")

    # 3. Every router path exists on disk and is indexed.
    for p in sorted(rows["routed"]):
        if p not in by_path:
            failures.append(f"ROUTER_PATH_MISSING {p}")

    # 4. Every RULE_COVERAGE active path exists on disk.
    coverage = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))
    for rel_list in coverage.get("release_coverage", {}).values():
        for p in rel_list.get("active", []):
            if p.endswith("/") or "*" in p:
                continue
            if p not in by_path:
                failures.append(f"COVERAGE_PATH_MISSING {p}")

    # 5. Unrouted rule files must be declared; declared gaps must still be real.
    declared = {g["path"]: g for g in rows["gaps"]["rule_gaps"]}
    actual_unrouted = {f["path"] for f in rows["files"]
                       if f["route_state"] in ("UNROUTED", "known_gap")}
    for p in sorted(actual_unrouted - set(declared)):
        failures.append(f"UNROUTED_RULE_UNDECLARED {p}")
    for p in sorted(set(declared) - actual_unrouted):
        failures.append(f"STALE_KNOWN_GAP {p} (now routed or removed; delete entry)")
    for p in sorted(actual_unrouted & set(declared)):
        warnings.append(f"KNOWN_GAP {declared[p]['id']} {p}: {declared[p]['reason']}")

    # 6. Every tools/*.py must carry a declared role (production|audit).
    #    Production tools that no routing/rule doc mentions are warned (F15 class).
    tool_decl = {a["path"]: a for a in rows["gaps"]["tool_acks"]}
    tool_files = {f["path"] for f in rows["files"] if f["kind"] == "tool"}
    for p in sorted(tool_files - set(tool_decl)):
        failures.append(f"UNDECLARED_TOOL_ROLE {p}")
    for p in sorted(set(tool_decl) - tool_files):
        failures.append(f"STALE_TOOL_DECL {p}")
    doc_text = "\n".join(
        (ROOT / f["path"]).read_text(encoding="utf-8")
        for f in rows["files"]
        if f["kind"] in ("entry", "router", "rule", "schema") and not f["binary"]
    )
    for p in sorted(tool_files & set(tool_decl)):
        decl = tool_decl[p]
        if decl["role"] not in ("production", "audit"):
            failures.append(f"BAD_TOOL_ROLE {p}: {decl['role']}")
        elif decl["role"] == "production" and Path(p).name not in doc_text:
            warnings.append(f"PRODUCTION_TOOL_NOT_REFERENCED_BY_ROUTING_DOCS {p}")

    # 7. DB must match the disk state (stale-index detection).
    if DB_PATH.exists():
        con = sqlite3.connect(DB_PATH)
        db_files = {r[0]: r[1] for r in con.execute("SELECT path, sha256 FROM files")}
        con.close()
        disk_files = {f["path"]: f["sha256"] for f in rows["files"]}
        if db_files != disk_files:
            failures.append("STALE_INDEX: build/aicad.sqlite differs from disk; run build")
    else:
        warnings.append("NO_INDEX: run `python3 tools/aicad.py build`")

    by_kind, by_state = {}, {}
    for f in rows["files"]:
        by_kind[f["kind"]] = by_kind.get(f["kind"], 0) + 1
        if f["route_state"] != "n/a":
            by_state[f["route_state"]] = by_state.get(f["route_state"], 0) + 1
    report = {
        "status": "FAIL" if failures else "PASS",
        "files": len(rows["files"]),
        "chunks": len(rows["chunks"]),
        "files_by_kind": by_kind,
        "rule_route_state": by_state,
        "failures": failures,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


def _fts_query(q: str, mode: str) -> str | None:
    tokens = [t for t in re.split(r"\s+", q.strip()) if len(t) >= 3]
    if not tokens:
        return None
    quoted = ['"' + t.replace('"', '""') + '"' for t in tokens]
    return (" AND " if mode == "all" else " OR ").join(quoted)


def cmd_search(args) -> int:
    if not DB_PATH.exists():
        print("NO_INDEX: run `python3 tools/aicad.py build` first", file=sys.stderr)
        return 2
    con = sqlite3.connect(DB_PATH)
    scopes = ("default", "excluded") if args.include_excluded else ("default",)
    placeholders = ",".join("?" * len(scopes))
    match = _fts_query(args.query, args.mode)
    if match is None:
        rows = con.execute(
            f"""SELECT c.id, c.path, c.start_line, c.end_line, c.heading, f.route_state, 0.0
                FROM chunks c JOIN files f ON f.path = c.path
                WHERE f.scope IN ({placeholders}) AND instr(c.text, ?) > 0
                LIMIT ?""", (*scopes, args.query, args.k)).fetchall()
    else:
        rows = con.execute(
            f"""SELECT c.id, c.path, c.start_line, c.end_line, c.heading, f.route_state,
                       bm25(chunk_tri) AS score
                FROM chunk_tri JOIN chunks c ON c.id = chunk_tri.id
                JOIN files f ON f.path = c.path
                WHERE chunk_tri MATCH ? AND f.scope IN ({placeholders})
                ORDER BY score LIMIT ?""", (match, *scopes, args.k)).fetchall()
    con.close()
    hits = [{"id": r[0], "path": r[1], "lines": f"{r[2]}-{r[3]}", "heading": r[4],
             "route_state": r[5], "score": round(float(r[6]), 4)} for r in rows]
    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
    else:
        for h in hits:
            print(f"{h['id']}  [{h['route_state']}]  {h['heading']}")
        if not hits:
            print("NOT_FOUND")
    return 0


def cmd_rule(args) -> int:
    if not DB_PATH.exists():
        print("NO_INDEX: run `python3 tools/aicad.py build` first", file=sys.stderr)
        return 2
    con = sqlite3.connect(DB_PATH)
    if re.search(r":L\d+-\d+$", args.target):
        row = con.execute("SELECT id, text FROM chunks WHERE id = ?", (args.target,)).fetchone()
        rows = [row] if row else []
    else:
        rows = con.execute(
            "SELECT id, text FROM chunks WHERE path = ? ORDER BY start_line", (args.target,)
        ).fetchall()
    con.close()
    if not rows:
        print("NOT_FOUND")
        return 1
    for cid, text in rows:
        print(f"===== {cid}")
        print(text, end="" if text.endswith("\n") else "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(func=cmd_build)
    sub.add_parser("verify").set_defaults(func=cmd_verify)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=8)
    s.add_argument("--mode", choices=["any", "all"], default="any")
    s.add_argument("--include-excluded", action="store_true",
                   help="also search archive/qa_evidence/test/ci/service files")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)
    r = sub.add_parser("rule")
    r.add_argument("target", help="chunk id path:Lstart-end, or a file path")
    r.set_defaults(func=cmd_rule)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
