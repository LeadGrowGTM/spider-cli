# Spider â€” LeadGrow Usage Guide

Fork of [spider-rs/spider](https://github.com/spider-rs/spider). Documents how LeadGrow uses Spider across our scraping pipeline.

## Scraping Waterfall

Start at Tier 1. Escalate only when the current tier fails or is blocked. Never jump tiers preemptively â€” the cheap path is almost always faster and sufficient.

| Tier | Tool | Cost | When to Use |
|------|------|------|-------------|
| 1 | Spider CLI â€” HTTP mode | Free | Static pages, link maps, no JS required |
| 2 | Spider CLI â€” headless (`--headless`) | Free | JS-rendered, no bot protection present |
| 3 | Spider CLI â€” stealth headless | Free | Light bot detection, fingerprinting |
| 4 | Spider Cloud API â€” basic (`request: http`) | ~$0.001/page | Batches >50 URLs, can't install Rust locally |
| 5 | Spider Cloud API â€” chrome + readability | ~$0.005/page | JS-heavy sites, need clean markdown for LLM input |
| 6 | Spider Cloud API â€” proxy enabled | ~$0.0075/page | Rate-limited or geo-restricted sites |
| 7 | Spider Cloud â€” unblocker mode | ~$0.01/page | Moderate bot protection (not DataDome/CF challenges) |
| 8 | SeleniumBase UC (Python) | Time only | DataDome, Cloudflare JS challenges â€” last resort |

**Tiers 1-3:** Spider CLI binary (this repo). Install: `cargo install spider_cli`
**Tiers 4-7:** Spider Cloud API. Clients in `gtme-skills/skills/*/spider_client.py` and `leadgrow-hq/tools/playbook-engine/src/spider.ts`
**Tier 8:** Separate tool. See `leadgrow-hq/gtme-skills/skills/web-scraper/`

## Escalation Decision

```
Try CLI HTTP â†’ blocked/empty? â†’ Try CLI headless â†’ JS challenge? â†’ Try Cloud chrome
â†’ rate limited? â†’ Add proxy â†’ bot protected? â†’ Use unblocker
â†’ DataDome/CF challenge? â†’ Drop to SeleniumBase (Tier 8)
```

If a site is known-hard (DataDome confirmed, Cloudflare JS verified), skip directly to Tier 8. Don't waste 7 attempts on it.

## Spider CLI â€” Standard Commands

**Research crawl (playbook research, competitor intel):**
```bash
spider --url https://example.com --return-format markdown --limit 25 --depth 2 scrape --output-html
```

**Link map (directory structure, site audit):**
```bash
spider --url https://example.com --limit 50 crawl --output-links
```

**Full-site download (offline analysis):**
```bash
spider --url https://example.com download -t _temp_downloads
```

**JS-rendered page (headless):**
```bash
spider --url https://example.com --headless scrape --output-html
```

**Stealth + headless:**
```bash
spider --url https://example.com --stealth --headless scrape --output-html
```

**With auth cookie:**
```bash
spider --url https://example.com --cookie "session=abc123; token=xyz" scrape --output-html
```

**With proxy:**
```bash
spider --url https://example.com --proxy-url http://proxy:8080 --stealth scrape --output-html
```

**Spider Cloud unblocker via CLI:**
```bash
spider --url https://example.com --spider-cloud-key $SPIDER_API_KEY --spider-cloud-mode unblocker scrape --output-html
```

## Spider Cloud API â€” Standard Usage

**Python (single page, readability on):**
```python
from spider_client import fetch_page
result = await fetch_page(url, readability=True, return_format="markdown")
```

**Python (batch, rate-limited):**
```python
from spider_client import fetch_pages_batch
results = await fetch_pages_batch(urls, concurrency=5, delay=0.2)
```

**Python (proxy for rate-limited site):**
```python
result = await fetch_page(url, use_proxy=True)
```

**Python (full page, no readability â€” for signal detection):**
```python
result = await fetch_page(url, readability=False, return_format="raw")
```

**TypeScript/Bun (playbook engine):**
```typescript
import { spiderCrawl } from "./spider";
const { pages, costDollars } = await spiderCrawl(url, { limit: 10, depth: 1 });
```

**Check cost before batch runs:**
```python
from spider_client import estimate_cost
print(estimate_cost(len(urls)))  # shows $/page and total before committing
```

## Standard Flag Reference

| Flag | Default | Purpose |
|------|---------|---------|
| `--limit` | unlimited | Max pages to crawl. Use 25 for research, 10 for quick intel |
| `--depth` | unlimited | Max crawl depth. Use 1-2 for most tasks |
| `--return-format markdown` | raw | Convert HTML to markdown (LLM input) |
| `--headless` | off | Enable browser rendering (JS sites) |
| `--stealth` | off | Bot detection evasion |
| `--delay` | 0 | Polite delay between requests (ms) |
| `--respect-robots-txt` | off | Honor robots.txt |
| `--block-images` | off | Skip image loading (faster headless) |
| `readability=True` (API) | True | Strip nav/footer. Set False for signal detection |

## Rules

- **CLI before Cloud.** CLI is free. Cloud costs credits. Only upgrade when CLI fails.
- **`--limit 25 --depth 2`** is the standard research crawl. Don't over-crawl â€” extra pages rarely add value.
- **`--return-format markdown`** for any output going into an LLM prompt.
- **`readability=True`** (API) for clean content. `readability=False` when you need nav/footer signals (tech stack detection, page structure analysis).
- **`estimate_cost()` before any batch run >50 URLs.**
- **Never hardcode `SPIDER_API_KEY`.** Load from `.env` only.
- **`block-images` + `stealth` together** for headless runs on commercial sites â€” faster and less fingerprint surface.

## Use Cases by Task

| Task | Tier | Command/Method |
|------|------|----------------|
| Competitor homepage intel | 1 | CLI HTTP, `--return-format markdown --limit 1` |
| Competitor full site crawl | 1 | CLI HTTP, `--limit 25 --depth 2` |
| Playbook research | 1-2 | CLI HTTP first, headless if empty |
| Company website enrichment (batch) | 4-5 | Cloud API, `fetch_pages_batch` |
| JS-heavy SaaS site | 2-3 | CLI headless + stealth |
| Gated/auth-walled content | 2 + cookie | CLI headless + `--cookie` |
| Protected site (no DataDome) | 7 | Cloud unblocker mode |
| DataDome-protected | 8 | SeleniumBase UC â€” skip all Spider tiers |

## When NOT to Use Spider

- **Paginated list scraping** (directories, search results, member databases) â†’ use `web-scraper` skill (SeleniumBase + BS4 decision tree)
- **LinkedIn** â†’ use linkedin skill
- **DataDome / Cloudflare JS challenge confirmed** â†’ go straight to SeleniumBase UC (Tier 8)
- **Need structured CSV with field mapping** â†’ web-scraper skill templates
- **Firecrawl** â†’ not used. SeleniumBase UC is the terminal fallback.

## Installation

```bash
# CLI (Rust binary)
cargo install spider_cli

# With smart mode (HTTP-first, browser fallback)
cargo install -F smart spider_cli

# Python Cloud API client
pip install aiohttp python-dotenv

# Required env var
SPIDER_API_KEY=your_key_here  # get from spider.cloud dashboard
```
