# Spider Waterfall â€” Site Compatibility Benchmarks

Tested: 2026-05-04  
Environment: Windows 11, Python 3.11, SeleniumBase 4.48.4  
Spider CLI: not installed during this run (requires `cargo install spider_cli`)  
Spider Cloud: account requires credits for Tiers 4-7  

---

## Full Results

### Pass 1 â€” Plain HTTP (Tier 1 equivalent via `requests`)

| Domain | URL | Result | Size | Cost |
|--------|-----|--------|------|------|
| LinkedIn Public | linkedin.com/company/salesforce | **PASS** | 476KB | $0.00 |
| Apollo | apollo.io/companies | **PASS** | 541KB | $0.00 |
| Crunchbase | crunchbase.com/organization/salesforce | BLOCKED | â€” | $0.00 |
| ZoomInfo | zoominfo.com/c/salesforce-com/4835324 | BLOCKED | â€” | $0.00 |
| BBB | bbb.org/us/ca/san-jose/category/computer-software | BLOCKED | â€” | $0.00 |
| Owler | owler.com/company/salesforce | BLOCKED | â€” | $0.00 |
| RocketReach | rocketreach.co | BLOCKED | â€” | $0.00 |
| G2 | g2.com/products/salesforce-sales-cloud/reviews | BLOCKED | â€” | $0.00 |
| Clutch | clutch.co/agencies/digital-marketing | BLOCKED | â€” | $0.00 |
| D&B | dnb.com/business-directory | BLOCKED | â€” | $0.00 |

**2/10 passed plain HTTP. $0.00.**

---

### Pass 2 â€” Spider Cloud API Tiers 4-7 (chrome, proxy, unblocker)

All 8 blocked sites attempted via Spider Cloud API.  
**Result: 0/8 passed. Root cause: API account had no credits (401 Unauthorized).**  
Tier 4-7 results were silently swallowed as empty responses in the probe script â€” not genuine bot-protection blocks.  
**Note:** With a funded Spider Cloud account, Tiers 4-7 should be retested before concluding these sites are impenetrable.

---

### Pass 3 â€” SeleniumBase UC Mode (Tier 8, no cookies)

| Domain | Result | Size | Protection Type | Cost |
|--------|--------|------|----------------|------|
| ZoomInfo | **PASS** | 9.7KB | None (plain JS render) | $0.00 |
| BBB | **PASS** | 241KB | None at UC level | $0.00 |
| Owler | **PASS** | 259KB | None at UC level | $0.00 |
| RocketReach | **PASS** | 167KB | None at UC level | $0.00 |
| Clutch | **PASS** | 2.8MB | None at UC level | $0.00 |
| D&B | **PASS** | 4.6MB | None at UC level | $0.00 |
| Crunchbase | **BLOCKED** | â€” | Cloudflare JS challenge | $0.00 |
| G2 | **BLOCKED** | â€” | DataDome captcha | $0.00 |

**6/8 bypassed with UC alone. $0.00. 2 require additional escalation.**

---

## Consolidated Summary

| Domain | Tier Required | Strategy | Cost/page | Notes |
|--------|--------------|----------|-----------|-------|
| LinkedIn Public | T1 | Plain HTTP | $0.00 | SSR shell only â€” actual data requires auth |
| Apollo | T1 | Plain HTTP | $0.00 | Marketing shell â€” company data requires auth |
| ZoomInfo | T8 | SeleniumBase UC | $0.00 | Passes UC, but 9.7KB = limited public data |
| BBB | T8 | SeleniumBase UC | $0.00 | Full directory content accessible |
| Owler | T8 | SeleniumBase UC | $0.00 | Company profile content accessible |
| RocketReach | T8 | SeleniumBase UC | $0.00 | Profile page accessible |
| Clutch | T8 | SeleniumBase UC | $0.00 | Full agency directory accessible |
| D&B | T8 | SeleniumBase UC | $0.00 | Full company directory accessible |
| Crunchbase | T8+ | UC + cookie injection OR Cloud unblocker | ~$0.01 | Cloudflare â€” needs logged-in cookies or funded Cloud account |
| G2 | T8+ | UC + per-request reconnect OR Cloud unblocker | ~$0.01 | DataDome â€” hardest class, per-request reconnect pattern |

**Total cost for full benchmark run: $0.00**

---

## Key Findings

1. **UC mode bypasses most commercial sites for free.** BBB, Owler, RocketReach, Clutch, D&B all yield content with zero cost. These are legitimate enrichment data sources.

2. **"Plain HTTP pass" doesn't mean usable data.** LinkedIn and Apollo return large SSR shells at T1, but the actual company/contact data is behind auth. Don't confuse page size with data availability.

3. **Spider Cloud API (Tiers 4-7) needs a funded account to test.** All Cloud tier failures in Pass 1 were 401s, not genuine bot blocks. Retest with credits â€” especially for Crunchbase and G2 where UC fails.

4. **Two genuinely hard targets:**
   - **Crunchbase:** Cloudflare JS challenge. Cookie injection (logged-in browser session) is the cleanest path.
   - **G2:** DataDome. Requires `uc_open_with_reconnect` on every page request (not just initial load). May still fail without residential proxy.

5. **Spider CLI not installed.** `cargo install spider_cli` needed to test Tiers 1-3 properly. Tiers 1-3 should handle static marketing sites and documentation pages well before reaching UC.

---

## Waterfall Gap: T7 Missing from Initial Probe

The initial waterfall probe script only implemented up to T6 (Chrome + proxy). T7 (unblocker/smart mode) was not tested. When Cloud credits are available, retest Crunchbase and G2 specifically with `request: "smart"` â€” Spider's unblocker is designed for Cloudflare and DataDome scenarios.

---

## Next Steps

- [ ] Fund Spider Cloud account and retest T4-T7 on Crunchbase + G2
- [ ] Install Spider CLI (`cargo install spider_cli`) and validate T1-T3 on static sites
- [ ] Cookie injection test: Crunchbase logged-in session
- [ ] Wire Spider API calls through lg-llm-runtime `tracked_call()` when V3 Track A ships
