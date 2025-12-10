

# 🚀 Google Apps Script CLASP Deploy

Production-ready, reusable CI/CD workflows for Google Apps Script deployments using CLASP.

## ✨ Features

- **🔄 Dual Environments**: Separate dev and production deployments
- **📦 Semantic Versioning**: Automatic version bumping based on conventional commits
- **🔁 Auto-Rollback**: Automatic rollback on deployment failures
- **🎯 Composite Actions**: Self-contained, no repository checkout needed
- **📝 Deployment History**: Track last 50 deployments for rollback
- **🏷️ Auto-Tagging**: Git tags and GitHub releases for production
- **⚡ Reusable Workflows**: Use across multiple projects
- **🛡️ Production-Ready**: Battle-tested deployment pipeline

## 📋 Quick Start

### 1. Prerequisites

- Google Apps Script project
- GitHub repository
- CLASP authentication token (`.clasprc.json` contents)

### 2. Setup Your Project

1. **Create version file** in your repository root:
   ```bash
   echo "1.0.0" > .version
   ```

2. **Create deployment config** (`deployment-config.json`):
   ```json
   {
     "scriptId": "YOUR_SCRIPT_ID",
     "projectId": "YOUR_PROJECT_ID",
     "environments": {
       "dev": {
         "name": "Development",
         "deploymentId": null,
         "webAppUrlProperty": "WEB_APP_URL_DEV",
         "versionStrategy": "HEAD"
       },
       "production": {
         "name": "Production",
         "deploymentId": "YOUR_PROD_DEPLOYMENT_ID",
         "webAppUrlProperty": "WEB_APP_URL_PROD",
         "versionStrategy": "versioned"
       }
     }
   }
   ```

3. **Add GitHub Secret**:
   - Go to Settings → Secrets → Actions
   - Add `CLASP_JSON_TOKEN` with your `.clasprc.json` contents

4. **Create workflow** (`.github/workflows/deploy-dev.yml`):
   ```yaml
   name: Deploy to Development

   on:
     push:
       branches: [dev]

   jobs:
     unit-tests:
       # Your project-specific unit tests
       uses: ./.github/workflows/reusable-unit-tests.yml

     deploy:
       needs: unit-tests
       uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_gapps-deploy-dev.yml@main
       with:
         script_id: "YOUR_SCRIPT_ID"
         project_id: "YOUR_PROJECT_ID"
         dev_branch: "dev"
         production_branch: "main"
         build_command_dev: "npm run wp-build-dev"
       secrets:
         CLASP_JSON_TOKEN: ${{ secrets.CLASP_JSON_TOKEN }}
   ```

## 📦 Available Workflows

### 1. Deploy to Development
**File**: `reusable_gapps-deploy-dev.yml`

Deploys to dev environment (@HEAD deployment).

**Inputs**:
- `script_id` (required): Google Apps Script ID
- `project_id` (required): Google Cloud Project ID
- `dev_deployment_id` (optional): Dev deployment ID
- `dev_branch` (default: `dev`): Development branch name
- `production_branch` (default: `main`): Production branch name
- `build_command_dev` (default: `npm run wp-build-dev`): Build command
- `node_version` (default: `20`): Node.js version
- `version_file` (default: `.version`): Version file path
- `config_file` (default: `deployment-config.json`): Config file path

**Secrets**:
- `CLASP_JSON_TOKEN` (required): CLASP authentication token

### 2. Deploy to Production
**File**: `reusable_gapps-deploy-production.yml`

Deploys to production with versioning, tagging, and releases.

**Inputs**:
- `script_id` (required): Google Apps Script ID
- `project_id` (required): Google Cloud Project ID
- `prod_deployment_id` (required): Production deployment ID
- `dev_branch` (default: `dev`): Development branch name
- `production_branch` (default: `main`): Production branch name
- `build_command_prod` (default: `npm run wp-build-prd`): Build command
- `node_version` (default: `20`): Node.js version
- `version_file` (default: `.version`): Version file path
- `config_file` (default: `deployment-config.json`): Config file path
- `version_override` (optional): Override automatic versioning

**Secrets**:
- `CLASP_JSON_TOKEN` (required): CLASP authentication token

### 3. Rollback
**File**: `reusable_gapps-rollback.yml`

Rollback to previous deployment.

**Inputs**:
- `script_id` (required): Google Apps Script ID
- `project_id` (required): Google Cloud Project ID
- `environment` (required): Environment to rollback (dev/production)
- `reason` (required): Reason for rollback
- `create_issue` (default: `true`): Create tracking issue

