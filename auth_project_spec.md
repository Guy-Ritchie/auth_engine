# AuthEngine — Project Specification & Learning Roadmap

> **Tagline:** A from-first-principles implementation of Authentication & Authorization mechanisms in Python 3.13, built to understand — not just use.
>
> **Repo:** `auth_engine` | **Package:** `auth_engine` | **Python:** 3.13 via `uv`

---

## 0. What This Is (and What It Isn't)

This project is a **deliberate learning vehicle** disguised as a web application.

The web app itself — a minimal HTML login page that routes users to one of two pages based on role — is the *pretext*, not the point. The point is to build every authentication and authorization mechanism from scratch, in increasing sophistication, in a production-quality Python codebase, so that by the end you don't just know *how* to use JWT or OAuth2 — you know *why* they exist, *what problem* each solves, and *what breaks* when they're absent or misused.

**What this is not:**
- A production-ready auth library (use `python-jose`, `passlib`, `authlib` for that)
- A project that reaches for `flask-login` or `fastapi-users` and calls it a day

---

## 1. Non-Negotiables (invariants across every phase)

### 1.1 Code Quality

| Concern | Tool | Config location |
|---|---|---|
| Linting + style + import order | `ruff` | `pyproject.toml → [tool.ruff]` |
| Type checking | `mypy` | `pyproject.toml → [tool.mypy]` |
| Secret scanning | `detect-secrets` | `.secrets.baseline` |
| Pre-commit enforcement | `pre-commit` | `.pre-commit-config.yaml` |
| Test runner | `pytest` | `pyproject.toml → [tool.pytest.ini_options]` |
| Coverage | `pytest-cov` | same |

**Ruff rule sets enabled:**

| Ruleset | Code | What it enforces |
|---|---|---|
| pycodestyle | `E`, `W` | formatting, whitespace, line length |
| pyflakes | `F` | undefined names, unused imports |
| pep8-naming | `N` | naming conventions (see below) |
| mccabe | `C90` | cyclomatic complexity ≤ 10 per function |
| pydocstyle | `D` | Google-convention docstrings |
| annotations | `ANN` | type hints on all function signatures |
| bandit | `S` | security anti-patterns |
| simplify | `SIM` | redundant constructs |
| pyupgrade | `UP` | modern Python 3.13 syntax |
| isort | `I` | import ordering (stdlib → third-party → local) |
| tidy-imports | `TID` | `TID252` bans relative imports |

**Naming conventions (enforced via N-rules):**

| Construct | Convention | Example |
|---|---|---|
| Classes | `PascalCase` | `PasswordAuthenticator` |
| Functions / methods | `snake_case` | `verify_credentials` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_LOGIN_ATTEMPTS` |
| Private members | `_leading_underscore` | `_hash_password` |
| Type variables | `T` or `PascalCaseT` | `T`, `UserT`, `EntityT` |
| Modules / packages | `snake_case` | `auth_engine.crypto.hashing` |

### 1.2 Import Convention

**Absolute imports only, everywhere.** No relative imports.

```python
# Correct
from auth_engine.crypto.hashing import hash_password

# Wrong — banned by ruff TID252
from .hashing import hash_password
from ..domain.user import User
```

Why: absolute imports make the dependency graph explicit at a glance. You always know exactly where a symbol comes from without counting dots.

### 1.3 `__init__.py` Convention

Every package directory has an `__init__.py`. It serves two purposes:

1. Makes the directory a proper Python package (required for absolute imports to resolve correctly with the src layout)
2. Defines the **public API** of that package — what's importable from the outside

```python
# src/auth_engine/crypto/__init__.py
# Public API for the crypto package.
# Internal modules (hashing, hmac, encoding) are implementation details.
# Consumers import from auth_engine.crypto, not from auth_engine.crypto.hashing.

from auth_engine.crypto.hashing import hash_password, verify_password
from auth_engine.crypto.comparison import constant_time_equal

