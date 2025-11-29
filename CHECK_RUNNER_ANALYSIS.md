# Check-Runner Current Implementation Analysis

**File:** `blogpost-tools/check-runner/src/check_runner.sh`

---

## Current Implementation Overview

### What It Does:
1. Checks if user forced to run on GitHub infrastructure (`FORCE_RUNS_ON_UBUNTU`)
2. Queries GitHub API for available self-hosted runners
3. Returns `self-hosted` if available, otherwise `ubuntu-latest`

### Current Inputs (Environment Variables):
- `CHECK_RUNNER_TOKEN` - GitHub token for API access
- `GITHUB_REPO_OWNER` - Repository owner
- `GITHUB_REPOSITORY` - Repository name
- `FORCE_RUNS_ON_UBUNTU` - Force Ubuntu runner (if 'true')

### Current Output:
- `runner-label` - Either "self-hosted" or "ubuntu-latest"

---

## Bugs Found 🐛

### Bug #1: Logic Error (Line 24)
```bash
if [[ -n "$GITHUB_REPO_OWNER" || -z "$GITHUB_REPO_OWNER" ]]; then
    GITHUB_REPO_OWNER=$GITHUB_REPOSITORY_OWNER
fi
```

**Issue:** This condition is ALWAYS true (variable is either non-empty OR empty)

**Impact:** `GITHUB_REPO_OWNER` always gets overwritten

**Fix Needed:** Should be `if [[ -z "$GITHUB_REPO_OWNER" ]]; then` (only if empty)

---

### Bug #2: Output Name Mismatch (action.yml)
```yaml
outputs:
  updated_posts:  # ❌ Wrong name
    description: Label of the runner
```

**Issue:** Output is named `updated_posts` but script sets `runner-label`

**Impact:** Consumers might be accessing wrong output

**Fix Needed:** Change to `runner-label` or update script

---

### Bug #3: Commented Dead Code (Line 38, 41, 63)
Multiple commented lines that should be removed for clarity

---

## Missing Features (Based on Your Requirements)

### 1. ❌ Force Self-Hosted
- Currently only has `FORCE_RUNS_ON_UBUNTU`
- No way to force `self-hosted` even if unavailable

### 2. ❌ Free Tier Threshold Management
- No tracking of GitHub Actions minutes
- No threshold-based routing
- No workflow priority levels

### 3. ❌ Fallback Configuration
- No configurable fallback behavior
- Always defaults to `ubuntu-latest` if no self-hosted available

### 4. ❌ Monitoring/Logging
- Lots of echo statements (good for debugging)
- But no structured logging
- No metrics/tracking

### 5. ❌ Priority-Based Routing
- No concept of workflow importance
- All workflows treated equally

---

## Enhancement Opportunities

### Current Logic Flow:
```
Start
  ↓
Is FORCE_RUNS_ON_UBUNTU=true?
  ↓ Yes → Return ubuntu-latest
  ↓ No
Query GitHub API for self-hosted runners
  ↓
Are there online, non-busy self-hosted runners?
  ↓ Yes → Return self-hosted
  ↓ No → Return ubuntu-latest
```

### Enhanced Logic Flow (Your Requirements):
```
Start
  ↓
Is FORCE_SELF_HOSTED=true?
  ↓ Yes → Check if available → Yes: self-hosted | No: Fail or Fallback?
  ↓ No
Is FORCE_UBUNTU=true?
  ↓ Yes → Return ubuntu-latest
  ↓ No
Check workflow priority level
  ↓
Get remaining GitHub Actions minutes
  ↓
Is remaining < threshold for this priority?
  ↓ Yes → Try self-hosted
  ↓ No → Use ubuntu-latest
  ↓
Is self-hosted available?
  ↓ Yes → Return self-hosted
  ↓ No → Fallback to ubuntu-latest or fail?
```

---

## Proposed New Features

### Feature 1: Force Runner Options
```bash
# New environment variables:
FORCE_RUNNER="self-hosted" | "ubuntu-latest" | "auto" (default)

# Behavior:
# - "self-hosted": Force self-hosted, fail if unavailable (or fallback based on config)
# - "ubuntu-latest": Force ubuntu-latest
# - "auto": Use smart routing (threshold-based)
```

### Feature 2: Free Tier Management
```bash
# New environment variables:
FREE_TIER_REMAINING=1000  # Minutes remaining
WORKFLOW_PRIORITY="HIGH" | "MEDIUM" | "LOW"
THRESHOLD_HIGH=200   # When to switch HIGH priority to self-hosted
THRESHOLD_MEDIUM=500 # When to switch MEDIUM priority to self-hosted
THRESHOLD_LOW=1000   # When to switch LOW priority to self-hosted

# Logic:
if [[ $FREE_TIER_REMAINING -lt $THRESHOLD_FOR_PRIORITY ]]; then
    # Try self-hosted
else
    # Use ubuntu-latest
fi
```

### Feature 3: Fallback Strategy
```bash
FALLBACK_STRATEGY="fail" | "fallback" | "wait"

# Behaviors:
# - fail: Exit with error if forced runner unavailable
# - fallback: Use alternative runner
# - wait: Wait for forced runner to become available (with timeout)
```

### Feature 4: Monitoring
```bash
# Log decisions to file or external service
# Track:
# - Runner selected
# - Reason for selection
# - Remaining minutes
# - Timestamp
# - Workflow name/priority
```

### Feature 5: Multi-Runner Selection
```bash
# Instead of just "self-hosted", support:
# - Specific runner by label
# - Load balancing across multiple self-hosted
# - Runner capabilities matching (docker, etc.)
```

---

## Edge Cases to Handle

