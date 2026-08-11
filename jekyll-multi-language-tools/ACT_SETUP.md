# `act` Setup for Jekyll Migration Testing (SP14.5-2)

**Scope note:** this is a config-file + documentation deliverable, not a binary
install. `act` itself must be installed once per machine that runs it
(developer laptop or a self-hosted CI runner) — it cannot be "installed" as a
repo artifact, and installing it inside an ephemeral sandbox session would not
persist. The full install/troubleshooting guide already lives in the vault at
`task_executor/docs/act-setup-guide.md` (629 lines, created 2026-01-19) — this
file does not duplicate it, it fixes the one broken cross-reference in it and
gives the config a canonical, copy-able home.

**What was missing:** the vault guide's §Configuration step 1 says:

```bash
cp /path/to/vault/task_executor/.actrc /path/to/jekyll-site/.actrc
```

...but `task_executor/.actrc` never actually existed in the vault (checked
2026-08-06). This directory's [`.actrc`](.actrc) is that file, now with a real
home. It matches the guide's documented content exactly.

## Usage

Copy this file into any Jekyll blog repo before running `act` locally:

```bash
cp jekyll-multi-language-tools/.actrc /path/to/jekyll-site/.actrc
```

Then follow the vault's `task_executor/docs/act-setup-guide.md` for
installation, secrets, and the SP14.5 per-repo testing sequence (`act -l`,
dry-run, then the 7-test plan in
`951.156.AINOTE...#SP14.4: Local Testing Workflow with act` for repos that
carry the e-commerce/build-mode logic).

## Why this lives here, not in the vault

Per the vault's Three-Repo Rule (CLAUDE.md), reusable scripts/config that
apply across the ~9 Jekyll blog repos belong in `blogpost-tools`, not in
`my-obsidian` (tracking-only). The vault guide stays the canonical
*documentation*; this file is the canonical *artifact* it references.
