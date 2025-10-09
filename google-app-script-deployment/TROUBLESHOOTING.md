# Troubleshooting Guide

Comprehensive guide for resolving common issues with Google Apps Script Marketplace automation.

## 📋 Table of Contents

- [Authentication Issues](#authentication-issues)
- [GCP Project Issues](#gcp-project-issues)
- [OAuth Consent Issues](#oauth-consent-issues)
- [Deployment Failures](#deployment-failures)
- [Asset Validation Issues](#asset-validation-issues)
- [API Quota Issues](#api-quota-issues)
- [Marketplace Submission Issues](#marketplace-submission-issues)
- [Workflow Failures](#workflow-failures)
- [Debug Mode](#debug-mode)

---

## Authentication Issues

### Error: "Service Account lacks permissions"

**Symptoms:**
```
Error 403: The caller does not have permission
```

**Solutions:**

1. **Grant Editor role:**
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/editor"
```

2. **Grant specific roles:**
```bash
# Apps Script Admin
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/appsscript.admin"

# Service Account User
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

3. **Verify service account:**
```bash
gcloud iam service-accounts describe SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com
```

### Error: "Invalid service account key"

**Symptoms:**
```
Error: GCP_SERVICE_ACCOUNT_KEY not set or invalid
```

**Solutions:**

1. **Verify JSON format:**
   - Open the key file
   - Ensure it's valid JSON
   - Check for `"type": "service_account"`

2. **Re-create the key:**
```bash
gcloud iam service-accounts keys create new-key.json \
  --iam-account=SA_EMAIL@PROJECT_ID.iam.gserviceaccount.com
```

3. **Update GitHub Secret:**
   - Go to Repository Settings > Secrets
   - Update `GCP_SERVICE_ACCOUNT_KEY`
   - Paste ENTIRE JSON file content
   - Don't add quotes or modify the JSON

### Error: "Authentication failed: refresh token"

**Symptoms:**
```
Error refreshing credentials: invalid_grant
```

**Solution for OAuth method:**

1. **Regenerate refresh token:**
```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

creds = flow.run_local_server(port=0)
print(f"Refresh token: {creds.refresh_token}")
```

2. **Update GitHub Secrets:**
   - `GCP_OAUTH_REFRESH_TOKEN`

---

## GCP Project Issues

### Error: "Project quota exceeded"

**Symptoms:**
```
Error: You have reached the maximum number of projects (10)
```

**Solutions:**

1. **Use reuse strategy:**
```yaml
gcp:
  strategy: "reuse"
  labels:
    environment: "production"
```

2. **Delete unused projects:**
```bash
# List all projects
gcloud projects list

# Delete unused project
gcloud projects delete PROJECT_ID
```

3. **Request quota increase:**
   - Go to [Quota page](https://console.cloud.google.com/iam-admin/quotas)
   - Request increase for "Projects"

### Error: "Cannot create project: billing account required"

**Symptoms:**
```
Error: Project creation requires billing account
```

**Solutions:**

1. **Link billing account:**
```bash
gcloud beta billing projects link PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

2. **Find billing account ID:**
```bash
gcloud beta billing accounts list
```

3. **Or set in config:**
```yaml
gcp:
  billing_account_id: "012345-6789AB-CDEF01"
```

### Error: "Project ID already exists"

**Symptoms:**
```
Error: Requested entity already exists
```

**Solutions:**

1. **Choose different name pattern:**
```yaml
gcp:
  project_name_pattern: "apps-script-{addon_id}-{timestamp}"
```

2. **Use specific existing project:**
```yaml
gcp:
  strategy: "specific"
  project_id: "your-existing-project"
```

---

## OAuth Consent Issues

### Error: "OAuth consent screen not configured"

**Symptoms:**
```
Error: OAuth consent screen is not configured
```

**Solutions:**

1. **Configure via Console:**
   - Visit: https://console.cloud.google.com/apis/credentials/consent
   - Choose user type (Internal/External)
   - Fill all required fields
   - Save

2. **Verify required fields:**
   - App name
   - Support email
   - Developer contact email
   - Privacy policy URL (external apps)
   - Terms of service URL (external apps)

3. **Check config matches:**
```yaml
oauth_consent:
  support_email: "support@example.com"  # Must match console
  privacy_policy_url: "https://..."     # Must be HTTPS
  terms_of_service_url: "https://..."   # Must be HTTPS
```

### Error: "Domain not verified"

**Symptoms:**
```
Error: Domain verification required for external apps
```

**Solutions:**

1. **Verify domain ownership:**
   - Go to: https://console.cloud.google.com/apis/credentials/domainverification
   - Add your domain
   - Follow verification steps (DNS or HTML file)

2. **Methods to verify:**
   
   **DNS Record Method:**
   ```
   TXT record: google-site-verification=ABC123...
   ```
   
   **HTML File Method:**
   - Download verification file
   - Upload to: https://yourdomain.com/google-verification.html

3. **Wait for verification:**
   - DNS: Can take 24-48 hours
   - HTML: Usually immediate

### Error: "Scopes not configured"

**Symptoms:**
```
Warning: No oauthScopes found in appsscript.json
```

**Solutions:**

1. **Add scopes to appsscript.json:**
```json
{
  "oauthScopes": [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/script.external_request"
  ]
}
```

2. **Common scopes:**
   - Sheets: `https://www.googleapis.com/auth/spreadsheets`
   - Docs: `https://www.googleapis.com/auth/documents`
   - Drive: `https://www.googleapis.com/auth/drive`
   - Gmail: `https://www.googleapis.com/auth/gmail.compose`
   - Calendar: `https://www.googleapis.com/auth/calendar`

3. **Enable auto-configure:**
```yaml
oauth_consent:
  auto_configure_scopes: true
```

---

## Deployment Failures

### Error: "Script not found"

**Symptoms:**
```
Error: Script project not found: SCRIPT_ID
```

**Solutions:**

1. **Verify script ID:**
   - Go to: https://script.google.com
   - Open your project
   - Project Settings > IDs
   - Copy "Script ID"

2. **Update config:**
```yaml
project:
  script_id: "YOUR_ACTUAL_SCRIPT_ID_HERE"
```

3. **Check service account access:**
   - Script must be in same GCP project, OR
   - Service account needs explicit access

### Error: "clasp push failed"

**Symptoms:**
```
Error: Push failed - authentication required
```

**Solutions:**

1. **Verify .clasp.json:**
```json
{
  "scriptId": "YOUR_SCRIPT_ID",
  "projectId": "YOUR_GCP_PROJECT_ID"
}
```

2. **Check Apps Script API:**
```bash
gcloud services enable script.googleapis.com --project=PROJECT_ID
```

3. **Manual test:**
```bash
# Login to clasp
clasp login

# Push manually
clasp push --force
```

### Error: "Deployment version conflict"

**Symptoms:**
```
Error: Version already exists
```

**Solutions:**

1. **Use HEAD versioning:**
```yaml
deployment:
  versioning: "head"
```

2. **Or increment version:**
```bash
git tag v1.0.1  # Increment version number
git push origin v1.0.1
```

3. **Delete conflicting deployment:**
```bash
clasp deployments
clasp undeploy DEPLOYMENT_ID
```

---

## Asset Validation Issues

### Error: "Invalid icon dimensions"

**Symptoms:**
```
Warning: Icon should be 128x128px, found (256, 256)
```

**Solutions:**

1. **Resize image:**
```bash
# Using ImageMagick
convert icon.png -resize 128x128 icon-128.png

# Using Python/Pillow
python << EOF
from PIL import Image
img = Image.open('icon.png')
img = img.resize((128, 128), Image.LANCZOS)
img.save('icon-128.png')
EOF
```

2. **Check format:**
   - Must be PNG (not JPG)
   - Transparent background recommended
   - No animations

3. **Validate locally:**
```python
from PIL import Image
img = Image.open('marketplace/icon.png')
print(f"Size: {img.size}, Format: {img.format}")
# Should output: Size: (128, 128), Format: PNG
```

### Error: "Screenshot validation failed"

**Symptoms:**
```
Error: Screenshot should be 1280x800px
```

**Solutions:**

1. **Correct dimensions:**
   - Width: 1280 pixels
   - Height: 800 pixels
   - Format: PNG

2. **Batch resize:**
```bash
for file in marketplace/screenshot*.png; do
  convert "$file" -resize 1280x800 "$file"
done
```

3. **Design tips:**
   - Use actual app screenshots
   - Add captions or annotations
   - Show key features
   - Maintain aspect ratio

### Error: "Asset URL not accessible"

**Symptoms:**
```
Error: Cannot fetch asset from URL
```

**Solutions:**

1. **Test URL manually:**
```bash
curl -I https://example.com/icon.png
# Should return 200 OK
```

2. **Check CORS:**
   - Ensure public access
   - No authentication required
   - HTTPS required

3. **Use CDN:**
   - CloudFlare
   - AWS S3 + CloudFront
   - Google Cloud Storage with public access

---

## API Quota Issues

### Error: "API rate limit exceeded"

**Symptoms:**
```
Error 429: Rate limit exceeded
```

**Solutions:**

1. **Wait and retry:**
   - Automatic exponential backoff enabled
   - Default: 3 retries

2. **Increase retry attempts:**
```yaml
retry:
  max_attempts: 5
  initial_delay: 10
  backoff_multiplier: 2
```

3. **Request quota increase:**
   - Go to: https://console.cloud.google.com/apis/api/script.googleapis.com/quotas
   - Request increase

### Error: "API not enabled"

**Symptoms:**
```
Error: API [script.googleapis.com] not enabled
```

**Solutions:**

1. **Enable via workflow:**
   - Should auto-enable on deployment
   - Check workflow logs for errors

2. **Enable manually:**
```bash
gcloud services enable script.googleapis.com --project=PROJECT_ID
gcloud services enable cloudresourcemanager.googleapis.com --project=PROJECT_ID
gcloud services enable iamcredentials.googleapis.com --project=PROJECT_ID
```

3. **Verify enabled:**
```bash
gcloud services list --enabled --project=PROJECT_ID | grep script
```

---

## Marketplace Submission Issues

### Error: "Submission rejected"

**Symptoms:**
- GitHub Issue created with rejection details

**Common rejection reasons:**

1. **Privacy Policy Issues:**
   - Not accessible (404)
   - Not using HTTPS
   - Doesn't cover data usage
   - Missing required sections

   **Solution:** Review [Privacy Policy Requirements](https://developers.google.com/workspace/marketplace/guidelines)

2. **Functionality Issues:**
   - App doesn't work as described
   - Missing features in description
   - Crashes or errors

   **Solution:** Test thoroughly before submission

3. **Content Policy Violations:**
   - Inappropriate content
   - Misleading claims
   - Trademark violations

   **Solution:** Review [Content Policy](https://developers.google.com/workspace/marketplace/policies)

4. **Technical Issues:**
   - OAuth scopes too broad
   - Poor error handling
   - Security vulnerabilities

   **Solution:** Request only necessary scopes

### Error: "Submission stuck in review"

**Symptoms:**
- Submission pending for > 7 days

**Solutions:**

1. **Check submission status:**
   - Manual workflow: `monitor-approval.yml`
   - Or wait for automatic check (every 6 hours)

2. **Contact support:**
   - Use [Google Workspace Marketplace Support](https://support.google.com/googleplay/android-developer/contact/marketplace)
   - Reference submission ID

3. **Resubmit if needed:**
   - Make any requested changes
   - Create new git tag
   - Redeploy

---

## Workflow Failures

### Error: "Validation failed"

**Symptoms:**
```
❌ VALIDATION FAILED
Please fix the errors above before deploying
```

**Solutions:**

1. **Run local validation:**
```bash
python scripts/validate-setup.py
```

2. **Fix reported errors:**
   - Missing required files
   - Invalid configuration
   - Asset issues

3. **Skip validation (not recommended):**
```bash
gh workflow run deploy-marketplace.yml -f force_deploy=true
```

### Error: "Rollback failed"

**Symptoms:**
```
Error: Cannot restore previous version
```

**Solutions:**

1. **Check if backup exists:**
   - Look for backup in workflow artifacts
   - Check clasp deployments: `clasp deployments`

2. **Manual rollback:**
```bash
# List deployments
clasp deployments

# Deploy previous version
clasp deploy --deploymentId PREVIOUS_DEPLOYMENT_ID
```

3. **Disable rollback if problematic:**
```yaml
rollback:
  enabled: false
```

### Error: "GitHub Actions timeout"

**Symptoms:**
```
Error: Job exceeded maximum execution time
```

**Solutions:**

1. **Optimize workflow:**
   - Reduce retry attempts
   - Skip unnecessary steps
   - Use caching

2. **Split into multiple jobs:**
   - Already done in provided workflows
   - Check for bottlenecks

3. **Increase timeout (if needed):**
```yaml
jobs:
  deploy-script:
    timeout-minutes: 30  # Default is 360 (6 hours)
```

---

## Debug Mode

### Enable Debug Logging

**In workflow:**

Add to workflow file:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

**In Python scripts:**

Add to scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Collect Debug Information

**Run validation:**
```bash
python scripts/validate-setup.py > debug.log 2>&1
```

**Check GCP access:**
```bash
gcloud auth list
gcloud projects list
gcloud services list --enabled --project=PROJECT_ID
```

**Test API access:**
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os

# Load service account
creds = service_account.Credentials.from_service_account_file(
    'sa-key.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Test Apps Script API
service = build('script', 'v1', credentials=creds)
print("✓ Apps Script API accessible")

# Test Cloud Resource Manager
crm = build('cloudresourcemanager', 'v1', credentials=creds)
projects = crm.projects().list().execute()
print(f"✓ Found {len(projects.get('projects', []))} projects")
```

### Common Debug Commands

**Check workflow run:**
```bash
# List recent runs
gh run list

# View specific run
gh run view RUN_ID

# View logs
gh run view RUN_ID --log
```

**Check secrets:**
```bash
# List secrets (names only)
gh secret list

# Set/update secret
gh secret set GCP_SERVICE_ACCOUNT_KEY < sa-key.json
```

**Test locally:**
```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
act -s GCP_SERVICE_ACCOUNT_KEY="$(cat sa-key.json)" push
```

---

## Getting Help

### Before Asking for Help

1. **Check this guide** - Most issues are covered here
2. **Read error messages** - They often contain the solution
3. **Check workflow logs** - GitHub Actions provides detailed logs
4. **Validate setup** - Run `python scripts/validate-setup.py`
5. **Search existing issues** - Someone may have solved it already

### Where to Get Help

1. **GitHub Issues**: For bugs or feature requests
2. **Stack Overflow**: Tag with `[google-apps-script]` `[deployment]`
3. **Google Groups**: Apps Script community
4. **Official Docs**:
   - [Apps Script](https://developers.google.com/apps-script)
   - [Workspace Marketplace](https://developers.google.com/workspace/marketplace)
   - [Google Cloud](https://cloud.google.com/docs)

### Providing Debug Information

When asking for help, include:

```
**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11]
- Git version: [e.g., 2.40]

**Configuration:**
- Auth method: [service_account/oauth]
- GCP strategy: [reuse/create/specific]
- Deployment trigger: [tag/manual/push]

**Error:**
[Paste complete error message]

**Workflow logs:**
[Link to failed workflow run]

**Steps to reproduce:**
1. [First step]
2. [Second step]
3. [Error occurs]
```

---

## Preventive Measures

### Before Each Deployment

✅ **Pre-deployment checklist:**
- [ ] Run `python scripts/validate-setup.py`
- [ ] Test add-on manually in Apps Script
- [ ] Verify all assets are accessible
- [ ] Check privacy policy is up to date
- [ ] Review configuration changes
- [ ] Test on staging environment first
- [ ] Ensure git repository is clean

### Regular Maintenance

✅ **Monthly tasks:**
- [ ] Rotate service account keys (every 90 days)
- [ ] Review and clean up old GCP projects
- [ ] Update dependencies (`requirements.txt`)
- [ ] Check for workflow updates
- [ ] Review submission analytics
- [ ] Update documentation

### Monitoring

✅ **Set up monitoring:**
- [ ] Enable GitHub Actions notifications
- [ ] Configure Slack/email alerts
- [ ] Monitor approval workflow runs
- [ ] Track submission success rate
- [ ] Review rejection patterns

---

## Quick Reference

### Useful Commands

```bash
# Validate setup
python scripts/validate-setup.py

# Test GCP connection
gcloud auth list
gcloud projects list

# Check APIs
gcloud services list --enabled --project=PROJECT_ID

# View workflow runs
gh run list --limit 10

# Trigger deployment
git tag v1.0.0 && git push origin v1.0.0

# Manual workflow dispatch
gh workflow run deploy-marketplace.yml -f environment=staging

# Check approval status
gh workflow run monitor-approval.yml

# View logs
gh run view --log

# List deployments
clasp deployments

# Test API access
python -c "from google.oauth2 import service_account; print('OK')"
```

### File Locations

```
Configuration: marketplace-config.yaml
Workflows: .github/workflows/
Validation: scripts/validate-setup.py
Assets: marketplace/
Tracker: .marketplace-submissions.json
Logs: GitHub Actions > Workflow runs
```

### Support Resources

- **Documentation**: Check README.md and SETUP.md
- **Examples**: See marketplace-config.yaml
- **Validation**: Run scripts/validate-setup.py
- **Community**: Stack Overflow, Google Groups
- **Official**: Google Workspace Marketplace support

---

*Last updated: 2025*
*For the latest troubleshooting tips, check the GitHub repository.*