__all__ = ["hash_password", "verify_password", "constant_time_equal"]
```

Phase 0 `__init__.py` files are empty — they'll be populated as each module is built.

### 1.4 Data Validation

Validate at the **boundary** — the point where untrusted data enters the system. That means:

- HTTP request bodies (form data, headers, cookies)
- Data read from the database before constructing domain objects
- Any function whose callers are external to the package

Internal functions between trusted, typed components do not need defensive validation — mypy + the type system handles that.

### 1.5 Domain Models

All domain models are **frozen dataclasses with `__slots__`** — immutable value objects.

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class User:
    """Represents an authenticated identity in the system.

    Attributes:
        user_id: Unique identifier (UUID string).
        username: Display name and login credential.
        password_hash: PBKDF2 hash of the user's password. Never plaintext.
        role: The role assigned to this user, determining authorization.
    """
    user_id: str
    username: str
    password_hash: str
    role: str
```

`frozen=True` — instances cannot be mutated after creation. Prevents accidental state corruption.
`slots=True` — attributes declared upfront, no `__dict__`. Faster attribute access, lower memory.

### 1.6 Type Variables / Generics

Type variables (`T`) are how you write functions or classes that work with *any* type while still being correctly type-checked. They are generics.

They enter this project in Phase 1 when we write a `Repository[T]` base class:

```python
from typing import TypeVar, Generic

EntityT = TypeVar("EntityT")

class Repository(Generic[EntityT]):
    """Base repository — concrete subclasses bind EntityT to a domain type."""

    def find_by_id(self, entity_id: str) -> EntityT | None: ...
```

`UserRepository(Repository[User])` — mypy knows `find_by_id` returns `User | None`.
`SessionRepository(Repository[Session])` — mypy knows `find_by_id` returns `Session | None`.

Without the type variable, you'd have to write `find_by_id` three separate times (once per entity) or lose type safety by returning `object`. Don't worry about this until Phase 1 introduces the base class.

### 1.7 Documentation

- Every **public** class, function, and method: Google-style docstring
- Every **module**: module-level docstring explaining its single responsibility
- Complex or non-obvious logic: inline `# comment` explaining *why*, not *what*
- `# TODO(PhaseN): description` for deferred work — never bare `# TODO`

### 1.8 Testing

| Category | Scope | Location | Pre-commit? |
|---|---|---|---|
| Unit | Single function / method, all branches, no I/O | `tests/unit/` | Yes (fast gate) |
| Integration | Multi-component flow (e.g., full login → session → dashboard) | `tests/integration/` | No (run manually / CI) |
| Regression | Captured bugs, found-in-review edge cases | `tests/regression/` | No |

Test function naming: `test_<subject>_<condition>_<expected_outcome>`

```python
def test_hash_password_with_empty_string_raises_value_error() -> None: ...
def test_verify_hmac_with_wrong_key_returns_false() -> None: ...
def test_login_with_valid_credentials_sets_session_cookie() -> None: ...
```

### 1.9 Commit Convention

