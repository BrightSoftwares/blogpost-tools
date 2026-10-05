# Jekyll fleet tooling

One home (this repo) for everything the Jekyll sites share, so a fix is made once instead of once per site.

| Concern | Shared piece | Where |
|---|---|---|
| `[[wikilinks]]` | gem `jekyll-obsidian-wikilinks` (consumed via `git:` in each Gemfile) | `jekyll-plugins/jekyll-obsidian-wikilinks/` |
| Plugin CI | `reusable_jekyll-plugin-tests.yml` (+ caller `jekyll-plugin-tests.yml`) | `.github/workflows/` |
| Dependency audit | `reusable_jekyll-dependency-audit.yml` (bundler-audit + pip-audit), caller template in `.github/workflows/examples/jekyll-dependency-audit.yml` | `.github/workflows/` |
| Dependabot config | canonical template, rendered per repo | `scripts/jekyll_fleet/templates/dependabot.yml` |
| Fleet visibility | `fleet_dependabot_report.py` (read-only table), `fleet_apply_dependabot_config.py` (dry-run default, `--apply` opens one PR per repo on `claude/automated-work`) | `scripts/jekyll_fleet/` |

Repo list: `scripts/jekyll_fleet/fleet_repos.txt`. Both scripts need `GITHUB_TOKEN` (never printed) and are unit-tested with mocked HTTP (`tests/jekyll_fleet`, workflow `jekyll-fleet-tests.yml`).

```bash
export GITHUB_TOKEN=...   # alerts:read + contents:write (apply only)
python3 scripts/jekyll_fleet/fleet_dependabot_report.py --repos scripts/jekyll_fleet/fleet_repos.txt
python3 scripts/jekyll_fleet/fleet_apply_dependabot_config.py --repos scripts/jekyll_fleet/fleet_repos.txt           # dry-run
python3 scripts/jekyll_fleet/fleet_apply_dependabot_config.py --repos scripts/jekyll_fleet/fleet_repos.txt --apply   # writes
```

## Why a git-sourced gem for wikilinks

Sites build with `bundle exec jekyll build` in GitHub Actions and ship by FTP/SSH to o2switch (no GitHub-Pages builder), so a custom gem is allowed. This repo is public, so Bundler can fetch `git:` + `glob:` with no token in CI.

