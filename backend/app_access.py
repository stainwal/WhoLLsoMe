"""Database access for the web app, and the secrets the deployed site needs (Day 22, 16 Nov 2026).

    .venv/bin/python backend/app_access.py apply     # apply backend/app.sql (safe to re-run)
    .venv/bin/python backend/app_access.py secrets   # create any missing app secrets in .env; prints names only
    .venv/bin/python backend/app_access.py rotate NAME   # replace one generated secret (APP_DATABASE_URL,
                                                         # VISITOR_SALT or ACCESS_CODE)
    .venv/bin/python backend/app_access.py vercel    # write .env.vercel: exactly the variables Vercel needs

Generated secrets go straight into .env (git-ignored) and are never printed:
  APP_DATABASE_URL  the whollsome_app login (backend/app.sql), through Supabase's transaction pooler
  VISITOR_SALT      salts the hashed visitor key used for rate limits
  ACCESS_CODE       lets Shailesh and testers past the holding page until launch
.env.vercel is git-ignored too; its contents can be pasted into Vercel's environment variable form.
"""

import base64
import hashlib
import hmac
import re
import secrets
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load  # noqa: E402

ROOT = load.ROOT
ENV = ROOT / ".env"
VERCEL = ROOT / ".env.vercel"
GENERATED = ("APP_DATABASE_URL", "VISITOR_SALT", "ACCESS_CODE")
# Copied from .env into .env.vercel, in this order. SITE_GATE is not a secret: "on" until launch.
FOR_VERCEL = ("ANTHROPIC_API_KEY", "VOYAGE_API_KEY", "APP_DATABASE_URL", "VISITOR_SALT", "ACCESS_CODE", "SITE_GATE")
CODE_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"  # no 0/o, 1/l/i: easy to read out to a tester


def read_env():
    out = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Z0-9_]+)=(.*)$", line)
        if m:
            out[m[1]] = m[2]
    return out


def set_env(name, value):
    lines = ENV.read_text(encoding="utf-8").splitlines()
    new = f"{name}={value}"
    for i, line in enumerate(lines):
        if line.startswith(f"{name}="):
            lines[i] = new
            break
    else:
        lines.append(new)
    ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply():
    with load.connect() as db:
        db.execute((ROOT / "backend" / "app.sql").read_text(encoding="utf-8"))
    print("backend/app.sql applied")


def scram(password, iterations=4096):
    """Postgres SCRAM-SHA-256 verifier (RFC 5802/7677), the form Postgres stores passwords in."""
    salt = secrets.token_bytes(16)
    salted = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    client_key = hmac.new(salted, b"Client Key", "sha256").digest()
    server_key = hmac.new(salted, b"Server Key", "sha256").digest()
    b64 = lambda b: base64.b64encode(b).decode()
    return f"SCRAM-SHA-256${iterations}:{b64(salt)}${b64(hashlib.sha256(client_key).digest())}:{b64(server_key)}"


def app_database_url():
    """A new password for whollsome_app, and its connection URL on the transaction pooler (port 6543)."""
    password = secrets.token_urlsafe(32)
    admin = urlsplit(read_env()["DATABASE_URL"])
    # Supabase's pooler names users "<role>.<project ref>"; the admin URL carries the project ref.
    ref = admin.username.split(".", 1)[1]
    with load.connect() as db:
        # Sent pre-hashed, so the plain password never reaches the database or its statement logs.
        db.execute(f"alter role whollsome_app with login password '{scram(password)}'")
    return f"postgresql://whollsome_app.{ref}:{quote(password)}@{admin.hostname}:6543{admin.path or '/postgres'}"


def generate(name):
    if name == "APP_DATABASE_URL":
        return app_database_url()
    if name == "VISITOR_SALT":
        return secrets.token_hex(32)
    if name == "ACCESS_CODE":
        return "-".join("".join(secrets.choice(CODE_ALPHABET) for _ in range(4)) for _ in range(3))
    sys.exit(f"not a generated secret: {name}")


def ensure_secrets():
    env = read_env()
    for name in GENERATED:
        if env.get(name):
            print(f"{name}: already in .env (unchanged)")
        else:
            set_env(name, generate(name))
            print(f"{name}: created in .env")
    if not env.get("SITE_GATE"):
        set_env("SITE_GATE", "on")
        print("SITE_GATE: set to on in .env")


def rotate(name):
    set_env(name, generate(name))
    print(f"{name}: replaced in .env (old value no longer works{' after the next deploy' if name != 'APP_DATABASE_URL' else ''})")


def vercel():
    env = read_env()
    missing = [n for n in FOR_VERCEL if not env.get(n)]
    if missing:
        sys.exit(f"missing in .env: {', '.join(missing)} (run `secrets` first)")
    VERCEL.write_text("".join(f"{n}={env[n]}\n" for n in FOR_VERCEL), encoding="utf-8")
    VERCEL.chmod(0o600)
    print(f"wrote {VERCEL.relative_to(ROOT)}: {', '.join(FOR_VERCEL)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "apply":
        apply()
    elif cmd == "secrets":
        ensure_secrets()
    elif cmd == "rotate" and len(sys.argv) == 3:
        rotate(sys.argv[2])
    elif cmd == "vercel":
        vercel()
    else:
        sys.exit(__doc__)
