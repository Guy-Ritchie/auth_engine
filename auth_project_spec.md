# AuthForge — Project Specification & Learning Roadmap

> **Tagline:** A from-first-principles implementation of Authentication & Authorization mechanisms in Python 3.13, built to understand — not just use.

---

## 0. What This Is (and What It Isn't)

This project is a **deliberate learning vehicle** disguised as a web application.

The web app itself — a minimal HTML login page that routes users to one of two pages based on role — is the *pretext*, not the point. The point is to build every authentication and authorization mechanism from scratch, in increasing sophistication, in a production-quality Python codebase, so that by the end you don't just know *how* to use JWT or OAuth2 — you know *why* they exist, *what problem* each solves, and *what breaks* when they're absent or misused.

**What this is not:**
- A production-ready auth library (use `python-jose`, `passlib`, `authlib` for that)
- A tutorial that hands you code to copy
- A project that reaches for `flask-login` or `fastapi-users` and calls it a day

---

## 1. Non-Negotiables (apply at every phase)

These are the invariants. No phase proceeds without them being satisfied.

### 1.1 Code Quality

| Concern | Tool | Config location |
|---|---|---|
| Linting + style | `ruff` | `pyproject.toml` → `[tool.ruff]` |
| Type checking | `mypy` | `pyproject.toml` → `[tool.mypy]` |
| Pre-commit enforcement | `pre-commit` | `.pre-commit-config.yaml` |
| Test runner | `pytest` | `pyproject.toml` → `[tool.pytest.ini_options]` |
| Coverage | `pytest-cov` | same |

**Ruff rules to enforce (minimum):**
- `E`, `W` — pycodestyle errors & warnings
- `F` — pyflakes
- `N` — pep8-naming (this is our naming enforcer)
- `C90` — mccabe complexity (max complexity = 10)
- `D` — pydocstyle (Google convention)
- `ANN` — flake8-annotations (enforces type hints)
- `S` — bandit security rules (critical for a security-focused project)
- `SIM` — simplify
- `UP` — pyupgrade

**Naming conventions (enforced via ruff N-rules):**
- Classes: `PascalCase`
- Functions / methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`
- Type variables: `T`, `UserT` (single uppercase or PascalCase with T suffix)

### 1.2 Commit Convention

Commits follow [Conventional Commits](https://www.conventionalcommits.org/) with scopes tied to the project module being touched:

```
<type>(<scope>): <short imperative summary>

[optional body]

[optional footer: BREAKING CHANGE, refs, closes]
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`, `perf`

**Scopes (defined per phase):**
- `scaffold` — project setup, tooling, pre-commit
- `crypto` — cryptographic primitives
- `auth-basic` — password/key based authentication
- `auth-session` — session-based auth
- `auth-token` — token-based (HMAC, JWT)
- `auth-oauth` — OAuth / OAuth2 simulation
- `authz-rbac` — role-based access control
- `authz-abac` — attribute-based access control
- `authz-pbac` — policy-based access control
- `ui` — client-side HTML/CSS changes
- `db` — SQLite schema / migrations
- `test` — test additions or fixes
- `infra` — pre-commit, CI, config

Example: `feat(auth-token): implement HS256 JWT signing and verification from scratch`

### 1.3 Documentation

- Every public class, function, and method gets a **Google-style docstring**.
- Every module gets a module-level docstring explaining its responsibility.
- Complex logic gets **inline comments** explaining *why*, not *what*.
- No orphan code — if it exists, it's explained.

**Google-style docstring shape:**
```python
def verify_hmac(message: bytes, signature: bytes, key: bytes) -> bool:
    """Verify an HMAC-SHA256 signature against a message and secret key.

    Uses a constant-time comparison to prevent timing attacks.

    Args:
        message: The original plaintext message bytes.
        signature: The HMAC digest to verify against.
        key: The shared secret key bytes.

    Returns:
        True if the signature is valid, False otherwise.

    Raises:
        ValueError: If message, signature, or key is empty.
    """
