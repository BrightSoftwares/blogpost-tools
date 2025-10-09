# 🚀 Google Apps Script Marketplace Automation

Complete, production-ready GitHub Actions workflows for automating the deployment of Google Apps Script add-ons to the Google Workspace Marketplace.

## ✨ Features

- **🔄 Full Automation**: From development to marketplace publication
- **🎯 Smart GCP Management**: Automatically reuses projects to maximize free tier (10 projects)
- **🌍 Multi-Language Support**: Deploy to multiple regions with localized content
- **🔐 Secure**: Service account or OAuth authentication
- **📊 Monitoring**: Automatic approval checking and status updates
- **♻️ Rollback**: Automatic rollback on failures
- **🔔 Notifications**: GitHub Issues for rejections, optional Slack/email
- **🎨 Flexible**: Highly configurable with sensible defaults
- **🧪 Multiple Environments**: Staging and production workflows
- **📦 Version Management**: Supports HEAD and versioned deployments

## 📋 Quick Start

### 1. Prerequisites

- Google Cloud Platform account
- GitHub repository
- Apps Script project (on script.google.com)
- Domain ownership (for external apps)

### 2. Installation

1. **Copy workflow files to your repository:**

```bash
mkdir -p .github/workflows
# Copy deploy-marketplace.yml and monitor-approval.yml to .github/workflows/
```

2. **Create configuration file:**

```bash
# Copy marketplace-config.yaml to your repository root
# Customize with your project details
```

3. **Setup Google Cloud:**

```bash
# Create service account
gcloud iam service-accounts create apps-script-publisher \
    --display-name="Apps Script Publisher"

# Grant roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:apps-script-publisher@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"

# Create key
gcloud iam service-accounts keys create sa-key.json \
    --iam-account=apps-script-publisher@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

4. **Configure GitHub Secrets:**

Go to: `Repository Settings > Secrets and variables > Actions`

Add secret:
- Name: `GCP_SERVICE_ACCOUNT_KEY`
- Value: Contents of `sa-key.json`

5. **Validate setup:**

```bash
python scripts/validate-setup.py
```

### 3. Deploy

**Via Git Tag:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Via GitHub Actions UI:**
1. Go to Actions tab
2. Select "Deploy to Google Workspace Marketplace"
3. Click "Run workflow"
4. Configure options and run

**Via GitHub CLI:**
```bash
gh workflow run deploy-marketplace.yml \
  -f environment=production \
  -f version=1.0.0
```

## 📁 Project Structure

```
your-repo/
├── .github/
│   └── workflows/
│       ├── deploy-marketplace.yml      # Main deployment workflow
│       └── monitor-approval.yml        # Approval monitoring
├── marketplace-config.yaml             # Main configuration
├── marketplace-config.staging.yaml     # Staging overrides (optional)
├── marketplace-config.production.yaml  # Production overrides (optional)
├── appsscript.json                     # Apps Script manifest
├── Code.gs                             # Your Apps Script code
├── marketplace/                        # Assets (if using repo storage)
│   ├── icon.png                       # 128x128 PNG
│   ├── screenshot1.png                # 1280x800 PNG
│   └── screenshot2.png                # 1280x800 PNG
├── scripts/
│   └── validate-setup.py              # Setup validation tool
└── README.md
```

## ⚙️ Configuration

### Minimal Configuration

```yaml
# marketplace-config.yaml
project:
  id: "my-addon"
  name: "My Amazing Add-on"
  script_id: "YOUR_APPS_SCRIPT_ID"

oauth_consent:
  support_email: "support@example.com"
  privacy_policy_url: "https://example.com/privacy"
  terms_of_service_url: "https://example.com/terms"

marketplace:
  assets:
    icon:
      external_url: "https://example.com/icon.png"
    screenshots:
      - external_url: "https://example.com/screenshot1.png"
        caption:
          en: "Main feature"
  content:
    tagline:
      en: "Boost your productivity"
    description:
      en: "Full description here..."
