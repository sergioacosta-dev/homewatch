# HomeWatch — Project Rules

Flask home network security monitor. Runs on **Homeserver**, not Omarchy — this local copy is for editing; the live instance is a separate, non-git deployment.

---

## Deploy Pattern (no git repo on Homeserver)

The live copy at `~/Projects/active/homewatch/` on Homeserver is a plain file deployment, not a git checkout. After editing locally:

```bash
scp app.py config.py db.py scanner.py alerts.py homeserver:/home/sergi/Projects/active/homewatch/
```

Then restart the systemd service — this needs `sudo`, which Claude can't run over SSH, so hand the exact command to the user:
```bash
sudo systemctl restart homewatch
```

Verify env vars are already set on the live `homewatch.env` before restarting if you touched `config.py`'s required-vars list — see below.

## Required Environment Variables

`config.py` fails fast (raises `RuntimeError`) if any of these are missing — this was a real gap fixed 2026-09-02 (they used to silently default to empty strings):

```
SECRET_KEY           # Flask session signing — generate: python3 -c "import secrets; print(secrets.token_hex(32))"
AUTH_USERNAME        # admin login
AUTH_PASSWORD_HASH   # werkzeug generate_password_hash() output
```

Optional (leave blank to disable that feature): `SMTP_FROM`, `SMTP_PASSWORD`, `ALERT_EMAIL_TO`, `NTFY_TOPIC`.

Loaded via systemd `EnvironmentFile=homewatch.env` (not python-dotenv) — see `homewatch.env.example` for the template. **`.gitignore` uses `*.env`, not `.env`** — the actual secrets file is named `homewatch.env`, not `.env`, and the old exact-match pattern never covered it (fixed 2026-09-02).

## Structure

- `app.py` — routes, `login_required` decorator, scan endpoints
- `config.py` — env var loading + validation, subnet, static nickname map
- `db.py` — SQLite access (`homewatch.db` — **never delete or overwrite, it's the live database**)
- `scanner.py` — `python-nmap`-based network scanning
- `alerts.py` — email/ntfy notification dispatch

## Auth

Session-based (`login_required` decorator on protected routes), single admin account via `AUTH_USERNAME`/`AUTH_PASSWORD_HASH`. No user registration flow — it's a single-operator tool.

---

## 7 Deadly Sins of Vibecoding

Verify all 7 before marking any task complete.

### 1. Safe Defaults
**Never ship permissive configs.** Production code must be locked down from the start.
- ❌ `CORS: *`, `DEBUG=True`, open firewall rules, world-readable file permissions, default admin credentials
- ✅ Allowlist specific origins, disable debug in prod, least-privilege on all configs and file permissions

### 2. Logging & Monitoring
**Silent code is blind code.** Every meaningful action and failure must leave a trace.
- ❌ Empty `except`/`catch` blocks, no request logging, swallowed errors, no alerting on failures
- ✅ Structured logs with severity levels, trace IDs on requests, log errors with context — never log secrets or PII

### 3. Dependency Hygiene
**Every package is a liability.** Vet before you install; pin what you keep.
- ❌ Unpinned versions (`requests`, `^1.0.0`), abandoned packages, unaudited installs, unnecessary dependencies
- ✅ Pin exact versions, run `pip audit` / `npm audit`, remove unused deps, prefer stdlib over micro-packages

### 4. Secrets
**A secret in code is already leaked.** Zero tolerance.
- ❌ Hardcoded API keys, passwords in source, `.env` committed to git, secrets appearing in logs or error messages
- ✅ Environment variables or a secrets manager, `.env` in `.gitignore`, startup validation that required secrets exist

### 5. Input Handling
**Never trust the caller.** Validate and sanitize at every system boundary.
- ❌ Raw user input passed to queries/shell/file paths, trusting client-side validation alone, no length limits
- ✅ Schema validation on entry, parameterized queries, path canonicalization, reject-early with clear error messages

### 6. Authentication
**Prove identity before anything else.** Use proven libraries — never roll your own.
- ❌ Unprotected endpoints, custom session token logic, plain-text password storage, no token expiry
- ✅ Established auth libraries (OAuth 2.0, JWT with short TTLs), bcrypt/argon2 for passwords, re-auth on sensitive actions

### 7. Authorization
**Authentication ≠ Authorization.** Verify permissions at every layer, default to deny.
- ❌ Checking auth but not ownership (IDOR), admin logic gated only on the frontend, assuming logged-in = permitted
- ✅ Server-side permission checks on every action, resource ownership validated, least-privilege roles, deny by default

---

### Pre-Completion Checklist

Before marking any task done:
- [ ] **Safe defaults** — no permissive configs shipped
- [ ] **Logging** — errors and key actions are logged; no secrets in logs
- [ ] **Dependencies** — all new packages vetted, pinned, and necessary
- [ ] **Secrets** — zero hardcoded credentials; `.env` excluded from git
- [ ] **Input handling** — all external input validated at the boundary
- [ ] **Authentication** — all endpoints that need auth have it
- [ ] **Authorization** — permission checks happen server-side, deny by default