```

### 1.4 Testing

Every non-trivial unit gets tests. Tests are not an afterthought.

**Test categories:**

| Category | What it tests | Location |
|---|---|---|
| Unit | Single function / method in isolation, all branches | `tests/unit/` |
| Integration | Multiple components working together (e.g. auth flow end-to-end) | `tests/integration/` |
| Regression | Captured bugs, edge cases found in review | `tests/regression/` |

**pytest conventions:**
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>` (grouped by subject)
- Test functions: `test_<what>_<when>_<expected>` (e.g. `test_verify_hmac_with_wrong_key_returns_false`)
- Fixtures in `conftest.py` at the appropriate level
- No magic — every test is readable in isolation
- Parametrize for equivalence classes: `@pytest.mark.parametrize`

### 1.5 No Third-Party Abstractions for Core Logic

The **only** allowed third-party packages are:

| Package | Why allowed |
|---|---|
| `pytest`, `pytest-cov` | Test runner infrastructure — not auth logic |
| `ruff`, `mypy`, `pre-commit` | Dev tooling |
| `uv` | Package / env manager |

Crypto, hashing, encoding, token generation, session management, HTTP handling — **all from stdlib only** (`hashlib`, `hmac`, `secrets`, `sqlite3`, `http.server`, `json`, `base64`, `struct`, `time`, `os`, `uuid`).

This constraint is the entire point. When you later reach for `python-jose`, you will know exactly what it's doing underneath.

---

## 2. Project Structure

```
authforge/
├── pyproject.toml                  # uv + ruff + mypy + pytest config
├── .pre-commit-config.yaml         # ruff, mypy, pytest on staged files
├── .python-version                 # 3.13
├── README.md
│
├── src/
│   └── authforge/
│       ├── __init__.py
│       │
│       ├── crypto/                 # Phase 2 — all cryptographic primitives
│       │   ├── __init__.py
│       │   ├── hashing.py          # password hashing (SHA-256, bcrypt-manual, PBKDF2)
│       │   ├── hmac.py             # HMAC implementation
│       │   ├── encoding.py         # base64url, hex utils
│       │   └── comparison.py      # constant-time comparison
│       │
│       ├── db/                     # SQLite layer
│       │   ├── __init__.py
│       │   ├── connection.py       # connection factory, context manager
│       │   ├── migrations.py       # schema versioning (manual, no ORM)
│       │   └── repositories/       # one repo per entity
│       │       ├── __init__.py
│       │       ├── user_repository.py
│       │       ├── session_repository.py
│       │       └── token_repository.py
│       │
│       ├── domain/                 # Pure domain models — no I/O
│       │   ├── __init__.py
│       │   ├── user.py             # User, Role, Permission dataclasses
│       │   ├── session.py          # Session dataclass
│       │   └── token.py            # TokenClaims, TokenHeader dataclasses
│       │
│       ├── auth/                   # Authentication mechanisms (one module per phase)
│       │   ├── __init__.py
│       │   ├── interfaces.py       # AuthenticatorProtocol — the DI contract
│       │   ├── basic/
│       │   │   ├── __init__.py
│       │   │   └── password_authenticator.py
│       │   ├── session/
│       │   │   ├── __init__.py
│       │   │   └── session_authenticator.py
│       │   ├── token/
│       │   │   ├── __init__.py
│       │   │   ├── hmac_token.py
│       │   │   └── jwt.py          # HS256 JWT from scratch
│       │   └── oauth/
│       │       ├── __init__.py
│       │       ├── authorization_server.py
│       │       ├── token_endpoint.py
│       │       └── resource_server.py
│       │
│       ├── authz/                  # Authorization mechanisms
│       │   ├── __init__.py
│       │   ├── interfaces.py       # AuthorizerProtocol
│       │   ├── rbac/
│       │   │   ├── __init__.py
│       │   │   └── role_authorizer.py
│       │   ├── abac/
│       │   │   ├── __init__.py
│       │   │   └── attribute_authorizer.py
│       │   └── pbac/
│       │       ├── __init__.py
│       │       └── policy_authorizer.py
│       │
│       ├── web/                    # Minimal HTTP server (stdlib http.server)
│       │   ├── __init__.py
│       │   ├── server.py           # RequestHandler subclass
│       │   ├── router.py           # path → handler dispatch
│       │   ├── request.py          # parsed Request dataclass
│       │   └── response.py         # Response builder
│       │
│       └── ui/                     # Static HTML templates (minimal)
│           ├── login.html
│           ├── dashboard_admin.html
│           └── dashboard_user.html
│
└── tests/
    ├── conftest.py                 # shared fixtures (in-memory SQLite, test users)
    ├── unit/
    │   ├── crypto/
    │   ├── auth/
    │   └── authz/
    ├── integration/
    │   ├── test_login_flow.py
    │   └── test_authorization_flow.py
    └── regression/
        └── .gitkeep
```

