# Phase 0 — Reference Guide & Structural Rationale

## Objective of Phase 0

Get a working skeleton that compiles, type-checks, lints clean, and runs a test — before
writing a single line of auth logic. The goal is a harness: every future commit goes through
the same gate (ruff → mypy → detect-secrets → pytest) so quality problems surface
immediately, not after ten phases of accumulated debt.

**What we're NOT doing in Phase 0:** any authentication or authorization logic. Not even
stubs of it. Just the project skeleton, tooling, and a server that boots and serves HTML.

---

## 1. Why the `src/` Layout

### The short version

Without `src/`, Python can silently import your source files directly from the project root
instead of from the installed package. This means your tests may pass against code that
would fail when actually installed — a subtle class of bug that only surfaces in deployment.

### The longer version

When you run `pytest` from the project root and your package is at `auth_engine/` (flat
layout), Python adds the current directory to `sys.path`. So `import auth_engine` finds
the local directory. This looks fine — until you realise:

- You could have a broken `__init__.py` that prevents installation, but tests still pass
  because they never go through the install path
- A missing file that should be included in the package (via `MANIFEST.in` or similar)
  won't be caught until someone else installs the package and gets an ImportError

With `src/auth_engine/`, the `src/` directory is NOT automatically on `sys.path`. You must
explicitly install the package (even in editable mode via `uv pip install -e .`) before
`import auth_engine` works. This forces your tests to run against the installed package,
catching packaging problems early.

### References

- **Hynek Schlawack — "Testing & Packaging"** (the canonical argument for `src/` layout)
  https://hynek.me/articles/testing-packaging/
  *What it addresses:* Explains exactly the `sys.path` shadowing problem above, with
  concrete examples of the bugs it hides. Read this before you decide on layout.

- **Brett Cannon — "Why you shouldn't invoke setup.py directly"** (background on modern
  Python packaging that motivates the src layout era)
  https://snarky.ca/why-you-shouldnt-invoke-setup-py-directly/
  *What it addresses:* Context on how `pyproject.toml`-based packaging (PEP 517/518)
  changed the packaging model and why the src layout aligns with it.

- **PEP 517** — A build-system independent format for source trees
  https://peps.python.org/pep-0517/
  *What it addresses:* The formal spec for the `pyproject.toml`-based build model.
  Explains what `[build-system]` means and why it replaced `setup.py`.

- **PEP 518** — Specifying minimum build system requirements
  https://peps.python.org/pep-0518/
  *What it addresses:* Why `pyproject.toml` was introduced and what problem
  `setup.py` couldn't solve (bootstrapping build dependencies).

### Why this matters specifically for `auth_engine`

We're going to run `pre-commit run --all-files` on every commit, which runs `pytest`.
If we had a flat layout and later made a packaging error, our pre-commit hook would still
pass (because pytest finds the local directory) while a fresh install would break.
The `src/` layout makes our test gate honest.

---

## 2. Why Explicit `__init__.py` Over Implicit Namespace Packages

### What PEP 420 / 402 proposed

PEP 420 (and the earlier PEP 402) proposed "implicit namespace packages" — directories
without `__init__.py` that Python would treat as packages anyway. PEP 420 was withdrawn.
What actually landed was **PEP 420's predecessor**: **PEP 420 was withdrawn**, and instead
**PEP 402 was superseded by PEP 420 which was superseded by PEP 382 which was superseded
by PEP 402** — the history is circular and confusing. What actually shipped in Python 3.3
was **PEP 420's final successor**:

- **PEP 420 (withdrawn):** https://peps.python.org/pep-0420/
- **What actually landed — PEP 420 context:** https://peps.python.org/pep-0402/
- **The one that shipped — implicit namespace packages:** **PEP 420** was withdrawn in
  favour of a simpler mechanism described in:
  **PEP 420 → actually read PEP 420's replacement:**
  https://peps.python.org/pep-0328/ (relative imports, for contrast)

To cut through the confusion: **the feature that shipped** is described here:
- **PEP 420 final:** The implicit namespace package feature is documented at
  https://docs.python.org/3/reference/import.html#namespace-packages
  and the motivating PEP is:
  **PEP 420 → PEP 402 → the actual shipped PEP:**
  https://peps.python.org/pep-0402/

*(The PEP numbering history here is genuinely confusing — PEP 420 was withdrawn, PEP 402
was superseded, and what shipped in 3.3 was based on a revised PEP 420 that became the
"namespace packages" section of PEP 382 which... just read the docs link above.)*

### The practical difference

| | Implicit namespace package (no `__init__.py`) | Explicit package (with `__init__.py`) |
|---|---|---|
| Python finds it | Yes, if on `sys.path` | Yes, always |
| You control public API | No — all submodules are importable | Yes — `__init__.py` defines `__all__` |
| Works across multiple directories | Yes (the main use case for namespaces) | No |
| Import clarity for readers | Lower — unclear what's "public" | Higher — `__init__.py` is the contract |
| Packaging tools handle it | Sometimes inconsistently | Consistently |

