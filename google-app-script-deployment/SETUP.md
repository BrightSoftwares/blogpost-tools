# Google Apps Script Marketplace Automation - Setup Guide

This guide will help you set up automated deployment to the Google Workspace Marketplace using GitHub Actions.

## 📋 Prerequisites

- Google Cloud Platform account
- GitHub repository for your Apps Script project
- Apps Script project already created on script.google.com
- Domain ownership (for external OAuth apps)

## 🚀 Quick Start

### 1. Initial Google Cloud Setup

#### Option A: Using Service Account (Recommended for Automation)

1. **Create or Select a GCP Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Note the Project ID

2. **Enable Required APIs**
   ```bash
   # Enable via gcloud CLI (or use the console)
   gcloud services enable script.googleapis.com
   gcloud services enable cloudresourcemanager.googleapis.com
   gcloud services enable iamcredentials.googleapis.com
   gcloud services enable serviceusage.googleapis.com
   ```

3. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Name: `apps-script-publisher`
   - Grant roles:
     - `Project Editor`
     - `Service Account User`
     - `Apps Script Admin`

4. **Generate Service Account Key**
   - Click on the service account
   - Go to Keys tab
   - Add Key > Create new key > JSON
   - Download and save the JSON file securely

5. **Configure OAuth Consent Screen**
   - Go to APIs & Services > OAuth consent screen
   - Choose User Type:
     - **Internal** (if you have Google Workspace)
     - **External** (for public apps)
   - Fill in required information:
     - App name
     - Support email
     - Developer contact
     - Privacy policy URL (required for external)
     - Terms of service URL (required for external)

#### Option B: Using OAuth (Alternative)

If you prefer OAuth over service accounts:

1. Create OAuth 2.0 Client ID in GCP Console
2. Download credentials
3. Use the credentials to generate a refresh token

### 2. GitHub Repository Setup

#### Configure GitHub Secrets

Go to your GitHub repository > Settings > Secrets and variables > Actions

Add the following secrets:

1. **`GCP_SERVICE_ACCOUNT_KEY`** (Required)
   - Content: The entire JSON key file from the service account
   - Format: Complete JSON object

   ```json
   {
     "type": "service_account",
     "project_id": "your-project",
     "private_key_id": "...",
     "private_key": "...",
     ...
   }
   ```

2. **`SLACK_WEBHOOK_URL`** (Optional)
   - For Slack notifications
   - Only if you enable notifications in config

#### Add Workflow Files

Copy these files to your repository:

```
.github/
└── workflows/
    ├── deploy-marketplace.yml
    └── monitor-approval.yml
```

### 3. Configuration Files

#### Create `marketplace-config.yaml`

Copy the template and customize for your project:

```yaml
project:
  id: "my-addon-id"
  name: "My Amazing Add-on"
  script_id: "YOUR_SCRIPT_ID_FROM_APPS_SCRIPT"

gcp:
  strategy: "reuse"
  labels:
    environment: "production"

oauth_consent:
  user_type: "external"
  support_email: "support@yourdomain.com"
  privacy_policy_url: "https://yourdomain.com/privacy"
  terms_of_service_url: "https://yourdomain.com/terms"
  auto_configure_scopes: true

marketplace:
  default_language: "en"
  asset_location: "external"
  assets:
    icon:
      external_url: "https://yourdomain.com/icon.png"
    screenshots:
      - external_url: "https://yourdomain.com/screenshot1.png"
        caption:
          en: "Main feature"
  content:
    tagline:
      en: "Your amazing tagline here"
    description:
      en: |
        # Full description
        Your detailed description...

deployment:
  environment: "production"
  versioning: "head"
  testing_phase: "direct"
```

#### Environment-Specific Configs (Optional)

Create additional configs for different environments:

- `marketplace-config.staging.yaml`
- `marketplace-config.production.yaml`

These will override the base config values.

#### Required Project Files

Ensure your repository has:

```
your-repo/
├── .github/
│   └── workflows/
│       ├── deploy-marketplace.yml
│       └── monitor-approval.yml
├── marketplace-config.yaml
├── appsscript.json
├── Code.gs (or Code.js)
└── marketplace/
    ├── icon.png (128x128)
    └── screenshot1.png (1280x800)
```

### 4. Apps Script Configuration

