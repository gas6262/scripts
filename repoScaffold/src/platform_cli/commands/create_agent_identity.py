"""platform-cli create-agent-identity — give a project's agent its own GitHub App.

Automates the whole GitHub App manifest flow so each scaffolded project gets its
own scoped bot identity (`<name>[bot]`) instead of borrowing a human's token:

  1. serve a pre-filled App manifest locally + open the browser
  2. you click "Create GitHub App" (the one consent GitHub requires)
  3. capture the redirect code, exchange it for the App id + private key
  4. store the private key in the project's Secret Manager
  5. open the install page + wait until the App is installed on the repo
  6. resolve the installation id + bot commit identity and print the wiring

The printed values (app_id, installation_id, bot_name, bot_email) go straight
into the generated agents/loop.sh (see the loop template's App-auth block).
"""
from __future__ import annotations

import http.server
import json
import socketserver
import subprocess
import tempfile
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import click
from rich.console import Console

console = Console()
PORT = 8722
_captured = {"code": None}


def _b64url(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _app_jwt(app_id: str, pem: str) -> str:
    """Sign an RS256 App JWT using openssl (no extra Python crypto dep)."""
    now = int(time.time())
    header = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    payload = _b64url(json.dumps({"iat": now - 60, "exp": now + 540, "iss": app_id}).encode())
    signing_input = f"{header}.{payload}".encode()
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as f:
        f.write(pem)
        key_path = f.name
    try:
        sig = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", key_path],
            input=signing_input, capture_output=True, check=True,
        ).stdout
    finally:
        Path(key_path).unlink(missing_ok=True)
    return f"{header}.{payload}.{_b64url(sig)}"


def _gh(url: str, token: str, bearer: bool = False, method: str = "GET", body: dict | None = None) -> dict:
    auth = f"Bearer {token}" if bearer else f"token {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": auth, "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "platform-cli",
    })
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def _serve_manifest(manifest: dict) -> threading.Thread:
    form = (
        "<!doctype html><body style='font-family:system-ui;max-width:640px;margin:60px auto'>"
        "<h2>Create the agent GitHub App</h2>"
        "<p>Clicking below sends a pre-filled manifest to GitHub "
        "(name + Contents/Pull-requests write already set). Review and click "
        "<b>Create GitHub App</b>.</p>"
        "<form action='https://github.com/settings/apps/new?state=platform-cli' method='post'>"
        f"<input type='hidden' name='manifest' value='{json.dumps(manifest).replace(chr(39), '&#39;')}'>"
        "<button type='submit' style='padding:12px 20px;font-size:16px'>Create the agent GitHub App &rarr;</button>"
        "</form></body>"
    )

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/created":
                code = urllib.parse.parse_qs(parsed.query).get("code", [""])[0]
                _captured["code"] = code
                msg = b"<h2>App created. Return to your terminal.</h2>"
            else:
                msg = form.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(msg)

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), H)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    t.httpd = httpd  # type: ignore
    return t


@click.command("create-agent-identity")
@click.option("--project", required=True, help="GCP project holding the agent's secrets.")
@click.option("--repo", required=True, help="GitHub repo as owner/name.")
@click.option("--name", default=None, help="App name (default: <repo-name>-agent).")
@click.option("--secret", default="github-app-private-key", help="Secret Manager name for the App private key.")
def create_agent_identity(project: str, repo: str, name: str | None, secret: str) -> None:
    """Create + install a per-project GitHub App bot for the agent."""
    owner, repo_name = repo.split("/", 1)
    app_name = name or f"{repo_name}-agent"
    manifest = {
        "name": app_name,
        "url": f"https://github.com/{owner}",
        "hook_attributes": {"url": "https://example.com/unused", "active": False},
        "redirect_url": f"http://localhost:{PORT}/created",
        "public": False,
        "default_permissions": {"contents": "write", "pull_requests": "write", "metadata": "read"},
        "default_events": [],
    }

    server = _serve_manifest(manifest)
    url = f"http://localhost:{PORT}/"
    console.print(f"\n[bold]Opening[/bold] {url} — click [bold]Create GitHub App[/bold] (rename if you like).")
    webbrowser.open(url)

    console.print("  [dim]waiting for you to create the App…[/dim]")
    while not _captured["code"]:
        time.sleep(1)
    server.httpd.shutdown()  # type: ignore

    # Exchange the manifest code for the App credentials.
    conv = _gh(f"https://api.github.com/app-manifests/{_captured['code']}/conversions",
               token="", method="POST")
    app_id, slug, pem = str(conv["id"]), conv["slug"], conv["pem"]
    console.print(f"  [green]created[/green] App {slug} (id {app_id})")

    # Store the private key in Secret Manager.
    if not subprocess.run(["gcloud", "secrets", "describe", secret, f"--project={project}"],
                          capture_output=True).returncode == 0:
        subprocess.run(["gcloud", "secrets", "create", secret, f"--project={project}",
                        "--replication-policy=automatic"], check=True, capture_output=True)
    subprocess.run(["gcloud", "secrets", "versions", "add", secret, f"--project={project}",
                    "--data-file=-"], input=pem.encode(), check=True, capture_output=True)
    console.print(f"  [green]stored[/green] private key in Secret Manager: {secret}")

    # Install + wait for it.
    install_url = f"https://github.com/apps/{slug}/installations/new"
    console.print(f"\n  [bold]Opening[/bold] {install_url} — install on [bold]{repo}[/bold] (Only select repositories).")
    webbrowser.open(install_url)
    console.print("  [dim]waiting for the install…[/dim]")
    install_id = None
    while not install_id:
        time.sleep(2)
        jwt = _app_jwt(app_id, pem)
        for inst in _gh("https://api.github.com/app/installations", jwt, bearer=True):
            install_id = inst["id"]
            break

    bot = _gh(f"https://api.github.com/users/{slug}%5Bbot%5D", _app_jwt(app_id, pem), bearer=True)
    bot_name = f"{slug}[bot]"
    bot_email = f"{bot['id']}+{slug}[bot]@users.noreply.github.com"

    console.print("\n[bold green]Agent identity ready.[/bold green] Wire these into agents/loop.sh:")
    console.print(f"  GITHUB_APP_ID=\"{app_id}\"")
    console.print(f"  GITHUB_APP_INSTALLATION_ID=\"{install_id}\"")
    console.print(f"  GITHUB_BOT_NAME=\"{bot_name}\"")
    console.print(f"  GITHUB_BOT_EMAIL=\"{bot_email}\"")