Format: `<type>(<scope>): <short imperative summary>`

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`, `perf`

**Scopes:**

| Scope | Phase |
|---|---|
| `scaffold` | 0 — project setup |
| `infra` | 0 — tooling, pre-commit, CI config |
| `ui` | 0 — HTML stubs, later OAuth consent screen |
| `db` | 1 — SQLite schema, repositories |
| `domain` | 1 — dataclasses, domain models |
| `crypto` | 2 — hashing, HMAC, encoding |
| `auth-basic` | 3 — password authentication |
| `auth-session` | 4 — session-based auth |
| `auth-token` | 5, 6 — HMAC token, JWT |
| `auth-oauth` | 9 — OAuth2 authorization code flow |
| `authz-rbac` | 7 — role-based access control |
| `authz-abac` | 8 — attribute-based access control |
| `authz-pbac` | 10 — policy-based access control |
| `test` | any — test additions independent of feature commits |

### 1.10 No Third-Party Abstractions for Core Logic

| Allowed | Why |
|---|---|
| `pytest`, `pytest-cov` | Test infrastructure — not auth logic |
| `ruff`, `mypy`, `pre-commit`, `detect-secrets` | Dev tooling |
| `uv` | Package / env management |

Everything else — crypto, hashing, token generation, session management, HTTP — stdlib only: `hashlib`, `hmac`, `secrets`, `sqlite3`, `http.server`, `json`, `base64`, `struct`, `time`, `os`, `uuid`, `dataclasses`, `typing`.

---

## 2. Project Structure

```
auth_engine/                         ← git root
├── pyproject.toml
├── .pre-commit-config.yaml
├── .secrets.baseline                ← detect-secrets audit file (committed)
├── .python-version                  ← 3.13
├── README.md
├── llm/                             ← LLM conversation logs (reference only)
│
├── src/
│   └── auth_engine/
│       ├── __init__.py
│       │
│       ├── crypto/                  ← Phase 2: cryptographic primitives
│       │   ├── __init__.py
│       │   ├── hashing.py           ← SHA-256, salted hash, PBKDF2
│       │   ├── hmac.py              ← HMAC-SHA256
│       │   ├── encoding.py          ← base64url encode/decode
│       │   └── comparison.py        ← constant-time comparison
│       │
│       ├── db/                      ← Phase 1: SQLite persistence layer
│       │   ├── __init__.py
│       │   ├── connection.py        ← connection factory + context manager
│       │   ├── migrations.py        ← sequential SQL migration runner
│       │   └── repositories/
│       │       ├── __init__.py
│       │       ├── base.py          ← Repository[T] generic base
│       │       ├── user_repository.py
│       │       ├── session_repository.py
│       │       └── token_repository.py
│       │
│       ├── domain/                  ← Phase 1: pure domain models (no I/O)
│       │   ├── __init__.py
│       │   ├── user.py              ← User, Role (frozen dataclasses)
│       │   ├── session.py           ← Session
│       │   └── token.py             ← TokenClaims, TokenHeader
│       │
│       ├── auth/                    ← Phases 3–9: authentication mechanisms
│       │   ├── __init__.py
│       │   ├── interfaces.py        ← AuthenticatorProtocol (DI contract)
│       │   ├── basic/
│       │   │   └── password_authenticator.py
│       │   ├── session/
│       │   │   └── session_authenticator.py
│       │   ├── token/
│       │   │   ├── hmac_token.py
│       │   │   └── jwt.py
│       │   └── oauth/               ← Phase 9: OAuth2 authorization code flow
│       │       ├── authorization_server.py
│       │       ├── token_endpoint.py
│       │       └── resource_server.py
│       │
│       ├── authz/                   ← Phases 7–10: authorization mechanisms
│       │   ├── __init__.py
│       │   ├── interfaces.py        ← AuthorizerProtocol
│       │   ├── rbac/
│       │   │   └── role_authorizer.py
│       │   ├── abac/
│       │   │   └── attribute_authorizer.py
│       │   └── pbac/
│       │       └── policy_authorizer.py
│       │
│       ├── web/                     ← Phase 0+: HTTP server + routing
│       │   ├── __init__.py
│       │   ├── server.py            ← HTTPServer entry point
│       │   ├── router.py            ← path → handler dispatch table
│       │   ├── request.py           ← parsed Request dataclass
│       │   └── response.py          ← Response builder helpers
│       │
│       └── ui/                      ← Static HTML (not a Python package)
│           ├── login.html
│           ├── dashboard_admin.html
│           └── dashboard_viewer.html
│
└── tests/
    ├── conftest.py                  ← shared fixtures
    ├── unit/
    │   ├── conftest.py
    │   ├── crypto/
    │   ├── auth/
    │   └── authz/
    ├── integration/
    └── regression/
