#!/usr/bin/env bash
# Mint a short-lived GitHub App installation access token (valid ~1h).
#
# The agent authenticates to GitHub as the App's bot identity
# (`<app-slug>[bot]`) instead of a human's personal token, so its commits and
# comments are clearly attributable and its access is scoped to just the
# installed repo(s) with fine-grained permissions.
#
# Usage: github-app-token.sh <gcp-project> <app-id> <installation-id>
#   - the App private key (PEM) is read from Secret Manager (github-app-private-key)
#   - prints the installation token to stdout (nothing else)
#
# Deps: openssl + curl + python3 (all present on the agent VM). No JWT library.
set -euo pipefail

PROJECT_ID="${1:?usage: github-app-token.sh <gcp-project> <app-id> <installation-id>}"
APP_ID="${2:?app id required}"
INSTALLATION_ID="${3:?installation id required}"
PRIVATE_KEY_SECRET="${GITHUB_APP_KEY_SECRET:-github-app-private-key}"

pem="$(gcloud secrets versions access latest --secret="$PRIVATE_KEY_SECRET" --project="$PROJECT_ID")"

# base64url without padding
b64url() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }

now="$(date +%s)"
# iat backdated 60s to tolerate clock skew; exp within the 10-min max.
header="$(printf '{"alg":"RS256","typ":"JWT"}' | b64url)"
payload="$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' "$((now - 60))" "$((now + 540))" "$APP_ID" | b64url)"
signature="$(printf '%s.%s' "$header" "$payload" \
  | openssl dgst -sha256 -sign <(printf '%s' "$pem") | b64url)"
jwt="${header}.${payload}.${signature}"

# Exchange the App JWT for an installation access token.
curl -sf -X POST \
  -H "Authorization: Bearer ${jwt}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])'
