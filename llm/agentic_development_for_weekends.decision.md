# Agentic Development for Weekends — Decision Record

**Date:** 2026-06-20
**Status:** Decided, pending implementation

## Context

Need: a low/no-cost setup for weekend-only usage covering two distinct workloads:
1. Conversational tutoring — concepts, reference-document curation, exercises with critique.
2. Sparse, deliberately friction-ful coding assistance — most code written by hand; agent used occasionally, not as a default autopilot.

Constraints: spend as little as possible, prefer pay-only-in-motivated-months flexibility, purely local/CLI workflow (no CI/CD), already has Cursor + Azure OpenAI/Codex-CLI access at work and is actively trying to *unlearn* trigger-happy agentic habits, not reinforce them.

## Decision

**Infrastructure:** OpenRouter, pay $10 once (lifetime, non-recurring) to unlock 1,000 free-model requests/day, 20 req/min.

**Coding harness:** Codex CLI, repointed at OpenRouter via a custom `model_providers` block.

**Search tool:** Self-built MCP server wrapping Tavily (primary) with Perplexity and/or Exa as fallback, registered as an MCP server in Codex CLI config — not Codex's native `web_search`, which is OpenAI-hosted and doesn't function once routed through OpenRouter to non-OpenAI models.

**Usage pattern:** Free OpenRouter models, used in low-traffic weekend windows (early mornings) to reduce shared-pool congestion.

**Tutoring/learning:** Conversational, via whichever free-tier chat product is convenient in the moment (Claude.ai / ChatGPT / Gemini) — no dedicated paid subscription committed to at this time. Revisit only if free-tier session walls become a recurring weekend blocker.

## Why this beats the alternatives considered

| Option | Why not (for this use case) |
|---|---|
| Claude Pro ($20/mo) | Good quality, but recurring cost for a workload that's intentionally low-volume and chat-shaped, not infra-shaped. Revisit only if free tiers prove insufficient. |
| Google AI Pro (₹1,950/mo) | Moved to a compute-based usage system (May 2026) — limits now vary by prompt complexity/length rather than a fixed quota, making weekend-marathon usage less predictable. |
| GLM Coding Plan (Z.ai) | Strong value, Claude Code-compatible, but pricing has been unstable through 2026 (promo removed Feb 2026; current public listings disagree, $3–19/mo range) and is built for agentic dev volume, not the tutoring-first workload here. Worth a second look only if the agentic-coding side of usage grows substantially. |
| Cursor / GitHub Copilot | Solves a problem (in-editor agentic coding at scale) this workflow is deliberately avoiding. Already have generous Cursor access at work — point of this setup is to *not* replicate that habit on weekends. |
| Playwright MCP for search | Free and flexible, but slower, more brittle (JS-rendered pages, cookie banners), and token-expensive (dumps raw page content into context) versus a purpose-built search API. |
| Combining all 5 search APIs (Tavily + Exa + Linkup + Perplexity + Apify) | Unnecessary integration surface for the usage scale involved. Tavily's free tier (1,000 credits/mo) alone covers far more than a weekend's worth of searches. |

## Key corrections made during this analysis

1. **"1 request" ≠ "1 task" in agentic coding.** Each tool-call turn in an agentic loop (read file, run command, edit, check) is its own API request. A single feature/bugfix can burn 15–50+ requests. Budget OpenRouter quota in *sessions*, not raw request count — though this matters less here since the primary workload is conversational, not agentic-loop-heavy.
2. **Free-tier shared pools congest exactly when you'll use them.** Weekend peak usage = more contention on free-model backends, independent of your own quota headroom.
3. **Codex CLI's native `web_search` is OpenAI-hosted** — it does not work once `model_provider` is repointed at OpenRouter for non-OpenAI models. A self-hosted MCP search server is required, not optional.
4. **Codex CLI config gotchas (post-Feb 2026 breaking changes):**
   - Must set `wire_api = "responses"` explicitly for any custom provider — the older `chat` protocol was removed.
   - Cannot name a custom provider `openai`, `ollama`, or `lmstudio` — these IDs are reserved. Use a distinct name (e.g. `openrouter`).
5. **Claude Pro's 5-hour window resets on a rolling basis**, not once per day — undersold in the original framing, though still not generous enough to justify the recurring cost for this specific workload.
6. **Google AI Pro's usage model changed** from a fixed multiplier to compute-based limits (May 2026) — "4x free tier" is no longer an accurate mental model.

## Minimal config skeleton (Codex CLI + OpenRouter + MCP search)

```toml
# ~/.codex/config.toml

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
wire_api = "responses"

model = "qwen/qwen3-coder:free"   # swap per session
model_provider = "openrouter"

[mcp_servers.search_proxy]
command = "node"
args = ["/path/to/search-mcp-server/index.js"]
```

## Open items / revisit triggers

- [ ] Build the search-proxy MCP server (Tavily primary, Perplexity/Exa fallback).
- [ ] Verify `wire_api = "responses"` + reserved-provider-name gotchas against current Codex CLI version before first session.
- [ ] If free-tier chat products start walling off mid-session most weekends → reconsider a single-month Claude Pro or Google AI Pro purchase, cancel after the sprint.
- [ ] If agentic (not conversational) coding volume grows materially → re-evaluate GLM Coding Plan once its 2026 pricing stabilizes.
- [ ] Re-check OpenRouter free-tier congestion in practice during early-morning weekend windows; adjust timing if still throttled.