```

### Full Configuration

See [marketplace-config.yaml](marketplace-config.yaml) for all available options.

## 🔄 Workflow Triggers

### Automatic Triggers

1. **Git Tags** (`v*.*.*`) → Production deployment
2. **Push to main/master** → Staging deployment
3. **Schedule** (approval monitor) → Every 6 hours

### Manual Triggers

**Deployment:**
- Environment selection (staging/production)
- Custom version number
- GCP project strategy
- Skip tests option
- Force deploy option

**Approval Monitor:**
- Specific submission ID
- Force publish toggle

## 📊 Workflow Steps

### Deployment Workflow

1. **Validate** - Check configuration and files
2. **Setup GCP** - Create/reuse GCP project, enable APIs
3. **Configure OAuth** - Setup OAuth consent screen
4. **Deploy Script** - Push code to Apps Script
5. **Submit to Marketplace** - Create marketplace listing
6. **Rollback** (on failure) - Restore previous version

### Approval Monitor Workflow

1. **Check Approvals** - Query pending submissions
2. **Publish Approved** - Auto-publish approved add-ons
3. **Handle Rejections** - Create GitHub Issues
4. **Cleanup** - Remove old submission records

## 🎯 GCP Project Strategies

### Reuse (Default) - Recommended

Finds existing projects with matching labels:

```yaml
gcp:
  strategy: "reuse"
  labels:
    environment: "production"
```

**Benefits:**
- Maximizes free tier (10 projects)
- Groups related add-ons
- Easier management

### Create

Always creates a new project:

```yaml
gcp:
  strategy: "create"
  project_name_pattern: "apps-script-{addon_id}-{random}"
```

**Use when:**
- Need isolated projects
- Different billing requirements

### Specific

Uses a pre-defined project:

```yaml
gcp:
  strategy: "specific"
  project_id: "my-project-123"
```

**Use when:**
- Project already configured
- Manual management preferred

## 🌍 Multi-Language Support

```yaml
marketplace:
  default_language: "en"
  supported_languages: ["fr", "es", "de"]
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

## 🎨 Asset Management

### External URLs (Default)

```yaml
marketplace:
  asset_location: "external"
  assets:
    icon:
      external_url: "https://cdn.example.com/icon.png"
```

✅ No repository bloat
✅ CDN benefits
✅ Easy updates

### Repository Files

```yaml
marketplace:
  asset_location: "repo"
  assets:
    icon:
      repo_path: "marketplace/icon.png"
```

✅ Version controlled
✅ No external dependencies
✅ Atomic updates

## 🔒 Security

### Service Account

**Recommended for automation**

```yaml
auth:
  method: "service_account"
```

Store key in GitHub Secret: `GCP_SERVICE_ACCOUNT_KEY`

### OAuth

**Alternative method**

```yaml
auth:
  method: "oauth"
```

Store credentials in secrets:
- `GCP_OAUTH_CLIENT_ID`
- `GCP_OAUTH_CLIENT_SECRET`
- `GCP_OAUTH_REFRESH_TOKEN`

## 🔔 Notifications

### GitHub Issues (Default)

Automatically creates issues for rejections:

```yaml
notifications:
  create_issue_on_rejection: true
  issue_labels:
    - "marketplace-rejection"
    - "deployment"
```

### Slack (Optional)

```yaml
notifications:
  slack:
    enabled: true
    webhook_url_secret: "SLACK_WEBHOOK_URL"
```

### Email (Optional)

```yaml
notifications:
  email:
    enabled: true
    recipients:
      - "team@example.com"
```

## 🐛 Troubleshooting

### Common Issues

**"Service Account lacks permissions"**
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/editor"
```

**"OAuth consent screen not configured"**
- Visit GCP Console > APIs & Services > OAuth consent screen
- Complete all required fields
- Verify domain ownership

**"Script not found"**
- Verify `script_id` in config
- Link GCP project in Apps Script settings
- Check service account access

**"Asset validation failed"**
- Icon: 128x128 PNG
- Screenshots: 1280x800 PNG
- Use PNG format (not JPG)

### Debug Mode

```yaml
validation:
  enabled: true
  strict: true  # Fail on warnings
```

### Validation Tool

```bash
# Run local validation before deployment
python scripts/validate-setup.py
```

## 📚 Documentation

- [Complete Setup Guide](SETUP.md)
- [Configuration Reference](marketplace-config.yaml)
- [Workflow Reference](.github/workflows/deploy-marketplace.yml)
- [Google Apps Script Docs](https://developers.google.com/apps-script)
- [Workspace Marketplace Guidelines](https://developers.google.com/workspace/marketplace/guidelines)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Apps Script team
- GitHub Actions community
- All contributors

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/yourrepo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/yourrepo/discussions)
- **Stack Overflow**: Tag with `[google-apps-script]` `[deployment]`

## 🗺️ Roadmap

- [ ] Support for Chrome Web Store extensions
- [ ] Automated testing before deployment
- [ ] Analytics integration
- [ ] Multi-repository support
- [ ] Terraform integration for GCP resources
- [ ] Advanced rollback strategies

## ⭐ Star History

If this project helped you, please consider giving it a star!

---

Made with ❤️ for the Google Apps Script community