---

## 3. Learning Roadmap (Phase-by-phase)

Each phase has: a **what you'll build**, a **what you'll learn**, and a **commit scope**.

---

### Phase 0 — Scaffold (`scope: scaffold`, `scope: infra`)

**Build:**
- `uv init -p 3.13` workspace
- `pyproject.toml` with all dev deps declared
- `ruff` configured with the rule set above
- `mypy` in strict mode
- `pre-commit` hooks: ruff → mypy → pytest (fast subset)
- Initial SQLite connection + schema migration runner
- Minimal HTTP server that returns 200 OK

**Learn:**
- How `uv` resolves and locks deps differently from `pip`
- What pre-commit hooks actually run and when
- Why `mypy --strict` is painful and necessary

**Non-negotiable exits:** `pre-commit run --all-files` passes. Server boots. DB creates schema on first run.

---

### Phase 1 — Domain + DB Layer (`scope: db`)

**Build:**
- `User`, `Role`, `Permission` dataclasses (frozen, slots)
- SQLite schema: `users`, `roles`, `permissions`, `user_roles` tables
- Repository pattern: `UserRepository` with typed methods
- Manual migration versioning (a `schema_version` table + sequential SQL files)
- Dependency injection: repositories are injected, never instantiated inside business logic

**Learn:**
- Why we separate domain models from persistence models
- Repository pattern vs Active Record — and why the former wins for testability
- Dependency injection without a framework (just constructor injection)
- SQLite quirks (no `BOOLEAN`, `INTEGER PRIMARY KEY` autoincrement, foreign key enforcement off by default)

---

### Phase 2 — Cryptographic Primitives (`scope: crypto`)

**Build:**
- `hashing.py`: SHA-256 (via `hashlib`), salted hash, PBKDF2 wrapper (via `hashlib.pbkdf2_hmac`)
- `hmac.py`: HMAC-SHA256 built on `hmac` stdlib (understand the inner/outer pad construction)
- `encoding.py`: base64url encode/decode (no padding issues — implement the padding fix)
- `comparison.py`: constant-time compare (explain why `==` leaks timing)

**Learn:**
- What a hash function is and why it's one-way
- Why salting exists (rainbow table attack)
- Why PBKDF2 / key stretching exists (brute-force cost)
- HMAC: why you can't just `SHA256(key + message)` (length extension attack)
- Timing attacks: how comparing byte-by-byte leaks information and how `hmac.compare_digest` fixes it
- base64url vs base64 and why JWT uses the URL-safe variant

**Cryptographic progression chart:**

```
Plaintext password  →  SHA-256(password)         [broken: no salt]
                    →  SHA-256(salt + password)   [better: rainbow table resistant]
                    →  PBKDF2(password, salt, N)  [good: expensive to brute-force]
```

---

### Phase 3 — Basic Password Authentication (`scope: auth-basic`)