```

**Why `src/` layout?** With a flat layout, `import auth_engine` in tests resolves to the local directory before the installed package — meaning tests can accidentally pass against source files rather than the installed package. The `src/` layout forces `auth_engine` to be installed (even in editable mode via `uv pip install -e .`) before it's importable, so tests always run against the real installed package. This catches import-related bugs that a flat layout hides.

---

## 3. UI Evolution by Phase

| Phase | What the UI needs |
|---|---|
| 0 | `login.html`, `dashboard_admin.html`, `dashboard_viewer.html` — static stubs, no logic |
| 3 | Login form POST works — server validates credentials and redirects |
| 4 | Session cookie set on login; logout link works |
| 7 | Admin vs viewer routing based on role — both dashboards reachable |
| 9 | OAuth2 consent screen: `consent.html` — new file; redirect landing page added to router |

The UI is deliberately minimal and changes only when a new auth feature *requires* it.

---

## 4. Phase-by-Phase Roadmap

### Phase 0 — Scaffold

**Scope tags:** `scaffold`, `infra`, `ui`

**Build:**
- Migrate from flat layout to `src/auth_engine/` package structure
- `pyproject.toml` fully configured (ruff, mypy, pytest, coverage)
- `.pre-commit-config.yaml` with ruff, mypy, detect-secrets, pytest-unit hooks
- `.secrets.baseline` generated and committed
- All `__init__.py` stubs in place
- Three HTML stubs in `src/auth_engine/ui/`
- `server.py` serving static HTML from `ui/` — GET `/login`, `/dashboard`, `/dashboard/admin`; POST `/login` stub

**Exit criteria:** `pre-commit run --all-files` passes clean. `uv run python -m auth_engine.web.server` serves `login.html` at `http://127.0.0.1:8080/login`.

**Commits (in order):**
```
chore(scaffold): migrate to src layout, remove flat main.py
chore(infra): configure ruff, mypy, detect-secrets, pytest in pyproject.toml
chore(infra): add pre-commit hooks for ruff, mypy, detect-secrets, pytest-unit
chore(infra): generate detect-secrets baseline
feat(ui): add login and dashboard HTML stubs
feat(scaffold): add minimal stdlib HTTP server serving static UI
```

---

### Phase 1 — Domain + DB Layer

**Scope tags:** `domain`, `db`

**Build:**
- `User`, `Role`, `Session`, `TokenClaims` as frozen dataclasses
- SQLite schema: `users`, `roles`, `permissions`, `user_roles`, `sessions`
- Migration runner: `schema_version` table + sequential SQL files
- `Repository[T]` generic base; `UserRepository`, `SessionRepository`
- Dependency injection: repositories constructed at app startup, passed down

**Learn:** repository pattern, DI without a framework, SQLite quirks, frozen dataclasses, type variables (introduced here)

---

### Phase 2 — Cryptographic Primitives

**Scope tag:** `crypto`

**Build:** `hashing.py`, `hmac.py`, `encoding.py`, `comparison.py`

**Learn:** hash functions, salting, PBKDF2, HMAC inner/outer pad, timing attacks, base64url

---

### Phase 3 — Password Authentication

**Scope tag:** `auth-basic`

**Build:** `PasswordAuthenticator`, POST `/login` wired to real credential check, redirect to dashboard on success

**Learn:** what authentication means precisely, credential stuffing vs brute-force, why we don't store plaintext

---

### Phase 4 — Session-Based Auth

**Scope tag:** `auth-session`

**Build:** `SessionAuthenticator`, `secrets.token_urlsafe`, session cookie set/read, session expiry + `/logout`

**Learn:** stateful sessions, CSPRNG vs PRNG, cookie flags (`HttpOnly`, `Secure`, `SameSite`), session fixation

---

### Phase 5 — HMAC Token Auth

**Scope tag:** `auth-token`

**Build:** stateless signed token (`payload + HMAC`), `TokenAuthenticator` issues + verifies without DB lookup

**Learn:** stateful vs stateless tradeoff, why the server can trust the token, token replay

---

### Phase 6 — JWT from Scratch

**Scope tag:** `auth-token`

**Build:** `JwtBuilder` + `JwtVerifier`, HS256, standard claims (`iss sub exp iat jti`), full base64url encoding

