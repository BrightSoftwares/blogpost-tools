# Jekyll Migration Report

**Date:** 2023-11-23
**Branch:** `migration/standardize-jekyll-20251123_182523`

## Summary

| Status | Count |
|--------|-------|
| ✅ Success | 5 |
| ❌ Failed | 6 |
| ⏳ Pending | 1 |
| **Total** | **12** |

## Successful Migrations (5)

| Repository | Notes |
|------------|-------|
| BrightSoftwares/corporate-website | Ruby 3.4 gems already present |
| BrightSoftwares/foolywise.com | Ruby 3.4 gems added |
| BrightSoftwares/joyousbyflora-posts | Ruby 3.4 gems already present |
| BrightSoftwares/modabyflora-corporate | Ruby 3.4 gems already present |
| Causting/causting.com | Ruby 3.4 gems added |

## Failed Migrations (6)

| Repository | Root Cause | Fix Required |
|------------|------------|--------------|
| BrightSoftwares/ieatmyhealth.com | Uses `runs-on: self-hosted` | Update runner or change to `ubuntu-latest` |
| BrightSoftwares/keke.li | No Jekyll workflow found | Add Jekyll workflow file |
| BrightSoftwares/olympics-paris2024.com | Uses `runs-on: self-hosted` | Update runner or change to `ubuntu-latest` |
| BrightSoftwares/eagles-techs.com | Uses `runs-on: self-hosted` | Update runner or change to `ubuntu-latest` |
| Causting/space-up-planet.com | Uses `runs-on: self-hosted` | Update runner or change to `ubuntu-latest` |
| sergioafanou/smart-cv | Uses `runs-on: self-hosted` | Update runner or change to `ubuntu-latest` |

## Pending (1)

| Repository | Status | Notes |
|------------|--------|-------|
| sergioafanou/blog | No workflow run | No Jekyll workflow found |

## Root Cause Analysis

### 1. Self-Hosted Runner Issues (5 repos)

The following repositories use `runs-on: self-hosted` in their workflows:
- BrightSoftwares/ieatmyhealth.com
- BrightSoftwares/eagles-techs.com
- BrightSoftwares/olympics-paris2024.com
- Causting/space-up-planet.com
- sergioafanou/smart-cv

**Problem:** Self-hosted runners may not have Ruby 3.4 or other required dependencies installed.

**Solutions:**
1. Update self-hosted runners with Ruby 3.4 and required gems
2. Change workflows to use `ubuntu-latest` GitHub-hosted runners
3. Use a Docker-based workflow that includes all dependencies

### 2. Missing Jekyll Workflow (2 repos)

The following repositories don't have a recognizable Jekyll workflow:
- BrightSoftwares/keke.li
- sergioafanou/blog

**Solution:** Add a standardized Jekyll workflow file (`.github/workflows/jekyll.yml`)

## Recommendations

### Immediate Actions

1. **For self-hosted runner repos:** Create a fix script that updates the workflow to use `ubuntu-latest` runner temporarily while self-hosted runners are updated.

2. **For repos without workflow:** Deploy the standardized Jekyll workflow template.

### Long-term Actions

1. Update self-hosted runners with:
   - Ruby 3.4.1
   - Bundler
   - ImageMagick
   - All Ruby 3.4 stdlib gems (csv, logger, base64, bigdecimal, observer, ostruct)

2. Standardize all Jekyll workflows to use the reusable workflow from `blogpost-tools`

## Migration Branches Created

All repositories have a migration branch:
```
migration/standardize-jekyll-20251123_182523
```

Changes made:
- Added Ruby 3.4 compatibility gems to Gemfile (where needed)
- Triggered workflow runs for testing

## Auto-Fix Applied

Changed `runs-on: self-hosted` to `runs-on: ubuntu-latest` in 5 repos:
- BrightSoftwares/ieatmyhealth.com
- BrightSoftwares/eagles-techs.com
- BrightSoftwares/olympics-paris2024.com
- Causting/space-up-planet.com
- sergioafanou/smart-cv

**Result:** Failures persisted after switching to GitHub-hosted runners, indicating the root cause is **not** the runner type but likely:
1. Missing secrets (SUBMODULE_SSH_PRIVATE_KEY for cloning jekyll-theme-common-includes)
2. Missing Algolia API keys
3. Missing Netlify credentials

## Next Steps

1. **Verify secrets are configured** in all repositories for:
   - `SUBMODULE_SSH_PRIVATE_KEY` - SSH key for cloning submodules
   - `ALGOLIA_API_KEY` - Algolia search indexing
   - `NETLIFY_AUTH_TOKEN` - Netlify deployment
   - `NETLIFY_SITE_ID` - Netlify site identifier

2. **Add Jekyll workflows** to repos that don't have them:
   - BrightSoftwares/keke.li
   - sergioafanou/blog

3. **Merge successful migration branches** to main/master:
   - BrightSoftwares/corporate-website
   - BrightSoftwares/foolywise.com
   - BrightSoftwares/joyousbyflora-posts
   - BrightSoftwares/modabyflora-corporate
   - Causting/causting.com
