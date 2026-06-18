Good progress. Let me work through your questions one at a time, then we'll fix the scaffold and produce an updated spec.



\*\*Secrets checker\*\* — Talisman is the right instinct. It's a pre-commit hook that scans for high-entropy strings, API keys, credentials accidentally committed. Valid concern, especially since we'll have things like HMAC keys and test tokens in fixtures. We'll add `detect-secrets` (by Yelp, widely used, works as a pre-commit hook natively) rather than Talisman — Talisman is git-hook based and harder to integrate into the pre-commit framework cleanly. Import ordering — yes, ruff's `I` ruleset (`isort`-compatible) handles this, we just need to add `I` to the select list.



\*\*Absolute imports\*\* — agreed, we align on absolute imports everywhere. No `from .sibling import X`, always `from authforge.crypto.hashing import X`. This is enforced partly by convention and partly by ruff's `TID252` rule (ban relative imports). We add that.



\*\*`\_\_init\_\_.py`\*\* — two valid conventions exist. Implicit namespace packages (PEP 420, no `\_\_init\_\_.py`) vs explicit packages (with `\_\_init\_\_.py`). For a learning project where we want the package structure to be legible and where we control what's exported from each subpackage, explicit `\_\_init\_\_.py` files are better — they let you define a clean public API for each module (`from authforge.crypto import hash\_password` rather than the full internal path). We keep them, but keep them minimal — just re-exports of the public interface, nothing else.



\*\*Data validation\*\* — yes, every function that receives external input (from HTTP, from the DB, from a config file) validates at the boundary. Internal functions between trusted components can trust their callers. The boundary is the discipline.



\*\*Schema as a class\*\* — `dataclass` with `frozen=True` and `\_\_slots\_\_ = True` for domain models (immutable value objects). For DB rows coming back from SQLite, we use the same frozen dataclasses — the repository maps raw tuples to typed dataclasses. No ORM, no magic.



\*\*Type variables / generics\*\* — good question, let's handle this properly:



A type variable `T` is how you tell the type checker "this function returns the same type it receives, but I don't know which type at definition time." Classic example: a `find\_by\_id` method on a repository that could return a `User`, a `Session`, or a `Token` — you don't want to write three identical methods. The type variable lets you write one generic method and have mypy verify it correctly at each call site. We won't need them immediately — Phase 0 and 1 won't use generics. When we introduce the `Repository` base class in Phase 1, that's when `T` enters, and we'll explain it in full at that point. Don't front-load it.



\*\*UI changes for OAuth2\*\* — yes, the UI will need to grow in Phase 9. The OAuth2 authorization code flow requires a "consent screen" (a page where the resource owner approves the client's requested scopes) and a redirect landing page. These are just two more static HTML files. We keep the UI deliberately thin until that phase forces our hand — which is exactly the right constraint.



\*\*Authorization Code Grant\*\* — yes, that is the OAuth2 flow we're implementing in Phase 9. "Authorization Code Flow" and "Authorization Code Grant" are the same thing — the spec calls it a grant type. It's listed as the primary OAuth2 implementation in the roadmap. PKCE variant of it is the stretch within that phase.



\*\*Client setup in Phase 0\*\* — yes, you're right. The three HTML files (`login.html`, `dashboard\_admin.html`, `dashboard\_user.html`) should be stubbed out in Phase 0 and the server should serve them, even if auth does nothing yet. This gives you a working end-to-end skeleton to build against from day one, rather than discovering at Phase 3 that your HTTP handler doesn't know how to serve static files. Good catch — updating the spec now.



Now the immediate fix needed: the pytest hook failing with exit code 5 means "no tests collected" — pytest treats that as an error. Two fixes needed: add `--ignore` or change the hook to not fail on no-tests, and also fix the coverage source path (your project is `auth-engine` not `auth\_engine` — the hyphen matters in the pyproject name but the import path uses underscores, and `uv init` may have created a flat layout rather than `src/`). Let me produce the corrected files now.Right — `uv init` creates a flat layout with `main.py` at root, not a `src/` layout. We need to migrate to `src/` manually. Let me write the corrected full scaffold as files.Now the stub HTML files and the minimal web server that serves them:Now the minimal HTTP server that actually serves them:Seven files. Here's the execution order to close out Phase 0:



\*\*Step 1 — replace config files.\*\* Drop `pyproject.toml` and `.pre-commit-config.yaml` into the project root, overwriting what's there. Two things changed in `pyproject.toml` worth noting: `\[tool.ruff.lint]` is now a separate table from `\[tool.ruff]` (ruff ≥ 0.4 requires this split — your current config had them merged, which is why some rules may not have been active), and `\[tool.coverage.run]` is now explicit so coverage actually finds the source.



\*\*Step 2 — run `scaffold.ps1`.\*\* It creates the directory tree and empty `\_\_init\_\_.py` files. Then place `server.py` into `src/auth\_engine/web/` and the three HTML files into `src/auth\_engine/ui/`.



\*\*Step 3 — fix the pytest exit-code-5 problem.\*\* That error is "no tests were collected" — pytest by default treats that as an error (exit 5). The corrected pre-commit hook doesn't add `--exit-zero` (that would hide real failures) — instead, once you have even one stub test file it goes away. Add this one-liner to `tests/unit/test\_placeholder.py` as a temporary measure:



```python

"""Placeholder so pytest finds at least one test during Phase 0."""





def test\_phase\_zero\_scaffold\_is\_alive() -> None:

&#x20;   """Confirms the test suite is discoverable. Remove after Phase 1."""

&#x20;   assert True

```



Commit that as `test(scaffold): add placeholder test to satisfy pytest pre-commit hook`.



\*\*Step 4 — detect-secrets.\*\* After `uv add --dev detect-secrets`, run `uv run detect-secrets scan > .secrets.baseline`. Commit the baseline file. From that point forward, if you accidentally stage a high-entropy string (a test HMAC key, a base64 fixture), the hook will catch it and tell you to either fix it or `uv run detect-secrets audit .secrets.baseline` to explicitly acknowledge it as a false-positive.



\*\*Step 5 — editable install.\*\* Run `uv pip install -e .` so `import auth\_engine` resolves from `src/` rather than needing to be on `PYTHONPATH` manually. This is what the `src/` layout requires.



One thing to confirm before you run: the `ruff` revision in `.pre-commit-config.yaml` is `v0.15.17` to match what `uv add` installed. If your pinned version in `pyproject.toml` drifts from the pre-commit revision, you'll get inconsistent linting between `uv run ruff` and the hook — so they should stay in sync.

