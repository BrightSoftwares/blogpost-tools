# blogpost-tools
Automation tools for blog posts


## How to generate a token to check runners availability

Here are the permissions to add

![image](https://github.com/BrightSoftwares/blogpost-tools/assets/774136/2ecfa124-8879-4397-a9c5-b876e6127a17)


## GitHub Actions Runner Strategy

### Wave 1 — Permanent Self-Hosted Repos (stay on self-hosted)

These repos run high-frequency content workflows and are permanently migrated to the home-lab self-hosted runner:

| Repo | Reason |
|------|--------|
| `joyousbyflora-posts` | 608 min/mo (featured-image-finder alone) |
| `eagles-techs.com` | Content blog — high workflow volume |
| `ieatmyhealth.com` | Content blog — high workflow volume |
| `foolywise.com` | Content blog — high workflow volume |
| `keke.li` | Content blog — high workflow volume |
| `modabyflora-corporate` | Content blog — high workflow volume |
| `hognekaba-backend` | Backend deploy workflow |
| `n8n-heroku` | Docker build + deploy workflow |

### Wave 4 — Watchlist (monitor; revert to ubuntu-latest after 2026-06-02 free tier reset)

These repos use GitHub-hosted runners for CI/testing — acceptable usage per wave analysis:

| Repo | Est. Usage | Notes |
|------|-----------|-------|
| `notiwise` | ~39 min/mo | CI + deploy; quality gates required |
| `pilotflow-with-zippy` | ~86 min/mo | CI + deploy; OAuth verification in progress |
| `smart-assets-manager` | ~21 min/mo | CI tests + FastAPI deploy |
| `duolingo-clone` | ~24 min/mo | CI only; Netlify deploys externally |
| `transaction-taxonomy` | ~5 min/mo | Model training; infrequent |

**Total watchlist usage:** ~175 min/mo — well under the 2,000 min free tier.

**Monitoring rule:** If GitHub-hosted minutes exceed 1,500 for 2 consecutive months, move the top consumer from this watchlist to self-hosted.

### Runner Toggle (Option C — set-runner-mode.yml)

Run `set-runner-mode.yml` via workflow_dispatch in `blogpost-tools` to toggle all repos:
- `mode=self-hosted` — switch all content repos to self-hosted (use during free-tier exhaustion)
- `mode=ubuntu-latest` — revert watchlist repos to GitHub-hosted (use on free-tier reset, 1st of each month)

See `set-runner-mode.yml` for configuration.
