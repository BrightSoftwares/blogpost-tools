import base64
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "jekyll_fleet"))

from fleet_common import GitHub  # noqa: E402


class FakeAPI:
    """Route table transport: routes[(METHOD, path)] -> (status, json) or callable(body)->(status, json)."""

    def __init__(self, routes=None):
        self.routes = routes or {}
        self.calls = []

    def __call__(self, method, url, headers, data):
        path = url.replace("https://api.github.com", "")
        body = json.loads(data) if data else None
        self.calls.append((method, path, body))
        route = self.routes.get((method, path))
        if route is None:
            return 404, {}, b'{"message": "Not Found"}'
        result = route(body) if callable(route) else route
        status, payload = result[0], result[1]
        headers = result[2] if len(result) > 2 else {}
        return status, headers, json.dumps(payload).encode()

    def writes(self):
        return [c for c in self.calls if c[0] != "GET"]


def file_payload(text):
    return {"content": base64.b64encode(text.encode()).decode(), "sha": "sha-" + str(len(text))}


def make_gh(routes):
    api = FakeAPI(routes)
    return GitHub("test-token", transport=api), api