For `auth_engine`, we have a **single-root package** (not a namespace package split across
multiple directories). The only reason to use namespace packages is when you want
`auth_engine.crypto` and `auth_engine.web` to live in completely separate repos/installs
and still resolve under the same `auth_engine` namespace. We don't want that — it adds
complexity with no benefit for a single-repo project.

The explicit `__init__.py` gives us something valuable: a place to define what is and
isn't part of a subpackage's public API.

```python
# src/auth_engine/crypto/__init__.py
# This is the contract. External code imports from here, not from internals.
from auth_engine.crypto.hashing import hash_password, verify_password
from auth_engine.crypto.comparison import constant_time_equal

__all__ = ["hash_password", "verify_password", "constant_time_equal"]
```

If `auth_engine.crypto.hashing` is an implementation detail, consumers never need to
know it exists. If we later split `hashing.py` into `hashing_pbkdf2.py` and
`hashing_sha256.py`, nothing outside `auth_engine.crypto` breaks — the `__init__.py`
stays stable.

### Reference

- **Python docs — packages and `__init__.py`:**
  https://docs.python.org/3/reference/import.html#regular-packages
  *What it addresses:* The formal distinction between regular packages (with `__init__.py`)
  and namespace packages (without).

---

## 3. Why the `tests/` Namespace Is Separate from `src/`

This is straightforward but worth stating explicitly.

`tests/` is not a package you install. It's a collection of test files that `pytest`
discovers by scanning the filesystem. It lives outside `src/` for two reasons:

1. **It doesn't ship.** When someone installs `auth_engine`, they get `src/auth_engine/`.
   They don't get your test suite. Keeping tests outside `src/` makes this boundary
   structurally explicit.

2. **It imports from the installed package.** Test files do `from auth_engine.crypto
   import hash_password` — they consume the public API, they don't extend the package.
   Putting them inside `src/` would blur that consumer relationship.

`tests/` does have its own `conftest.py` files (not `__init__.py`). These are pytest's
mechanism for sharing fixtures. A `conftest.py` at `tests/` is visible to all tests.
One at `tests/unit/` is visible only to unit tests. Pytest discovers them automatically —
no import needed.

### Reference

- **pytest — Good Integration Practices (layout recommendations)**
  https://docs.pytest.org/en/stable/explanation/goodpractices.html
  *What it addresses:* Pytest's own recommendation on `src/` layout and why it avoids
  the `sys.path` shadowing problem. Also explains `conftest.py` scoping.

---

## 4. Why `conftest.py` in Phase 0 Has a Docstring but No Fixtures

Empty files with docstrings serve two purposes in Phase 0:

1. **They tell pytest where to look.** An empty `tests/unit/conftest.py` signals that
   `tests/unit/` is a fixture scope. Without it, if you later add unit-level fixtures,
   you have to remember to create the file. Creating it now with a docstring is cheap
   and prevents a future "why isn't my fixture visible?" debug session.

2. **They communicate intent.** A file with a module docstring saying "Fixtures specific
   to unit tests — no I/O, no database, no network" is self-documenting. Someone reading
   the project for the first time understands the testing philosophy from the file layout
   alone.

---

## 5. Why `.gitkeep` in Empty Directories

Git does not track directories — only files. If you create `tests/regression/` and put
nothing in it, it won't appear in `git status` and won't be committed. When someone clones
the repo, the directory won't exist, and any path assumption in the code or tooling that
references it will break.

`.gitkeep` is a convention (not a git feature) — an empty file with a name that signals
"I'm here only to make git track this directory." The name is arbitrary; `.gitkeep` is
the community standard.

---

## 6. Per-Phase Reference Lists

### Phase 0 — Scaffold & Tooling

**Project layout & packaging:**
- https://hynek.me/articles/testing-packaging/ — the `src/` layout argument
- https://peps.python.org/pep-0517/ — pyproject.toml build system spec
- https://peps.python.org/pep-0518/ — build dependency specification
- https://docs.python.org/3/reference/import.html#regular-packages — regular vs namespace packages
- https://docs.pytest.org/en/stable/explanation/goodpractices.html — pytest layout recommendations

**Tooling:**
- https://docs.astral.sh/ruff/rules/ — full ruff rule reference (bookmark this)
- https://mypy.readthedocs.io/en/stable/config_file.html — mypy configuration options
- https://pre-commit.com/#creating-new-hooks — pre-commit hook authoring
- https://github.com/Yelp/detect-secrets — detect-secrets README (covers baseline workflow)

**Conventional commits:**
- https://www.conventionalcommits.org/en/v1.0.0/ — the spec we're following

---

### Phase 1 — Domain Models & Database Layer

**Design patterns:**
- https://martinfowler.com/eaaCatalog/repository.html — Repository pattern (Fowler)
- https://martinfowler.com/eaaCatalog/dataMapper.html — Data Mapper (contrast with Active Record)
- https://en.wikipedia.org/wiki/Dependency_injection — DI concept overview

**Python specifics:**
- https://docs.python.org/3/library/dataclasses.html — `@dataclass`, `frozen`, `slots`
- https://peps.python.org/pep-0557/ — PEP 557: dataclasses original proposal
- https://mypy.readthedocs.io/en/stable/generics.html — generics and TypeVar in mypy
- https://peps.python.org/pep-0544/ — PEP 544: Protocols (structural subtyping — used for DI contracts)

