### Utils and Helpful resources

* [Token Goat - A python based proxy, that helps with token consumption a lot!](https://github.com/DFKHelper/token-goat)
* [Free OpenRouter Models](https://openrouter.ai/openrouter/free)


---

### Models in OpenRouter

#### Free Models ($0 - for Input/Output)

1. [Cohere: North Mini Code](https://openrouter.ai/cohere/north-mini-code:free)
2. [Gemma 4 26B A4B](https://openrouter.ai/google/gemma-4-26b-a4b-it:free)
3. [Gemma 4 31B](https://openrouter.ai/google/gemma-4-31b-it:free)
4. [Qwen3 Next 80B A3B Instruct](https://openrouter.ai/qwen/qwen3-next-80b-a3b-instruct:free)
5. [OpenAI GPT-OSS-120B](https://openrouter.ai/openai/gpt-oss-120b:free)
6. [Qwen3 Coder 480B A35B](https://openrouter.ai/qwen/qwen3-coder:free)
7. [Nous: Hermes 3 405B Instruct](https://openrouter.ai/nousresearch/hermes-3-llama-3.1-405b:free)

#### Notable mentions

8. [NVIDIA Nemotron 3 Nano 30B A3B](https://openrouter.ai/nvidia/nemotron-3-nano-30b-a3b:free)
9. [LiquidAI: LFM2.5 1.2B Instruct](https://openrouter.ai/liquid/lfm-2.5-1.2b-instruct:free)
10. [LiquidAI: LFM2.5 1.2B Thinking](https://openrouter.ai/liquid/lfm-2.5-1.2b-thinking:free)
11. [NVIDIA Nemotron 3 Ultra](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b:free)
12. [NVIDIA Llama Nemotron Rerank VL 1B V2**](https://openrouter.ai/nvidia/llama-nemotron-rerank-vl-1b-v2:free)

** Reranker, not an LLM.

---
> Some reddit discussion threads / online blogs covering the cost - value discussions for different AI plans:

1. [What's the best value subscription for agentic coding right now?](https://www.reddit.com/r/AI_India/comments/1swll5f/whats_the_best_value_subscription_for_agentic/)
2. [AI Coding Tools pricing comparison: What you actually pay in 2026](https://www.developersdigest.tech/blog/ai-coding-tools-pricing-comparison)
3. [What AI coding tools are you all actually paying for right now?](https://www.reddit.com/r/vibecoding/comments/1tc8zl1/what_ai_coding_tools_are_you_all_actually_paying/)

---

> QUESTION: Do we have platform level rate limits, on OpenRouter? If so, they we've to work around that!  
- Need help here, referring to the [OpenRouter Pricing](https://openrouter.ai/pricing) page, it looks like, I can find the following info:

`Rate limits => High global limits` (for Pay-as-you-go tier).
- `Input and output tokens are billed per model at posted rates.`
- `We do not mark up provider pricing. Pricing shown in the model catalog is what you pay which is exactly what you will see on provider's websites.`
- `Pay-as-you-go: You buy credits and use them as you wish. You can automatically top-up your account or do it manually. You can see the activity in your settings > API Keys`
- `No. When routing/fallback is enabled, you're billed only for the successful model run.`
- `No. Pricing is per token regardless of streaming. You pay only for successful runs when routing/fallback is enabled.`
- On Rate Limits:  
```
Q: Do you enforce rate limits?
A: For free plan - Yes. Not for Pay-as-you-go or Enterprise plans.

Yes. Different plans have different limits.

Free users have a limit of 50 requests per day and 20 requests per minute (rpm)
For pay-as-you-go users with at least $10 in credits -
No limits on paid models
1000 request limit on free models with 20 RPM
Free‑tier usage of popular models can be subject to rate limiting by the provider, especially during peak times. Failed attempts still count toward your daily quota.
```
- `Routing/fallback can automatically try alternative models. You're billed only for the successful runs. Every request has Zero Completion Insurance.`
- Model pricing changes:
```
Q: What happens if a model is depricated or pricing changes?
A: If a model is deprecated, you will receive a 404 when you request it, with an error message like "no endpoints for this model found."

If the pricing changes, we will continue to route to the model and it will serve your requests. But, you will be charged at the new rate and your credits will deduct accordingly. This will be reflected in your billing.
```
- Data Retention:
```
Q: Do you train on customer data?
A: No. We do not train on your data. Provider‑side retention can be disabled at the account level or per API call.
```

---  

So, this is my qualm.
I want to be able to leverage / get as much value out of different plans from different vendors, for as little as I possibly can (spend).
Optionally, I'm looking to get as much value out of the afforded requests per day quota.
Looking through multiple reddit discussion threads, or even at the OpenRouter FAQ's I'm thinking of doing one of the following:
- Purchase a minimum of $10 worth of credits on months where I'm feeling motivated to build something, etc. on OpenRouter -> which takes my requests/day quota to 1000/day & 20/min. $10 would roughly amount to like INR.1000/- which is completely fine for the benefits I get, and in the months that I'm not using much, I would rather just stick to the monthly 50 requests tier! Use the free models listed on the first section (OSS free models) for Agentic tasks [am assuming from what I read previously, that OpenRouter exposes models through OpenAI's API spec style - which means that using these models in Codex-CLI should be easy!] - as my agentic development workflow / toolkit, and trying to hard-constraint myself to like 250 requests per-weekend, on the 1000 available quota per month [since I'll be doing these extensive developments only in the weekends!] - and in months where there's a 5th week, I'll try to leverage maybe other models / plan accordingly. Maybe make it 200 requests per weekend!
- Purchase a Claude Pro ($20 subscription -> roughly translates to about INR.2200-ish after GST & conversion rate application), and use that in a limited manner everyday within the 5 hour limit (which albeit will be very low on weekends, I won't be able to progress much at all, and will be left frustrated - lowest preference plan!)
- Or, purchase a [Google AI Pro](https://gemini.google/subscriptions/#footnote:usage_limits) subscription for like 1.9k INR (directly priced in INR), and being able to avail what's captured as 4x more usage limits than the standard tier (which on relative terms doesn't give any sort of scale, cause 1- I'm not a big Gemini User, and 2-doesn't have any info on what on average amounts as a Standard limit on the free tier!) - which can be used in AntiGravity! Ofc, this means that it's not stopping at just Gemini, but also gives NotebookLM higher limits (5x more), Gemini access directly in Google Apps, YouTube Premium Lite Plan [which honestly doesn't make a difference cause I use brave, and I get all of those perks and more for free already!], and like 5TB of additional storage across Gmail, drive and photos, which again I don't think neither me nor my family (mom/brother) are going to take much / any advantage of.

I'm ofc, at this moment, leaning towards the OpenRouter approach / route. It's very flexible, and I can use close to only INR-1000 on only the months I really need it, for like super-cool amount of limits.
I need your help, and detailed due diligence to look for:
- best value for money choices [amongst available choices - not limited to only things, I've highlighted! But also other attractive / good choices / deals. Maybe some of them can be referred to from the reddit / attractive / good choices / deals. Maybe some of them can be referred to from the reddit / other link sections area.]
- What will fit my needs, if I plan to develop apps (medium sized repo's or make edits to them after development actively, majorly on weekends for quite a bit of time) and also to use the LLM's to help me learn and improve my knowledge?
- Mis-understandings I've had on any proposals  I've made so far...

---  

For the web-search API's can we not use a combination of:
- Tavily Search
- Exa search
- Linkup Search
- Perplexity Search?
- Apify
??
The primary reason for a search-tool is to identify live, upto date information from different references.
Or maybe just simply setup a playright mcp that has access to a web-browser, bam, that should do it then, no?
or a custom search tool, that uses a local fine-tuned model maybe, that can browse the web and figure out the answers needed??

Not the most efficient of the solutions, but I'm just leaning towards the OpenRouter pathway still, man!
It's very lineant usage limits - 1000 req's per day will be good enough for me on weekends!
For scarce web-searches, maybe if they're necessary I can change my workflow to pool them together into a specific phased search strategy; even do the searching myself - I might discover some things myself [I know this is soo counter-intuitive and I'm sounding like a joker, but I can't help it man!]

---
