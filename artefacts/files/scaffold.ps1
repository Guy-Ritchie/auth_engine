# Phase 0 — directory scaffold
# Run from: C:\Users\rinzler\Documents\learning\python\auth_engine
#
# What this does:
#   - Removes the flat-layout main.py (uv init default — not what we want)
#   - Creates the src/auth_engine package hierarchy
#   - Stubs the three UI HTML files (login + two role pages)
#   - Creates empty test directories with placeholder conftest files
#   - Creates the detect-secrets baseline (must run before first commit)

# 1. Remove the flat-layout default file created by uv init
Remove-Item main.py -ErrorAction SilentlyContinue

# 2. Source layout — the package lives at src/auth_engine/
$dirs = @(
    "src\auth_engine\crypto",
    "src\auth_engine\db\repositories",
    "src\auth_engine\domain",
    "src\auth_engine\auth\basic",
    "src\auth_engine\auth\session",
    "src\auth_engine\auth\token",
    "src\auth_engine\auth\oauth",
    "src\auth_engine\authz\rbac",
    "src\auth_engine\authz\abac",
    "src\auth_engine\authz\pbac",
    "src\auth_engine\web",
    "src\auth_engine\ui",
    "tests\unit\crypto",
    "tests\unit\auth",
    "tests\unit\authz",
    "tests\integration",
    "tests\regression",
    "llm"
)

foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

# 3. __init__.py files — one per package directory.
#    Kept empty at scaffold time; will receive re-exports as each module is built.
$packages = @(
    "src\auth_engine",
    "src\auth_engine\crypto",
    "src\auth_engine\db",
    "src\auth_engine\db\repositories",
    "src\auth_engine\domain",
    "src\auth_engine\auth",
    "src\auth_engine\auth\basic",
    "src\auth_engine\auth\session",
    "src\auth_engine\auth\token",
    "src\auth_engine\auth\oauth",
    "src\auth_engine\authz",
    "src\auth_engine\authz\rbac",
    "src\auth_engine\authz\abac",
    "src\auth_engine\authz\pbac",
    "src\auth_engine\web"
)

foreach ($p in $packages) {
    $init = "$p\__init__.py"
    if (-not (Test-Path $init)) {
        New-Item -ItemType File -Path $init | Out-Null
    }
}

# 4. Stub conftest files for pytest (prevents "no tests" hard-fail on hook)
@"
"""Shared pytest fixtures for the auth_engine test suite.

Fixtures defined here are available to all tests without explicit import.
Test-category-specific fixtures live in conftest.py files within each
subdirectory (tests/unit/, tests/integration/).
"""
"@ | Set-Content -Encoding utf8 tests\conftest.py

@"
"""Fixtures specific to unit tests.

Unit tests are isolated — no I/O, no database, no network.
External dependencies are replaced with fakes or stubs.
"""
"@ | Set-Content -Encoding utf8 tests\unit\conftest.py

# 5. Placeholder to keep regression/ tracked by git (git ignores empty dirs)
"" | Set-Content tests\regression\.gitkeep
"" | Set-Content tests\unit\crypto\.gitkeep
"" | Set-Content tests\unit\auth\.gitkeep
"" | Set-Content tests\unit\authz\.gitkeep

# 6. detect-secrets baseline — run AFTER copying pyproject.toml and .pre-commit-config.yaml
#    but BEFORE the first `git commit`. Generates .secrets.baseline which must be committed.
Write-Host ""
Write-Host "Scaffold directories created." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps (run in order):" -ForegroundColor Yellow
Write-Host "  1. Copy pyproject.toml and .pre-commit-config.yaml into the project root"
Write-Host "  2. uv add --dev detect-secrets"
Write-Host "  3. uv run detect-secrets scan > .secrets.baseline"
Write-Host "  4. pre-commit install"
Write-Host "  5. pre-commit run --all-files   # should pass cleanly"
Write-Host "  6. git add -A"
Write-Host '  7. git commit -m "chore(scaffold): migrate to src layout, configure ruff/mypy/detect-secrets/pytest"'
