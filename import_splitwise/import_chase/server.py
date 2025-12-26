import os
import sys
import json
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import secrets
import requests

#!/usr/bin/env python3
"""
Simple OAuth2 authorization-code flow to get a bearer token from Splitwise.

Usage:
    - Set SPLITWISE_CONSUMER_KEY and SPLITWISE_CONSUMER_SECRET environment variables
        or run and enter them when prompted.
    - Run this script. It will open your browser to authorize and capture the callback.
    - The token response is printed and saved to token.json.

Requires: requests
        pip install requests
"""

import urllib.parse
# Get current file location
CUR_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Config
AUTHORIZE_URL = "https://secure.splitwise.com/oauth/authorize"
TOKEN_URL = "https://secure.splitwise.com/oauth/token"
LISTEN_PORT = 8000
REDIRECT_PATH = "/callback"
TOKEN_FILE = os.path.join(CUR_SCRIPT_DIR, "token.json")
CONSUMER_FILE = "consumer_oauth.json"

# Try to load consumer key/secret from file first
CLIENT_ID = ""
CLIENT_SECRET = ""

consumer_file_path = os.path.join(os.path.dirname(__file__), CONSUMER_FILE)
if os.path.exists(consumer_file_path):
        try:
                with open(consumer_file_path, 'r') as f:
                        consumer_data = json.load(f)
                        CLIENT_ID = consumer_data.get("consumer_key", "")
                        CLIENT_SECRET = consumer_data.get("consumer_secret", "")
        except Exception as e:
                print(f"Warning: Could not read {CONSUMER_FILE}: {e}")

# Fall back to environment variables if not loaded from file
if not CLIENT_ID:
        CLIENT_ID = os.getenv("SPLITWISE_CONSUMER_KEY") or ""
if not CLIENT_SECRET:
        CLIENT_SECRET = os.getenv("SPLITWISE_CONSUMER_SECRET") or ""

# Prompt user if still not set
if not CLIENT_ID:
        CLIENT_ID = input("SPLITWISE_CONSUMER_KEY: ").strip()
if not CLIENT_SECRET:
        CLIENT_SECRET = input("SPLITWISE_CONSUMER_SECRET: ").strip()

redirect_uri = f"http://localhost:{LISTEN_PORT}{REDIRECT_PATH}"
state = secrets.token_urlsafe(16)


def build_authorize_url():
        params = {
                "response_type": "code",
                "client_id": CLIENT_ID,
                "redirect_uri": redirect_uri,
                "state": state,
                # add scope if needed, e.g. "profile"
        }
        return AUTHORIZE_URL + "?" + urllib.parse.urlencode(params)


class OAuthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                
                # New endpoint to trigger OAuth flow
                if parsed.path == "/refresh":
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        auth_url = build_authorize_url()
                        response = {"auth_url": auth_url}
                        self.wfile.write(json.dumps(response).encode())
                        return
                
                if parsed.path != REDIRECT_PATH:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b"Not found")
                        return

                qs = urllib.parse.parse_qs(parsed.query)
                received_state = qs.get("state", [""])[0]
                code = qs.get("code", [""])[0]

                if received_state != state or not code:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b"Missing or invalid code/state")
                        # stop server after response
                        threading.Thread(target=self.server.shutdown, daemon=True).start()
                        return

                # Exchange code for token
                try:
                        data = {
                                "grant_type": "authorization_code",
                                "code": code,
                                "client_id": CLIENT_ID,
                                "client_secret": CLIENT_SECRET,
                                "redirect_uri": redirect_uri,
                        }
                        headers = {"Accept": "application/json"}
                        resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=10)
                        resp.raise_for_status()
                        token_json = resp.json()
                except Exception as e:
                        self.send_response(500)
                        self.end_headers()
                        msg = f"Token exchange failed: {e}"
                        self.wfile.write(msg.encode())
                        threading.Thread(target=self.server.shutdown, daemon=True).start()
                        return

                # Save token and respond to browser
                try:
                        with open(TOKEN_FILE, "w") as f:
                                json.dump(token_json, f, indent=2)
                except Exception:
                        pass

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<html><body><h2>Authorization complete</h2><p>You can close this window.</p></body></html>")

                # Print token to stdout and shutdown server
                print("Token response:")
                print(json.dumps(token_json, indent=2))
                threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, format, *args):
                # silence default logging except errors
                return


def run_server():
        server_address = ("", LISTEN_PORT)
        httpd = HTTPServer(server_address, OAuthHandler)
        print(f"Listening on http://localhost:{LISTEN_PORT}{REDIRECT_PATH} for the OAuth callback...")
        try:
                httpd.serve_forever()
        except KeyboardInterrupt:
                pass
        finally:
                httpd.server_close()


if __name__ == "__main__":
        auth_url = build_authorize_url()
        print("Opening browser for authorization...")
        print("If it does not open automatically, visit this URL:")
        print(auth_url)
        try:
                webbrowser.open(auth_url)
        except Exception:
                pass

        run_server()
        print(f"Done. Token saved to {TOKEN_FILE} (if exchange succeeded).")