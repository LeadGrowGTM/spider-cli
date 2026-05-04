# Spider Waterfall — Site Compatibility Benchmarks

Tested: 2026-05-04
Environment: Windows 11, Python 3.11, SeleniumBase 4.48.4, spider_cli 2.51.157
Spider Cloud: 201,113 credits confirmed available

---

## Consolidated Results

| Domain | Tier Required | Strategy | Content | Cost/page | Notes |
|--------|--------------|----------|---------|-----------|-------|
| Apollo | T1 | Spider CLI / plain HTTP | 541KB | $0.00 | Marketing shell — data behind auth |
| LinkedIn Public | T1 | Spider CLI / plain HTTP | 476KB | $0.00 | SSR shell — data behind auth |
| ZoomInfo | T8 | SeleniumBase UC | 9.7KB | $0.00 | Limited public data |
| BBB | T8 | SeleniumBase UC | 241KB | $0.00 | Full directory accessible |
| Owler | T8 | SeleniumBase UC | 259KB | $0.00 | Company profiles accessible |
| RocketReach | T8 | SeleniumBase UC | 167KB | $0.00 | Profile pages accessible |
| Clutch | T8 | SeleniumBase UC | 2.8MB | $0.00 | Full agency directory accessible |
| D&B | T8 | SeleniumBase UC | 4.6MB | $0.00 | Full company directory accessible |
| G2 | BLOCKED | DataDome — all tiers fail | — | — | Per-request reconnect + residential proxy needed |
| Crunchbase | BLOCKED | Cloudflare — all tiers fail | — | — | Enterprise Cloudflare; impenetrable without logged-in cookies |

**Total cost: $0.00**

---

## Pass Details

### Pass 1 — Spider CLI T1 (plain HTTP)
Apollo and LinkedIn return 200 at T1. Both are SSR shells — the JS-rendered company data requires auth. Useful for tech stack detection and page structure, not lead data.

### Pass 2 — Spider Cloud T4-T7
Initial test showed false 401s due to streaming parse bug (`.json()` on chunked response). Fixed to `stream=True` + line-by-line JSON. Retested Crunchbase at T4/T5/T7 — all fail with empty response. Cloudflare blocks Spider Cloud including smart/unblocker mode. 201K credits confirmed available on account.

### Pass 3 — SeleniumBase UC T8 (no cookies)
6/8 bypassed cold. BBB, Owler, RocketReach, Clutch, D&B all yield real content. ZoomInfo returns minimal public data. Crunchbase (Cloudflare) and G2 (DataDome) remain blocked.

---

## Key Findings

1. **UC mode handles most commercial B2B sites for free.** BBB, Owler, RocketReach, Clutch, D&B are legitimate enrichment sources accessible at zero cost.

2. **Spider Cloud T4-T7 advantage is speed/scale, not bypass power.** For the 6 UC-passing sites, Cloud lets you run parallel batches without spinning up Chrome instances. Worth using for bulk enrichment runs once UC confirms a site is accessible.

3. **Two genuinely impenetrable targets:**
   - **Crunchbase** — Enterprise Cloudflare. Cookie injection (logged-in session) is the only viable path.
   - **G2** — DataDome. Requires per-request `uc_open_with_reconnect` + likely residential proxy. Not worth the effort for most use cases.

4. **"Plain HTTP pass" != usable data.** LinkedIn and Apollo return large payloads at T1 but actual contact/company data is gated.

5. **Spider CLI installed** at `spider_cli 2.51.157` via `cargo`. Requires VS 2022 Build Tools (C++ workload) on Windows — one-time install.

---

## Waterfall Correction

Original probe script had two bugs:
- Only implemented T1-T6 (missing T7 unblocker)
- Used `requests.json()` on Spider Cloud's chunked streaming response — caused false "Response ended prematurely" errors at T4-T6

Both fixed. T7 retest on Crunchbase confirmed it still blocks regardless.

---

## Next Steps

- [ ] Retest T4-T7 on BBB/Owler/Clutch/D&B to benchmark Cloud speed vs UC for bulk ops
- [ ] G2: test DataDome per-request reconnect pattern (`uc_open_with_reconnect` on every page)
- [ ] Wire Spider API calls through lg-llm-runtime `tracked_call()` when V3 Track A ships