## 🎯 Semantic Versioning

Versions are automatically bumped based on conventional commit messages:

```bash
# PATCH: 1.0.0 → 1.0.1
git commit -m "fix: Resolve timezone bug"
git commit -m "chore: Update dependencies"

# MINOR: 1.0.0 → 1.1.0
git commit -m "feat: Add email notifications"
git commit -m "feat(addon): Add quick settings"

# MAJOR: 1.0.0 → 2.0.0
git commit -m "feat!: Redesign addon UI"
git commit -m "feat: New API

BREAKING CHANGE: API v1 removed"
```

## 🔧 Composite Actions

The system includes two composite actions that make workflows self-contained:

### 1. Version Manager
**Path**: `.github/actions/gapps-clasp-deploy/version-manager`

Handles semantic versioning operations.

**Usage**:
```yaml
- uses: BrightSoftwares/blogpost-tools/.github/actions/gapps-clasp-deploy/version-manager@main
  with:
    command: 'get-current'
    version_file: '.version'
```

**Commands**:
- `get-current`: Get current version
- `get-next`: Get next version (based on commits)
- `set`: Set specific version
- `bump`: Bump version automatically
- `description`: Get deployment description
- `info`: Show version info

### 2. Deploy Helper
**Path**: `.github/actions/gapps-clasp-deploy/deploy-helper`

Handles environment-specific deployments.

**Usage**:
```yaml
- uses: BrightSoftwares/blogpost-tools/.github/actions/gapps-clasp-deploy/deploy-helper@main
  with:
    command: 'dev'
    config_file: 'deployment-config.json'
```

**Commands**:
- `dev`: Deploy to development
- `production`: Deploy to production
- `rollback`: Rollback deployment
- `history`: Show deployment history
- `get-deployment-id`: Get deployment ID for environment

## 📁 Project Structure

```
your-project/
├── .github/
│   └── workflows/
│       ├── deploy-dev.yml          # Calls reusable workflow
│       ├── deploy-production.yml    # Calls reusable workflow
│       └── reusable-unit-tests.yml  # Your tests
├── .version                         # Version tracking
├── deployment-config.json           # Deployment configuration
├── .deployment-history.json         # Git-ignored, auto-generated
└── scripts/                         # Auto-copied during workflow
    ├── version-manager.js
    └── deploy-helper.js
```

## 🔐 Security

- **CLASP_JSON_TOKEN**: Store as GitHub Secret (never commit)
- **deployment-config.json**: Safe to commit (contains deployment IDs, not credentials)
- **.deployment-history.json**: Git-ignored (local deployment tracking)

## 🔄 Complete Workflow Example

```yaml
name: Deploy Google Apps Script

on:
  push:
    branches: [dev, main]
  workflow_dispatch:

jobs:
  # Project-specific tests
  unit-tests:
    uses: ./.github/workflows/reusable-unit-tests.yml

  e2e-tests:
    uses: ./.github/workflows/reusable-e2e-tests.yml

  # Deploy to dev (on dev branch)
  deploy-dev:
    if: github.ref == 'refs/heads/dev'
    needs: [unit-tests, e2e-tests]
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_gapps-deploy-dev.yml@main
    with:
      script_id: "YOUR_SCRIPT_ID"
      project_id: "YOUR_PROJECT_ID"
      build_command_dev: "npm run build:dev"
    secrets:
      CLASP_JSON_TOKEN: ${{ secrets.CLASP_JSON_TOKEN }}

  # Deploy to production (on main branch)
  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: [unit-tests, e2e-tests]
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_gapps-deploy-production.yml@main
    with:
      script_id: "YOUR_SCRIPT_ID"
      project_id: "YOUR_PROJECT_ID"
      prod_deployment_id: "YOUR_PROD_DEPLOYMENT_ID"
      build_command_prod: "npm run build:prod"
    secrets:
      CLASP_JSON_TOKEN: ${{ secrets.CLASP_JSON_TOKEN }}
```

## 📚 Documentation

- [SETUP.md](./docs/SETUP.md) - Detailed setup guide
- [Scripts Documentation](./scripts/) - Script usage and API

## 🆘 Support

For issues or questions:
1. Check existing documentation
2. Review workflow logs in GitHub Actions
3. Create issue in blogpost-tools repository

## 📝 License

MIT License - see LICENSE file for details

---

**Maintained by**: BrightSoftwares
**Version**: 1.0.0