**Build:**
- `PasswordAuthenticator`: accepts `(username, password)`, returns `User | None`
- HTML login form → POST handler → authenticator → redirect
- Store PBKDF2 hashes in SQLite, never plaintext

**Learn:**
- Credential stuffing vs brute-force — different threat, different defence
- Why HTTP Basic Auth (base64 in header) is not the same as password auth
- What "authentication" means precisely: asserting identity

---

### Phase 4 — Session-Based Auth (`scope: auth-session`)

**Build:**
- `SessionAuthenticator`: generates a cryptographically random session token (`secrets.token_urlsafe`)
- `SessionRepository`: stores `(session_id, user_id, expires_at)` in SQLite
- Set/read session cookie in HTTP response/request
- Session expiry + invalidation (logout)

**Learn:**
- What a session is (server-side state, client holds only a reference)
- Why `random` is wrong and `secrets` is right (CSPRNG vs PRNG)
- Cookie flags: `HttpOnly`, `Secure`, `SameSite` — what each prevents
- Session fixation attack

---

### Phase 5 — HMAC Token Auth (`scope: auth-token`)

**Build:**
- Stateless token: `user_id + expires_at` payload, HMAC-SHA256 signed
- `TokenAuthenticator`: issues and verifies tokens
- No DB lookup on verify — everything in the token (contrast with Phase 4)

**Learn:**
- Stateful (session) vs stateless (token) — tradeoffs
- Why the server can trust the token without a DB lookup (HMAC guarantees integrity + origin)
- Token replay attacks and expiry as partial mitigation

---

### Phase 6 — JWT from Scratch (`scope: auth-token`)

**Build:**
- `JwtBuilder`: constructs `base64url(header).base64url(payload).signature`
- `JwtVerifier`: splits, decodes, re-signs header+payload, constant-time compares
- HS256 only (HMAC-SHA256) — RS256 is a stretch goal
- Standard claims: `iss`, `sub`, `exp`, `iat`, `jti`

**Learn:**
- Why JWT is just "a signed JSON object with a standard structure" — demystify the format
- The three parts: header, payload, signature — each independently base64url-encoded
- `alg: none` vulnerability — why you must reject tokens with no algorithm
- `jti` (JWT ID) for one-time-use tokens

---

### Phase 7 — Role-Based Access Control (`scope: authz-rbac`)

**Build:**
- `Role`, `Permission` domain objects
- `RoleAuthorizer`: given `(user, required_permission)`, returns `bool`
- Decorator / middleware pattern: `@requires_permission("admin:read")`
- Roles seeded in DB: `admin`, `viewer`

**Learn:**
- Authentication vs Authorization — precisely: "who are you" vs "what can you do"
- RBAC model: Users → Roles → Permissions (not Users → Permissions directly)
- Why flat permission lists don't scale and roles are the indirection layer
- Principle of least privilege

---

### Phase 8 — Attribute-Based Access Control (`scope: authz-abac`)

**Build:**
- `AttributeAuthorizer`: evaluates `policy(subject_attrs, resource_attrs, env_attrs) → bool`
- Policies expressed as simple Python predicates (no DSL yet)
- Example: `user.department == resource.owner_department and env.time < 18:00`

