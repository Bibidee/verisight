"""Mark every existing Supabase Auth user as email-confirmed.

Run once: python scripts/confirm_all_users.py
"""
import os
import sys
import urllib.request
import urllib.error
import json
from pathlib import Path

# load .env.local
env_path = Path(__file__).resolve().parent.parent / ".env.local"
env = {}
for line in env_path.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()

URL = env["NEXT_PUBLIC_SUPABASE_URL"].rstrip("/")
KEY = env["SUPABASE_SERVICE_ROLE_KEY"]
HDRS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def req(method: str, path: str, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(f"{URL}{path}", method=method, headers=HDRS, data=data)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:200]}")
        return None


page = 1
total = 0
while True:
    res = req("GET", f"/auth/v1/admin/users?page={page}&per_page=200")
    if not res or not res.get("users"):
        break
    for u in res["users"]:
        if u.get("email_confirmed_at"):
            continue
        out = req("PUT", f"/auth/v1/admin/users/{u['id']}", {"email_confirm": True})
        if out is not None:
            print(f"  confirmed {u['email']}")
            total += 1
    if len(res["users"]) < 200:
        break
    page += 1

print(f"\nConfirmed {total} user(s).")