| Option | Verdict |
|---|---|
| Copy `_plugins/wikilinks.rb` into each repo (what `audit-and-align-jekyll-repos/scripts/deploy-wikilinks.sh` did) | Rejected: it produced the drift measured below - 8 identical copies, none with the code-block fix. Every fix needs N PRs. |
| Reusable workflow that re-syncs `_plugins/` | Rejected: still N copies, commits to every repo on every change. |
| Publish to rubygems.org | Possible later (needs the owner's account); `git:` gives the same one-line adoption without it. |
| **Git-sourced gem, pinned by tag** | **Chosen**: 1 line per site, `bundle update` to upgrade, Dependabot bundler can bump the tag, tests live next to the code. |

Trade-off: sites pin a tag, so a fix still needs one lockfile bump per site - but a bump (Dependabot PR) replaces hand-porting code.

### Adopting the gem (3 lines per site)

1. Add to `Gemfile` (`group :jekyll_plugins`): `gem 'jekyll-obsidian-wikilinks', git: 'https://github.com/BrightSoftwares/blogpost-tools.git', glob: 'jekyll-plugins/jekyll-obsidian-wikilinks/*.gemspec', tag: 'jekyll-obsidian-wikilinks-v2.1.0'`
2. `git rm _plugins/wikilinks.rb && bundle install`, then verify with `bundle exec jekyll build` and commit `Gemfile` + `Gemfile.lock`.
3. Add `.github/dependabot.yml` (see apply script) so tag bumps arrive automatically.

## Inventory (2026-10-05)

Source: GitHub REST API with the owner's token over all 183 non-archived repos visible to it in `BrightSoftwares/*` and `sergioafanou/*` (+ `sergioafanou/smart-cv`, which the listing endpoint does not return but is accessible). 11 have a `Gemfile` that requires `jekyll`; `sergioafanou/latexcv` has a `_config.yml` but no Gemfile (not a Jekyll bundle).

| Repo | Default branch | Last push | Local plugins | Gemfile.lock last commit | dependabot.yml | Open alerts (H/M/L) | Notes |
|---|---|---|---|---|---|---|---|
| BrightSoftwares/automatic-app-landing-page | master | 2023-11-26 | - | 2019-01-24 | no | n/a (403) | fork, stale (2023); alerts API 403 |
| BrightSoftwares/corporate-website | master | 2026-10-05 | adstxt_converter.rb, algolia_hooks.rb, cache_buster.rb, duplicate_url_check.rb, hex_to_rgb.rb, img-tag-transform.rb, jekyll_minimagick.rb.bak, last_modified_at_virtual_page_guard.rb, my-minimagik.rb.bak, wikilinks.rb | 2022-01-15 | no | 7/14/1 | also nested `_data/cleanup_scripts/Pipfile.lock` (17 pip alerts) |
| BrightSoftwares/eagles-techs.com | main | 2026-09-29 | wikilinks.rb | 2025-12-04 | no | 5/7/10 | git tree truncated (~39k files) |
| BrightSoftwares/foolywise.com | main | 2026-09-25 | wikilinks.rb | 2026-04-30 | no | n/a (403) | Dependabot alerts DISABLED; commits `vendor/bundle/` |
| BrightSoftwares/hosting_frontend | gh-pages | 2023-11-26 | - | 2020-09-05 | no | 1/5/0 | stale (2023), `gh-pages` default branch |
| BrightSoftwares/ieatmyhealth.com | main | 2026-09-30 | wikilinks.rb | 2025-11-26 | no | n/a (403) | Dependabot alerts DISABLED |
| BrightSoftwares/joyousbyflora-posts | main | 2026-09-22 | cachebust.rb, category_generator.rb, wikilinks.rb | 2026-04-30 | no | n/a (403) | Dependabot alerts DISABLED; commits `vendor/bundle/` |
| BrightSoftwares/keke.li | main | 2026-09-26 | wikilinks.rb | 2026-04-30 | no | 2/5/10 | commits `vendor/bundle/` |
| BrightSoftwares/modabyflora-corporate | master | 2026-09-29 | wikilinks.rb | 2025-11-24 | yes | 1/4/0 | commits `vendor/bundle/`; root + nested Python manifests |
| BrightSoftwares/olympics-paris2024.com | main | 2026-09-08 | wikilinks.rb | 2025-12-01 | yes | 7/8/10 |  |
| sergioafanou/smart-cv | master | 2026-10-05 | wikilinks.rb | 2026-10-05 | yes | 11/17/11 | alerts still open after lock fix (bundler-audit: 0) -> Dependabot rescan lag; committed `.venv/` |

Wikilinks plugin state: the 8 `wikilinks.rb` copies in BrightSoftwares repos are byte-identical (142 lines, md5 `aa297faf`, the old v2 without code-block skipping); smart-cv has the fixed 209-line version (the one now shipped as the gem).

### Fleet report (output of `fleet_dependabot_report.py`, same day)

| Repo | Branch | Crit | High | Med | Low | Total | dependabot.yml | Gemfile.lock age | wikilinks |
|---|---|--:|--:|--:|--:|--:|:-:|--:|:-:|
| BrightSoftwares/corporate-website | master | 0 | 7 | 14 | 1 | 22 | NO | 1724d | local-copy |
| BrightSoftwares/modabyflora-corporate | master | 0 | 1 | 4 | 0 | 5 | yes | 315d | local-copy |
| BrightSoftwares/ieatmyhealth.com | main | n/a (alerts disabled) |  |  |  | n/a | NO | 313d | local-copy |
| BrightSoftwares/eagles-techs.com | main | 0 | 5 | 7 | 10 | 22 | NO | 305d | local-copy |
| BrightSoftwares/joyousbyflora-posts | main | n/a (alerts disabled) |  |  |  | n/a | NO | 158d | local-copy |
| BrightSoftwares/keke.li | main | 0 | 2 | 5 | 10 | 17 | NO | 158d | local-copy |
| BrightSoftwares/olympics-paris2024.com | main | 0 | 7 | 8 | 10 | 25 | yes | 308d | local-copy |
| BrightSoftwares/foolywise.com | main | n/a (alerts disabled) |  |  |  | n/a | NO | 158d | local-copy |
| sergioafanou/smart-cv | master | 0 | 11 | 17 | 11 | 39 | yes | 0d | local-copy |
| **Fleet total** | | 0 | 33 | 55 | 42 | 130 | | | |

`n/a (alerts disabled)`: Dependabot alerts are switched off for the repo, so 0 would be a lie. `fleet_apply_dependabot_config.py --enable-alerts` can turn them on (needs admin).

## Findings worth a follow-up

- 4 sites commit `vendor/bundle/` (keke.li, foolywise.com, modabyflora-corporate, joyousbyflora-posts): gem sources in git defeat dependency scanning and bloat clones. Fix: add `vendor/bundle` to `.gitignore` and `git rm -r --cached`.
- smart-cv commits a `.venv/` (numpy etc.) - same class of problem.
- Several repos carry the same Python helper lock `_data/cleanup_scripts/Pipfile.lock` (17 pip alerts each in corporate-website and smart-cv): another duplicated asset that belongs in this repo.
- Similar per-site plugins exist (`cache_buster.rb` vs `cachebust.rb`): candidates for the next shared gem.
