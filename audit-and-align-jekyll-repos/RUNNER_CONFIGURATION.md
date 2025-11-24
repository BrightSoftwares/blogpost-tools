# GitHub Actions Runner Configuration

This document explains how to manage GitHub Actions runner configuration across all Jekyll repositories.

## Current Configuration

All 11 repositories are currently using **ubuntu-latest** runners for faster, consistent builds.

## Runner Options

### ubuntu-latest (Recommended)

**Pros:**
- ✅ Fast build times
- ✅ No maintenance required
- ✅ Consistent environment
- ✅ Always available
- ✅ GitHub-hosted (no infrastructure needed)

**Cons:**
- ⚠️ Consumes GitHub Actions minutes (free tier: 2000 min/month)
- ⚠️ Network egress costs for large artifacts

**Best for:** Most use cases, especially for open-source projects

### self-hosted

**Pros:**
- ✅ Unlimited minutes (no GitHub Actions consumption)
- ✅ Custom hardware configuration
- ✅ Network cost control
- ✅ Potential cost savings for high-volume builds

**Cons:**
- ⚠️ Requires infrastructure setup
- ⚠️ Maintenance overhead
- ⚠️ Availability depends on runner status
- ⚠️ Security considerations

**Best for:** Organizations with existing infrastructure, high build volumes

## Switching Runners

### Switch to ubuntu-latest

```bash
./scripts/switch-runners.sh $GITHUB_TOKEN ubuntu-latest
```

### Switch to self-hosted

```bash
./scripts/switch-runners.sh $GITHUB_TOKEN self-hosted
```

**Note:** Before switching to self-hosted, ensure runners are properly configured in each repository's settings.

## Verification

After switching, verify workflows run successfully:

```bash
./scripts/check-status.sh $GITHUB_TOKEN
```

Or manually check workflow runs:
```
https://github.com/{owner}/{repo}/actions
```

## Recommendations

### For Development/Testing
**Use:** `ubuntu-latest`
- Faster iteration
- No infrastructure dependencies
- Consistent results

### For Production
**Consider:** `self-hosted` if:
1. Build volume exceeds GitHub Actions free tier
2. You have existing runner infrastructure
3. You need custom build environment
4. Network costs are a concern

**Otherwise use:** `ubuntu-latest`
- Simpler operations
- Lower maintenance burden
- Better for most teams

## Repository Status

| Repository | Current Runner | Notes |
|------------|----------------|-------|
| BrightSoftwares/corporate-website | ubuntu-latest | ✅ Working |
| BrightSoftwares/foolywise.com | ubuntu-latest | ✅ Working |
| BrightSoftwares/ieatmyhealth.com | ubuntu-latest | ✅ Working |
| BrightSoftwares/joyousbyflora-posts | ubuntu-latest | ✅ Working |
| BrightSoftwares/keke.li | ubuntu-latest | ✅ Working |
| BrightSoftwares/modabyflora-corporate | ubuntu-latest | ✅ Working |
| BrightSoftwares/olympics-paris2024.com | ubuntu-latest | ✅ Working |
| BrightSoftwares/eagles-techs.com | ubuntu-latest | ✅ Working |
| Causting/causting.com | ubuntu-latest | ✅ Working |
| Causting/space-up-planet.com | ubuntu-latest | ✅ Working |
| sergioafanou/smart-cv | ubuntu-latest | ✅ Working |

## History

- **2025-11-24:** All repos switched to `ubuntu-latest` for testing
- **Plugin alignment:** All workflows tested and verified on `ubuntu-latest`
- **Recommendation:** Keep `ubuntu-latest` unless specific needs require `self-hosted`

## Support

For runner configuration issues:
1. Check workflow logs in GitHub Actions
2. Verify runner status in repository settings
3. Review this documentation
4. Contact repository administrators
