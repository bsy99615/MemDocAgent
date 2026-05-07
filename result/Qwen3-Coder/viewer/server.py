#!/usr/bin/env python3
"""Documentation viewer server for Qwen3-Coder output."""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).parent.parent
VIEWER_DIR = Path(__file__).parent


def build_tree(root: Path, rel_root: Path = None) -> dict:
    """Build a nested tree structure from the directory."""
    if rel_root is None:
        rel_root = root

    node = {
        "name": root.name,
        "path": str(root.relative_to(BASE_DIR)),
        "type": "directory",
        "children": [],
    }

    try:
        entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        return node

    for entry in entries:
        if entry.is_dir():
            child = build_tree(entry, rel_root)
            if child["children"] or any(entry.rglob("*.md")):
                node["children"].append(child)
        elif entry.is_file() and entry.suffix == ".md":
            node["children"].append({
                "name": entry.name,
                "path": str(entry.relative_to(BASE_DIR)),
                "type": "file",
            })

    return node


def get_doc_tree() -> list:
    """Return list of stage-level trees."""
    trees = []
    for stage_dir in sorted(BASE_DIR.iterdir()):
        if stage_dir.is_dir() and stage_dir.name.startswith("stage") and stage_dir.name != "viewer":
            trees.append(build_tree(stage_dir))
    return trees


class Handler(BaseHTTPRequestHandler):
    _tree_cache = None

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text, content_type="text/plain; charset=utf-8", status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html_file(self, filepath: Path):
        content = filepath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_html_file(VIEWER_DIR / "index.html")

        elif path == "/api/tree":
            if Handler._tree_cache is None:
                Handler._tree_cache = get_doc_tree()
            self.send_json(Handler._tree_cache)

        elif path == "/api/file":
            rel = qs.get("path", [""])[0]
            if not rel:
                self.send_json({"error": "path required"}, 400)
                return

            # Security: resolve and ensure inside BASE_DIR
            target = (BASE_DIR / rel).resolve()
            if not str(target).startswith(str(BASE_DIR.resolve())):
                self.send_json({"error": "forbidden"}, 403)
                return
            if not target.exists() or not target.is_file():
                self.send_json({"error": "not found"}, 404)
                return

            self.send_text(target.read_text(encoding="utf-8", errors="replace"))

        else:
            self.send_json({"error": "not found"}, 404)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"Documentation viewer running at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