#### Update `appsscript.json`

Ensure your manifest includes:

```json
{
  "timeZone": "America/New_York",
  "dependencies": {},
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8",
  "oauthScopes": [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
  ],
  "webapp": {
    "executeAs": "USER_DEPLOYING",
    "access": "ANYONE"
  }
}
```

#### Link to GCP Project

1. Go to script.google.com
2. Open your project
3. Project Settings > Google Cloud Platform (GCP) Project
4. Enter your GCP Project Number
5. Click "Set Project"

## 🎯 Usage

### Triggering Deployments

#### Method 1: Git Tags (Recommended for Production)

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This will automatically:
- Deploy to production environment
- Use the tag as version number
- Submit to marketplace for review

#### Method 2: Merge to Main (Staging)

```bash
# Merge your changes to main branch
git checkout main
git merge feature-branch
git push origin main
```

This will:
- Deploy to staging environment
- Use timestamp as version
- Submit for testing

#### Method 3: Manual Dispatch

Via GitHub UI:
1. Go to Actions tab
2. Select "Deploy to Google Workspace Marketplace"
3. Click "Run workflow"
4. Choose parameters:
   - Environment (staging/production)
   - Version number (optional)
   - GCP strategy
   - Skip tests (optional)

Via GitHub CLI:
```bash
gh workflow run deploy-marketplace.yml \
  -f environment=production \
  -f version=1.0.0 \
  -f gcp_strategy=reuse
```

### Monitoring Approvals

The approval monitor runs automatically every 6 hours to check for:
- Approved submissions → Auto-publish
- Rejected submissions → Create GitHub Issue

#### Manual Approval Check

```bash
gh workflow run monitor-approval.yml \
  -f submission_id=sub-12345 \
  -f force_publish=true
```

## 📊 Workflow Outputs

### Deployment Workflow

After deployment, check:

1. **GitHub Actions Summary**
   - Validation results
   - GCP project details
   - Deployment status
   - Submission summary

2. **Artifacts**
   - `validated-config`: Configuration files used
   - `oauth-config`: OAuth scopes extracted
   - `marketplace-submission`: Submission details

### Approval Workflow

When approvals are found:

1. **Auto-publish** (if configured)
2. **GitHub Issue** (for rejections)
3. **Updated tracker** (`.marketplace-submissions.json`)

## 🔧 Advanced Configuration

### GCP Project Strategies

#### Reuse Strategy (Default)

Automatically finds existing projects with matching labels:

```yaml
gcp:
  strategy: "reuse"
  labels:
    environment: "production"
    team: "myteam"
```

Benefits:
- Maximizes free tier (10 projects)
- Groups related add-ons
- Easier management

#### Create Strategy

Always creates a new project:

```yaml
gcp:
  strategy: "create"
  project_name_pattern: "apps-script-{addon_id}-{random}"
  billing_account_id: "012345-6789AB-CDEF01"
```

Use when:
- Need isolated projects
- Different billing requirements
- Testing purposes

#### Specific Strategy

Uses a pre-defined project:

```yaml
gcp:
  strategy: "specific"
  project_id: "my-existing-project-123"
```

Use when:
- Project already configured
- Manual management preferred
- Legacy projects

### Multi-Language Support

Configure multiple languages:

```yaml
marketplace:
  default_language: "en"
  supported_languages:
    - "fr"
    - "es"
    - "de"
  content:
    tagline:
      en: "Boost your productivity"
      fr: "Boostez votre productivité"
      es: "Aumenta tu productividad"
      de: "Steigern Sie Ihre Produktivität"
    description:
      en: "English description..."
      fr: "Description française..."
```

### Asset Management

#### Option 1: External URLs (Default)

```yaml
marketplace:
  asset_location: "external"
  assets:
    icon:
      external_url: "https://cdn.example.com/icon.png"
```

Benefits:
- No repository bloat
- CDN benefits
- Easy updates

#### Option 2: Repository Files

```yaml
marketplace:
  asset_location: "repo"
  assets:
    icon:
      repo_path: "marketplace/icon.png"
```

Benefits:
- Version controlled
- No external dependencies
- Atomic updates

### Rollback Configuration

Enable automatic rollback on failures:

```yaml
rollback:
  enabled: true
  keep_versions: 5
  create_backup: true
```