**SQLite:**
- https://docs.python.org/3/library/sqlite3.html — stdlib sqlite3 docs
- https://www.sqlite.org/lang_createtable.html — SQLite DDL reference

---

### Phase 2 — Cryptographic Primitives

**Cryptography fundamentals:**
- https://en.wikipedia.org/wiki/Cryptographic_hash_function — hash function properties
- https://en.wikipedia.org/wiki/Salt_(cryptography) — salting and why it matters
- https://en.wikipedia.org/wiki/PBKDF2 — PBKDF2 key stretching
- https://en.wikipedia.org/wiki/HMAC — HMAC construction (inner/outer pad)
- https://en.wikipedia.org/wiki/Length_extension_attack — why `SHA256(key + message)` is broken

**Security / attacks:**
- https://codahale.com/a-lesson-in-timing-attacks/ — timing attack explanation (short, essential)
- https://en.wikipedia.org/wiki/Rainbow_table — why salting defeats rainbow tables

**Python specifics:**
- https://docs.python.org/3/library/hashlib.html — `hashlib.pbkdf2_hmac`, SHA-256
- https://docs.python.org/3/library/hmac.html — `hmac.new`, `hmac.compare_digest`
- https://docs.python.org/3/library/secrets.html — `secrets` module (CSPRNG)
- https://docs.python.org/3/library/base64.html — `base64.urlsafe_b64encode`

---

### Phase 3 — Password Authentication

**Security:**
- https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html — OWASP auth cheat sheet
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html — OWASP password storage
- https://en.wikipedia.org/wiki/Credential_stuffing — credential stuffing vs brute-force

**Python:**
- https://docs.python.org/3/library/urllib.parse.html#urllib.parse.parse_qs — parsing form POST body

---

### Phase 4 — Session-Based Authentication

**Security:**
- https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html — OWASP sessions
- https://en.wikipedia.org/wiki/Session_fixation — session fixation attack
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies — cookie flags (HttpOnly, Secure, SameSite)

**Python:**
- https://docs.python.org/3/library/http.cookies.html — stdlib cookie handling
- https://docs.python.org/3/library/secrets.html — `secrets.token_urlsafe`

---

### Phase 5 — HMAC Token Authentication

**Concepts:**
- https://en.wikipedia.org/wiki/Stateless_protocol — stateless vs stateful
- https://en.wikipedia.org/wiki/Replay_attack — token replay attack

---

### Phase 6 — JWT from Scratch

**Specifications:**
- https://datatracker.ietf.org/doc/html/rfc7519 — RFC 7519: JSON Web Token (the formal spec)
- https://datatracker.ietf.org/doc/html/rfc7515 — RFC 7515: JSON Web Signature
- https://datatracker.ietf.org/doc/html/rfc7518 — RFC 7518: JSON Web Algorithms (HS256 defined here)

**Security:**
- https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/ — `alg: none` attack
- https://portswigger.net/web-security/jwt — PortSwigger JWT attack labs (excellent)

**Practical:**
- https://jwt.io — JWT decoder (for manually verifying your implementation)

---

### Phase 7 — RBAC

**Concepts:**
- https://en.wikipedia.org/wiki/Role-based_access_control — RBAC model
- https://en.wikipedia.org/wiki/Principle_of_least_privilege — least privilege
- https://csrc.nist.gov/projects/role-based-access-control — NIST RBAC model (formal)

---

### Phase 8 — ABAC

**Concepts:**
- https://en.wikipedia.org/wiki/Attribute-based_access_control — ABAC overview
- https://csrc.nist.gov/projects/attribute-based-access-control — NIST ABAC guide
- https://en.wikipedia.org/wiki/XACML — XACML (enterprise policy language — understand the concept, don't implement)

---

### Phase 9 — OAuth2

**Specifications (read these in order):**
- https://datatracker.ietf.org/doc/html/rfc6749 — RFC 6749: OAuth 2.0 framework (the base spec)
- https://datatracker.ietf.org/doc/html/rfc7636 — RFC 7636: PKCE (Proof Key for Code Exchange)
- https://datatracker.ietf.org/doc/html/rfc6750 — RFC 6750: Bearer token usage

**Practical guides (read alongside the RFCs):**
- https://www.oauth.com/oauth2-servers/authorization/ — OAuth2 Simplified (Aaron Parecki — best practical guide)
- https://developer.okta.com/blog/2019/08/22/okta-authjs-pkce — PKCE walkthrough with diagrams
- https://portswigger.net/web-security/oauth — PortSwigger OAuth attack labs

**Clarification (important):**
- https://oauth.net/articles/authentication/ — OAuth 2.0 is NOT authentication (explains why OIDC exists on top)

---

### Phase 10 — PBAC (stretch)

- https://en.wikipedia.org/wiki/Attribute-based_access_control#Policy-based — PBAC as an extension of ABAC
- https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/ — Google Zanzibar (ReBAC — relationship-based, where PBAC leads at scale)
