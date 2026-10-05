"""Shared helpers for the Jekyll fleet tools (stdlib only, HTTP injectable for tests).

The token is read from the environment (GITHUB_TOKEN or GH_TOKEN) and never printed.
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from typing import Callable, Iterator

API = "https://api.github.com"
SEVERITIES = ("critical", "high", "medium", "low")

# transport(method, url, headers, data) -> (status, response_headers, body_bytes)
Transport = Callable[[str, str, dict, "bytes | None"], "tuple[int, dict, bytes]"]


def urllib_transport(method: str, url: str, headers: dict, data: "bytes | None"):
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers or {}), err.read()


class GitHubError(RuntimeError):
    def __init__(self, status: int, path: str):
        super().__init__(f"GitHub API {status} for {path}")
        self.status = status


class GitHub:
    def __init__(self, token: str, transport: Transport = urllib_transport, base: str = API):
        if not token:
            raise ValueError("a GitHub token is required (set GITHUB_TOKEN)")
        self._token = token
        self._transport = transport
        self._base = base

    @classmethod
    def from_env(cls, transport: Transport = urllib_transport) -> "GitHub":
        return cls(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "", transport)

    def request(self, method: str, path: str, body=None):
        """Return (status, parsed_json_or_None, headers)."""
        url = path if path.startswith("http") else self._base + path
        headers = {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "blogpost-tools-jekyll-fleet",
        }
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        status, resp_headers, raw = self._transport(method, url, headers, data)
        try:
            parsed = json.loads(raw) if raw else None
        except ValueError:
            parsed = None
        return status, parsed, resp_headers

    def get(self, path: str):
        status, data, _ = self.request("GET", path)
        return status, data

    def paginate(self, path: str, max_pages: int = 50) -> Iterator[dict]:
        """Follow `Link: rel="next"` (cursor-safe: the Dependabot alerts API rejects `page=`)."""
        sep = "&" if "?" in path else "?"
        url = f"{path}{sep}per_page=100"
        for _ in range(max_pages):
            status, data, headers = self.request("GET", url)
            if status != 200 or not isinstance(data, (list, type(None))):
                # Never swallow an error page: a silent empty result reads as "0 findings".
                raise GitHubError(status, path)
            yield from data or []
            link = {k.lower(): v for k, v in headers.items()}.get("link", "")
            m = re.search(r'<([^>]+)>;\s*rel="next"', link)
            if not m:
                return
            url = m.group(1)

    def file_text(self, repo: str, path: str, ref: str | None = None):
        """Return (status, text|None, sha|None) for a file via the contents API."""
        q = f"?ref={ref}" if ref else ""
        status, data = self.get(f"/repos/{repo}/contents/{path}{q}")
        if status == 200 and isinstance(data, dict) and "content" in data:
            return status, base64.b64decode(data["content"]).decode("utf-8", "replace"), data.get("sha")
        return status, None, None


def parse_repo_list(text: str) -> "list[tuple[str, str | None]]":
    """Lines of `owner/repo [branch]`; `#` starts a comment; blanks ignored."""
    out = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", parts[0]):
            raise ValueError(f"invalid repo entry: {line!r}")
        out.append((parts[0], parts[1] if len(parts) > 1 else None))
    return out


def default_branch(gh: GitHub, repo: str) -> "str | None":
    status, data = gh.get(f"/repos/{repo}")
    return data.get("default_branch") if status == 200 and data else None