**Learn:** JWT structure (three parts), `alg: none` vulnerability, `jti` for one-time tokens

---

### Phase 7 — RBAC

**Scope tag:** `authz-rbac`

**Build:** `RoleAuthorizer`, `@requires_permission` decorator, `admin` + `viewer` roles seeded in DB, routing diverges by role

**Learn:** authentication vs authorization, Users → Roles → Permissions indirection, least privilege

---

### Phase 8 — ABAC

**Scope tag:** `authz-abac`

**Build:** `AttributeAuthorizer`, policy as Python predicate, subject/resource/environment attributes

**Learn:** why RBAC fails on context-dependent access, four ABAC pillars, PDP vs PEP

---

### Phase 9 — OAuth2 (Authorization Code Flow + PKCE)

**Scope tags:** `auth-oauth`, `ui`

**Build:**
- `AuthorizationServer`: issues authorization codes
- `TokenEndpoint`: exchanges code → access token + refresh token
- `ResourceServer`: validates bearer tokens on protected routes
- Simulated "client" making the redirect dance within the same server
- `consent.html` UI: scope approval screen
- PKCE: code challenge + code verifier exchange

**Learn:** why OAuth2 exists (delegated auth without sharing passwords), four roles, authorization code flow step-by-step, what PKCE prevents (code interception), access token vs refresh token, OAuth2 ≠ authentication (that's OIDC)

---

### Phase 10 — PBAC *(stretch)*

**Scope tag:** `authz-pbac`

**Build:** policy engine with structured rules in SQLite, conflict resolution (deny-overrides)

**Learn:** enterprise PAM/IAM thinking, ReBAC and Google Zanzibar as a direction beyond ABAC

---

## 5. Learning Structure Per New Concept

For every new concept introduced, exactly this structure — no diverging:

1. **Plain English** — one sentence, no jargon
2. **Real-world analogy** — a concrete non-technical parallel that maps cleanly
3. **Why it exists** — what problem preceded it, what broke without it
4. **How it works** — mechanism, not just interface
5. **Pitfalls** — what goes wrong when misused or absent
6. **Related / variant concepts** — briefly named, with a note on when each applies instead
7. **Where it fits** — zoom out to the bigger auth picture
8. **Python specifics** — stdlib behaviour, gotcha, or idiom relevant to this concept

If a tangent is intriguing but off-topic: one sentence naming it, a `# TODO(PhaseN): revisit` comment. No more.

---

## 6. Immediate Next Steps (Phase 0 completion)

```powershell
# From auth_engine project root

# 1. Delete the uv init default (flat layout)
Remove-Item main.py

# 2. Run the scaffold script to create the directory structure
.\scaffold.ps1    # (or create dirs manually — see scaffold.ps1)

# 3. Replace pyproject.toml with the corrected version
# 4. Add .pre-commit-config.yaml

# 5. Add detect-secrets as a dev dep and generate baseline
uv add --dev detect-secrets
uv run detect-secrets scan > .secrets.baseline

# 6. Install pre-commit hooks
pre-commit install

# 7. Add the src layout package to uv (editable install)
uv pip install -e .

# 8. Run hooks — should pass clean
pre-commit run --all-files

# 9. Smoke test the server
uv run python -m auth_engine.web.server
# → open http://127.0.0.1:8080/login in browser
```

---

## 7. What Success Looks Like

By the end you can, without notes:

- Explain why salted PBKDF2 is used instead of `SHA256(password)`
- Implement HMAC-SHA256 from a verbal description of the algorithm
- Read a raw JWT string and decode all three parts by hand
- Explain the OAuth2 authorization code flow step-by-step, including what PKCE prevents
- Choose between RBAC and ABAC for a given authorization requirement and justify the choice
- Write a Python module with full type annotations, Google docstrings, and a test suite a stranger could read and trust

---

*Document version: 0.2 — updated after Phase 0 clarifications. Living document: updated at the start of each phase.*