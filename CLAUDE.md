# Parachute - Project Reference

## Repository Structure
- `parachute_master/` — Primary codebase (was a git submodule, now inline)
- `parachute_develop/` — Development/experimental branch code (gitignored, has secrets)
- `config/config.py` — Local-only config (gitignored), provides: `FC`, `BADGE`, `FCMPASS`, `DUMMY_CONTAINER`, `SCRIPTS_DIR`, `TEST_EMAIL`, `TEST_MODE`, `OWNER`
- `.env` — Provides `FIREFOX_PROFILE_DIR`

## Active Work Area: turbo_ps
**Location:** `parachute_master/scripts/turbo_ps/`

### Architecture
5-thread daemon automating Amazon FC container problem-solve using Selenium:

```
Container Research (watch_ps) — polls Flow Sortation every 5s
    |
    v  [adds to DJ buffer]
Directed Jackpot (inf_parse) — scans containers via JS, categorizes:
    |-- invalid_container --> Sideline (mark overage) + Slack alert
    |-- invalid_routing   --> Unbind --> back to DJ buffer
    |-- virtually_empty   --> FC Research --> Sideline (adjustment)
    '-- good_work         --> dropped (no action needed)
```

### Key Files
| File | Purpose |
|------|---------|
| `scripts/turbo_ps/main.py` | Entry point: driver pool + continuous loop |
| `scripts/turbo_ps/turbo_ps.py` | Thread orchestrator, driver pool management |
| `src/ampy/integrations/firefox.py` | Centralized driver factory + auth (A-to-Z, FCMenu + site selection) |
| `src/ampy/integrations/container_research.py` | Flow Sortation queries |
| `src/ampy/integrations/dj.py` | Directed Jackpot container classification |
| `src/ampy/integrations/sideline.py` | AFT Poirot overage/adjustment processing |
| `src/ampy/integrations/unbind.py` | Unbind Hierarchy tool |
| `src/ampy/integrations/fc_research.py` | FC Research for virtually empty containers |
| `src/ampy/integrations/slack.py` | Slack webhook notifications |

### Known Issues / Patterns
- **Thread death is silent**: Each `inf_*` loop wraps the entire while-loop in one try/except. A single unhandled exception kills the thread with only a log entry.
- **DJ `process_container` returns None on exception**: Container gets silently dropped from the pipeline instead of retried or logged as lost.
- **Logging was mostly commented out in DJ**: Key processing/result log lines were disabled.
- **FCMenu site selection**: Fixed in firefox.py — now auto-enters FC into qlInput after login.

### Internal Amazon Tools Used
- Flow Sortation: `https://flow-sortation-na.amazon.com/{FC}/`
- FCMenu: `https://fcmenu-iad-regionalized.corp.amazon.com/`
- AFT Poirot: `https://aft-poirot-website-iad.iad.proxy.amazon.com/`
- Unbind Hierarchy: `http://tx-b-hierarchy-iad.iad.proxy.amazon.com/unbindHierarchy`
- FC Research: `http://fcresearch-na.aka.amazon.com/{FC}/`

## Development Notes
- No tests — this is a local automation tool, not deployed software
- Python + Selenium + Firefox with profile-based auth
- `config.py` is gitignored; must exist locally at `parachute_master/config/config.py`
- Thread communication uses `collections.deque` (thread-safe for append/popleft)
