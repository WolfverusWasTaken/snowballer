"""Create, validate, register, search, and serve Snowballer research reports."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit

SKILL_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = Path(os.environ.get("SNOWBALLER_REGISTRY", Path.home() / ".codex" / "snowballer" / "reports.json"))
REQUIRED = {"id", "title", "year", "kind", "description", "what_it_does", "pros", "cons", "tags", "novelty", "core_discovery", "past_work", "related_work", "folder_path", "sources"}
SUMMARY = ("id", "title", "year", "kind", "description", "what_it_does", "tags", "core_discovery", "past_work", "related_work", "folder_path")


def registry_items() -> list[dict]:
    if not REGISTRY.exists():
        return []
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Registry must be a list: {REGISTRY}")
    return data


def save_registry(items: list[dict]) -> None:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    temp = REGISTRY.with_suffix(".tmp")
    temp.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(REGISTRY)


def report_id(root: Path) -> str:
    slug = "".join(c.lower() if c.isalnum() else "-" for c in root.name).strip("-") or "report"
    digest = hashlib.sha256(str(root).casefold().encode()).hexdigest()[:8]
    return f"{slug[:40]}-{digest}"


def register(root: Path, title: str, logo: Path | None = None) -> dict:
    root = root.resolve()
    if not (root / "ideas").is_dir():
        raise ValueError(f"Missing ideas directory: {root / 'ideas'}")
    if logo is not None:
        logo = logo.resolve()
        if not logo.is_file() or logo.suffix.lower() not in {".png", ".jpg", ".jpeg", ".svg", ".webp"}:
            raise ValueError(f"Logo must be an image file: {logo}")
    record = {"id": report_id(root), "title": title, "root": str(root)}
    if logo:
        record["logo"] = str(logo)
    items = [x for x in registry_items() if Path(x["root"]).resolve() != root]
    items.append(record)
    save_registry(items)
    return record


def read_ideas(root: Path) -> list[dict]:
    root = root.resolve()
    items = []
    for path in sorted((root / "ideas").glob("*/idea.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = REQUIRED - set(data)
        if missing:
            raise ValueError(f"{path}: missing {sorted(missing)}")
        if data["id"] != path.parent.name or data["folder_path"] != path.parent.relative_to(root).as_posix():
            raise ValueError(f"{path}: ID or folder_path mismatch")
        if not (path.parent / "README.md").is_file():
            raise ValueError(f"{path}: missing README.md")
        if not 10 <= len(data["novelty"].replace("-", " ").split()) <= 15:
            raise ValueError(f"{path}: novelty must be 10-15 words")
        if not data["sources"] or not all(isinstance(url, str) and url.startswith("https://") for url in data["sources"]):
            raise ValueError(f"{path}: HTTPS primary sources required")
        items.append(data)
    by_id = {x["id"]: x for x in items}
    if len(by_id) != len(items):
        raise ValueError("Duplicate idea IDs")
    for item in items:
        for field in ("past_work", "related_work"):
            unknown = set(item[field]) - set(by_id)
            if unknown or item["id"] in item[field]:
                raise ValueError(f"{item['id']}: invalid {field}: {sorted(unknown)}")
        for predecessor in item["past_work"]:
            if by_id[predecessor]["year"] > item["year"]:
                raise ValueError(f"{item['id']}: future idea in past_work: {predecessor}")
    return items


def build(root: Path) -> int:
    root = root.resolve()
    ideas = read_ideas(root)
    (root / "master.json").write_text(json.dumps({"schema_version": 1, "count": len(ideas), "ideas": ideas}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(ideas)


def visible_reports() -> list[dict]:
    result = []
    for item in registry_items():
        root = Path(item["root"])
        if (root / "ideas").is_dir():
            result.append({"id": item["id"], "title": item["title"], "has_logo": bool(item.get("logo"))})
    return result


def find_report(identifier: str) -> dict | None:
    return next((x for x in registry_items() if x["id"] == identifier and (Path(x["root"]) / "ideas").is_dir()), None)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        # Keep a detached local server responsive if its launching terminal closes.
        pass

    def send_data(self, body: bytes, mime: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, value: object, status: int = 200) -> None:
        self.send_data(json.dumps(value, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self) -> None:
        try:
            self.route()
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, 400)

    def route(self) -> None:
        parsed = urlsplit(self.path)
        path = unquote(parsed.path)
        if path in {"/", "/index.html"}:
            self.send_data((SKILL_ROOT / "assets" / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if path == "/api/reports":
            self.send_json(visible_reports())
            return
        parts = path.strip("/").split("/")
        if len(parts) < 3 or parts[:2] != ["api", "reports"]:
            self.send_json({"error": "Not found"}, 404)
            return
        report = find_report(parts[2])
        if not report:
            self.send_json({"error": "Unknown report"}, 404)
            return
        root = Path(report["root"]).resolve()
        if len(parts) == 4 and parts[3] == "ideas":
            self.send_json({"ideas": [{k: x[k] for k in SUMMARY} for x in read_ideas(root)]})
            return
        if len(parts) == 5 and parts[3] == "ideas":
            item = next((x for x in read_ideas(root) if x["id"] == parts[4]), None)
            self.send_json(item if item else {"error": "Unknown idea"}, 200 if item else 404)
            return
        if len(parts) == 4 and parts[3] == "search":
            query = parse_qs(parsed.query)
            words = query.get("q", [""])[0].casefold().split()
            year = query.get("year", [""])[0]
            tag = query.get("tag", [""])[0]
            found = []
            for x in read_ideas(root):
                haystack = " ".join(str(x[k]) for k in ("id", "title", "description", "what_it_does", "core_discovery", "tags")).casefold()
                if all(word in haystack for word in words) and (not year or str(x["year"]) == year) and (not tag or tag in x["tags"]):
                    found.append({k: x[k] for k in SUMMARY})
            self.send_json({"count": len(found), "ideas": found})
            return
        if len(parts) == 4 and parts[3] == "logo" and report.get("logo"):
            logo = Path(report["logo"])
            mime = {".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}[logo.suffix.lower()]
            self.send_data(logo.read_bytes(), mime)
            return
        if len(parts) >= 5 and parts[3] == "files":
            target = (root / "/".join(parts[4:])).resolve()
            if not target.is_relative_to(root) or not target.is_file() or target.suffix.lower() not in {".md", ".pdf", ".txt", ".png", ".jpg", ".jpeg", ".svg", ".webp"}:
                self.send_json({"error": "File not found"}, 404)
                return
            mime = {".md": "text/markdown; charset=utf-8", ".txt": "text/plain; charset=utf-8", ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml", ".webp": "image/webp"}[target.suffix.lower()]
            self.send_data(target.read_bytes(), mime)
            return
        self.send_json({"error": "Not found"}, 404)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create and register a new report folder")
    init.add_argument("--root", type=Path, required=True)
    init.add_argument("--title", required=True)
    init.add_argument("--logo", type=Path)
    reg = sub.add_parser("register", help="Register an existing report")
    reg.add_argument("--root", type=Path, required=True)
    reg.add_argument("--title", required=True)
    reg.add_argument("--logo", type=Path)
    bld = sub.add_parser("build", help="Validate idea folders and rebuild master.json")
    bld.add_argument("--root", type=Path, required=True)
    sub.add_parser("list", help="List registered reports")
    serve = sub.add_parser("serve", help="Run the shared local browser")
    serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "init":
        root = args.root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        (root / "ideas").mkdir(exist_ok=True)
        if not (root / "README.md").exists():
            (root / "README.md").write_text(f"# {args.title}\n\nResearch brief and evolving synthesis.\n", encoding="utf-8")
        print(json.dumps(register(root, args.title, args.logo), ensure_ascii=False))
    elif args.command == "register":
        print(json.dumps(register(args.root, args.title, args.logo), ensure_ascii=False))
    elif args.command == "build":
        print(f"Validated {build(args.root)} linked ideas")
    elif args.command == "list":
        print(json.dumps(visible_reports(), ensure_ascii=False, indent=2))
    elif args.command == "serve":
        print(f"Snowballer: http://localhost:{args.port}/", flush=True)
        ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