### 1. API Rate Limiting
- Current: No handling
- Needed: Retry logic, caching of runner status

### 2. Token Expiry/Invalid
- Current: Falls back to ubuntu-latest
- Needed: Better error messages

### 3. Network Issues
- Current: Falls back to ubuntu-latest
- Needed: Retry logic

### 4. Concurrent Workflows
- Current: Might all pick same self-hosted runner
- Needed: Load balancing or queue management

### 5. Billing Cycle Rollover
- Current: No concept of time
- Needed: Auto-reset of minute counters

### 6. Manual Override Mid-Run
- Current: Can't change mid-workflow
- Needed: Way to signal runner to yield?

---

## Proposed Configuration File Structure

```yaml
# .github/check-runner-config.yml

version: 1

# Global settings
settings:
  fallback_strategy: fallback  # fail | fallback | wait
  api_retry_attempts: 3
  api_retry_delay: 2  # seconds
  log_decisions: true
  log_destination: artifacts  # artifacts | api | both

# Free tier management
free_tier:
  monthly_quota: 2000  # minutes
  current_usage: 1250  # Updated by monitoring
  usage_tracking: manual  # manual | api (if GitHub exposes this)

  thresholds:
    high_priority: 200     # Switch HIGH priority workflows at 200 min remaining
    medium_priority: 500   # Switch MEDIUM priority workflows at 500 min remaining
    low_priority: 1000     # Switch LOW priority workflows at 1000 min remaining

  # When quota exhausted
  quota_exhausted_action: force_self_hosted  # force_self_hosted | fail | queue

# Workflow priorities
workflow_priorities:
  # HIGH: Always use GitHub-hosted unless quota critical
  - pattern: "jekyll.*build"
    priority: HIGH
  - pattern: "deploy.*"
    priority: HIGH

  # MEDIUM: Balance between GitHub and self-hosted
  - pattern: "seo-.*"
    priority: MEDIUM
  - pattern: "auto-internal.*"
    priority: MEDIUM

  # LOW: Prefer self-hosted to save quota
  - pattern: "auto-.*"
    priority: LOW
  - pattern: ".*-generator"
    priority: LOW

# Runner preferences
runners:
  self_hosted:
    # Check both org and repo level
    check_org_level: true
    check_repo_level: true

    # Requirements
    must_be_online: true
    must_be_not_busy: true
    required_labels: ["self-hosted"]

    # Load balancing
    selection_strategy: random  # random | least-busy | round-robin

  ubuntu_latest:
    version: "latest"  # Or specific: "22.04"

# Force overrides (for testing/emergencies)
force:
  runner: auto  # auto | self-hosted | ubuntu-latest
  expires_at: null  # Optional: "2025-11-30T00:00:00Z"
  reason: ""  # For logging

# Monitoring
monitoring:
  enabled: true
  metrics:
    - runner_selected
    - selection_reason
    - remaining_minutes
    - workflow_duration
    - queue_time

  alerts:
    - condition: remaining_minutes < 100
      action: github_issue  # github_issue | slack | email
      recipients: ["@fullbright"]

    - condition: self_hosted_unavailable
      action: log
```

---

## Implementation Plan

### Phase 1: Bug Fixes (Immediate)
- [ ] Fix logic error on line 24
- [ ] Fix output name mismatch
- [ ] Clean up commented code
- [ ] Add proper error handling

### Phase 2: Core Enhancements (High Priority)
- [ ] Add `FORCE_SELF_HOSTED` option
- [ ] Implement configuration file support
- [ ] Add workflow priority detection
- [ ] Implement basic threshold checking

### Phase 3: Advanced Features (Medium Priority)
- [ ] Free tier tracking integration
- [ ] Monitoring and logging
- [ ] Load balancing across multiple self-hosted
- [ ] Alert system

### Phase 4: Polish (Low Priority)
- [ ] API rate limiting handling
- [ ] Retry logic
- [ ] Dashboard/reporting
- [ ] Documentation

---

## Testing Checklist

### Unit Tests Needed:
- [ ] Force ubuntu-latest
- [ ] Force self-hosted (available)
- [ ] Force self-hosted (unavailable)
- [ ] Auto mode with high free tier remaining
- [ ] Auto mode with low free tier remaining
- [ ] Auto mode with quota exhausted
- [ ] Self-hosted available (not busy)
- [ ] Self-hosted available (busy)
- [ ] Self-hosted offline
- [ ] No self-hosted runners
- [ ] API errors/timeouts
- [ ] Invalid token
- [ ] Network failures
- [ ] Different workflow priorities

### Integration Tests Needed:
- [ ] Real workflow using check-runner
- [ ] Multiple concurrent workflows
- [ ] Threshold crossing during run
- [ ] Billing cycle rollover
- [ ] Configuration file updates mid-run

---

## Questions to Clarify

1. **Free Tier Tracking:**
   - How should I get remaining minutes? GitHub doesn't expose this in API currently
   - Manual update via config file?
   - External service integration?

2. **Workflow Priority Detection:**
   - Based on workflow name pattern (as in example config)?
   - Explicit input parameter?
   - Both?

3. **Configuration Location:**
   - Config file in each repo?
   - Centralized in blogpost-tools?
   - Repository secrets?
   - Mix of all?

4. **Breaking Changes:**
   - Can I change the action interface (inputs/outputs)?
   - Or must maintain backward compatibility?

5. **Monitoring Data:**
   - Where should metrics be stored?
   - GitHub Actions artifacts?
   - External service (Datadog, CloudWatch, etc.)?
   - Simple log files?

---

**Add this analysis to your WORKFLOW_MIGRATION_INSTRUCTIONS.md document in the check-runner section with your preferences and answers to the questions above.**