This will:
- Backup before deployment
- Restore on failure
- Keep last 5 versions

## 🐛 Troubleshooting

### Common Issues

#### Issue: "Service Account lacks permissions"

**Solution:**
```bash
# Grant additional roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/editor"
```

#### Issue: "OAuth consent screen not configured"

**Solution:**
1. Visit GCP Console > APIs & Services > OAuth consent screen
2. Complete all required fields
3. Add test users (for internal testing)
4. Verify domain ownership (for external apps)

#### Issue: "Script not found"

**Solution:**
- Verify `script_id` in config matches Apps Script project
- Ensure GCP project is linked in Apps Script settings
- Check service account has access to the script

#### Issue: "API not enabled"

**Solution:**
```bash
# Enable required APIs
gcloud services enable script.googleapis.com --project=PROJECT_ID
gcloud services enable cloudresourcemanager.googleapis.com --project=PROJECT_ID
```

#### Issue: "Asset validation failed"

**Solution:**
- Verify image dimensions:
  - Icon: 128x128 PNG
  - Screenshots: 1280x800 PNG
  - Promo: 440x280 PNG
- Ensure PNG format (not JPG)
- Check file accessibility (for external URLs)

### Debugging

Enable debug mode:

```yaml
validation:
  enabled: true
  strict: true  # Fail on warnings
```

Check workflow logs:
1. Go to Actions tab
2. Select failed workflow
3. Expand each step
4. Look for ❌ error messages

### Getting Help

1. **Check Documentation**
   - [Google Apps Script Docs](https://developers.google.com/apps-script)
   - [Workspace Marketplace Guidelines](https://developers.google.com/workspace/marketplace/guidelines)

2. **Review Logs**
   - GitHub Actions logs
   - GCP Cloud Logging
   - Apps Script execution logs

3. **Community Support**
   - Stack Overflow: `[google-apps-script] [deployment]`
   - Google Groups: Apps Script community

## 📚 Additional Resources

### Templates

Example add-ons with full automation:
- [Minimal Example](https://github.com/example/minimal-addon)
- [Full-Featured Example](https://github.com/example/advanced-addon)

### Scripts

Utility scripts for common tasks:
- `scripts/validate-assets.py` - Validate images
- `scripts/test-api-access.py` - Test GCP permissions
- `scripts/generate-descriptions.py` - Generate localized content

### Documentation

- [Google Workspace Marketplace Overview](https://developers.google.com/workspace/marketplace)
- [Apps Script Deployment Guide](https://developers.google.com/apps-script/concepts/deployments)
- [OAuth 2.0 Configuration](https://developers.google.com/identity/protocols/oauth2)

## 🔒 Security Best Practices

1. **Service Account Keys**
   - Never commit keys to repository
   - Rotate keys regularly (every 90 days)
   - Use separate keys for dev/prod

2. **GitHub Secrets**
   - Use environment-specific secrets
   - Enable secret scanning
   - Review access logs

3. **OAuth Scopes**
   - Request minimum necessary scopes
   - Document why each scope is needed
   - Review scope changes in PRs

4. **Domain Verification**
   - Complete verification before external release
   - Keep verification records updated
   - Monitor verification status

## 🎓 Next Steps

After setup:

1. **Test Deployment**
   - Run a staging deployment
   - Verify all steps complete
   - Check generated artifacts

2. **Configure Notifications**
   - Set up Slack/email notifications
   - Test rejection alerts
   - Monitor approval status

3. **Document Process**
   - Add team-specific notes
   - Document custom configurations
   - Create runbooks

4. **Plan Releases**
   - Define versioning strategy
   - Schedule release windows
   - Coordinate with marketing

## ✅ Checklist

Before first deployment:

- [ ] GCP project created
- [ ] Service account configured with proper roles
- [ ] Service account key added to GitHub Secrets
- [ ] OAuth consent screen configured
- [ ] Domain verified (for external apps)
- [ ] Apps Script project linked to GCP
- [ ] `marketplace-config.yaml` customized
- [ ] Assets prepared (icon, screenshots)
- [ ] Privacy policy and ToS URLs accessible
- [ ] Workflow files added to repository
- [ ] Configuration validated locally
- [ ] Test deployment to staging successful

You're now ready to automate your Google Workspace Marketplace deployments! 🚀