**Learn:**
- Why RBAC fails when access depends on context (time, location, data attributes)
- ABAC: Subject + Resource + Environment + Action — the four pillars
- Policy decision point (PDP) vs policy enforcement point (PEP)
- XACML as the enterprise spec (understand conceptually, don't implement)

---

### Phase 9 — OAuth2 Simulation (`scope: auth-oauth`)

**Build (Authorization Code Flow, simulated within the same process):**
- `AuthorizationServer`: issues authorization codes
- `TokenEndpoint`: exchanges code for access token + refresh token
- `ResourceServer`: validates bearer token on protected endpoints
- Simulated "third-party client" (another route) performing the redirect dance

**Learn:**
- Why OAuth2 exists: delegated authorization without sharing passwords
- The four roles: Resource Owner, Client, Authorization Server, Resource Server
- Authorization Code Flow step-by-step (the redirect → code → token exchange)
- Why PKCE (Proof Key for Code Exchange) exists — code interception attack
- Access token vs refresh token — different lifetimes, different purposes
- OAuth2 ≠ authentication (that's OpenID Connect on top)

---

### Phase 10 — Policy-Based Access Control (`scope: authz-pbac`) *(stretch)*

**Build:**
- A minimal policy engine: policies stored in SQLite as structured rules
- `PolicyAuthorizer`: evaluates applicable policies, returns permit/deny/not-applicable
- Conflict resolution: deny-overrides vs permit-overrides

**Learn:**
- How enterprise PAM/IAM systems think about policy
- ReBAC (Relationship-Based Access Control) as a direction beyond ABAC (e.g. Google Zanzibar)

---

## 4. Learning Structure Per New Concept

Whenever a new concept is introduced, it is presented in this order — no diverging into tangents:

1. **Plain English** — what it is in one sentence, no jargon
2. **Real-world analogy** — a concrete, non-technical parallel that maps cleanly
3. **Why it exists** — what problem preceded it, what broke without it
4. **How it works** — mechanism, not just interface
5. **Pitfalls** — what goes wrong when it's misused or absent
6. **Related / variant concepts** — briefly named, with a note on when they're relevant instead
7. **Where it fits in our project** — zoom out to the bigger auth picture
8. **Python specifics** — any stdlib behaviour, gotcha, or idiom worth knowing for this concept

If a tangent topic is intriguing but not the focus, it gets: one sentence naming it, and a `# TODO: revisit in Phase N` comment. No more.

---

## 5. Pre-Commit Hook Configuration (reference)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: []  # no stubs needed — stdlib only

  - repo: local
    hooks:
      - id: pytest-fast
        name: pytest (unit tests only)
        entry: uv run pytest tests/unit/ -q --tb=short
        language: system
        pass_filenames: false
        stages: [pre-commit]
```

---

## 6. `pyproject.toml` Skeleton (reference)

```toml
[project]
name = "authforge"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []

[tool.uv]
dev-dependencies = [
    "ruff>=0.4",
    "mypy>=1.10",
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pre-commit>=3.7",
]

[tool.ruff]
target-version = "py313"
line-length = 88
select = ["E", "W", "F", "N", "C90", "D", "ANN", "S", "SIM", "UP"]
ignore = ["D203", "D212"]  # conflict with Google docstring style

[tool.ruff.pydocstyle]
convention = "google"

[tool.ruff.mccabe]
max-complexity = 10

[tool.mypy]
strict = true
python_version = "3.13"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/authforge --cov-report=term-missing -q"
```

---

## 7. First Steps — Ordered

Execute these in order before writing any auth logic:

```bash
# 1. Initialise project
uv init authforge -p 3.13
cd authforge

# 2. Add dev deps
uv add --dev ruff mypy pytest pytest-cov pre-commit

# 3. Create src layout
mkdir -p src/authforge tests/unit tests/integration tests/regression

# 4. Install pre-commit hooks
uv run pre-commit install

# 5. Verify hook runs clean on an empty project
uv run pre-commit run --all-files

# 6. First commit
git add .
git commit -m "chore(scaffold): initialise uv project with ruff, mypy, pre-commit"
```

---

## 8. What Success Looks Like

By the end of this project you will be able to:

- Explain, without notes, why salted PBKDF2 is used instead of `SHA256(password)`
- Implement HMAC-SHA256 from a description of the algorithm, not from memory
- Read a raw JWT string and decode all three parts by hand
- Explain the OAuth2 authorization code flow, step-by-step, including what PKCE prevents
- Articulate the difference between RBAC and ABAC and choose the right one for a given requirement
- Write a Python module with full type annotations, Google docstrings, and a test suite that a stranger could read and trust

---

*Document version: 0.1 — living document, updated at the start of each phase.*
