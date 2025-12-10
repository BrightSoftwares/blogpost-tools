# 📖 Setup Guide for Google Apps Script CLASP Deploy

Complete setup guide for integrating the reusable CLASP deployment workflows into your project.

## Prerequisites

Before starting, ensure you have:

- ✅ Google Apps Script project created
- ✅ GitHub repository for your project
- ✅ CLASP installed and configured locally (`npm install -g @google/clasp`)
- ✅ Node.js project with build scripts

## Step-by-Step Setup

### Step 1: Get Your Credentials

#### 1.1 Get CLASP Authentication Token

```bash
# Login to CLASP
clasp login

# Get your token
cat ~/.clasprc.json
```

Copy the entire contents of `.clasprc.json`. You'll need this for GitHub Secrets.

#### 1.2 Get Google Apps Script IDs

```bash
# In your project directory with .clasp.json
cat .clasp.json
```

Note down:
- `scriptId`: Your Google Apps Script ID
- `projectId`: Your Google Cloud Project ID

#### 1.3 Get Production Deployment ID

1. Go to https://script.google.com
2. Open your project
3. Click **Deploy** → **Manage deployments**
4. Find your production deployment and copy the Deployment ID

### Step 2: Configure GitHub Repository

#### 2.1 Add GitHub Secret

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `CLASP_JSON_TOKEN`
5. Value: Paste the contents of `.clasprc.json`
6. Click **Add secret**

### Step 3: Create Project Files

#### 3.1 Create Version File

In your project root:

```bash
echo "1.0.0" > .version
```

#### 3.2 Create Deployment Config

Create `deployment-config.json` in your project root:

```json
{
  "scriptId": "YOUR_SCRIPT_ID_HERE",
  "projectId": "YOUR_PROJECT_ID_HERE",
  "environments": {
    "dev": {
      "name": "Development",
      "deploymentId": null,
      "description": "Development environment - deploys on push to dev branch",
      "webAppUrlProperty": "WEB_APP_URL_DEV",
      "versionStrategy": "HEAD"
    },
    "production": {
      "name": "Production",
      "deploymentId": "YOUR_PROD_DEPLOYMENT_ID_HERE",
      "description": "Production environment - deploys on merge to main",
      "webAppUrlProperty": "WEB_APP_URL_PROD",
      "versionStrategy": "versioned"
    }
  }
}
```

Replace:
- `YOUR_SCRIPT_ID_HERE` with your actual script ID
- `YOUR_PROJECT_ID_HERE` with your actual project ID
- `YOUR_PROD_DEPLOYMENT_ID_HERE` with your production deployment ID

#### 3.3 Update .gitignore

Add to your `.gitignore`:

```
# Deployment history (local only)
.deployment-history.json

# CLASP credentials (NEVER commit)
.clasprc.json
~/.clasprc.json

# Scripts (copied during workflow)
scripts/version-manager.js
scripts/deploy-helper.js
```

### Step 4: Create Workflow Files

#### 4.1 Create Dev Deployment Workflow

Create `.github/workflows/deploy-dev.yml`:

```yaml
name: 🚀 Deploy to Development

on:
  push:
    branches: [dev]
  pull_request:
    branches: [dev]
  workflow_dispatch:

jobs:
  # Your project-specific unit tests
  unit-tests:
    name: 🧪 Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm test

  # Deploy using reusable workflow
  deploy:
    needs: unit-tests
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_gapps-deploy-dev.yml@main
    with:
      script_id: "YOUR_SCRIPT_ID"
      project_id: "YOUR_PROJECT_ID"
      dev_branch: "dev"
      production_branch: "main"
      build_command_dev: "npm run wp-build-dev"  # Adjust to your build command
      node_version: "20"
    secrets:
      CLASP_JSON_TOKEN: ${{ secrets.CLASP_JSON_TOKEN }}
```

#### 4.2 Create Production Deployment Workflow

Create `.github/workflows/deploy-production.yml`:

```yaml
name: 🚀 Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  # Your project-specific tests
  unit-tests:
    name: 🧪 Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm test

  # Deploy using reusable workflow
  deploy:
    needs: unit-tests
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_gapps-deploy-production.yml@main
    with:
      script_id: "YOUR_SCRIPT_ID"
      project_id: "YOUR_PROJECT_ID"
      prod_deployment_id: "YOUR_PROD_DEPLOYMENT_ID"
      dev_branch: "dev"
      production_branch: "main"
      build_command_prod: "npm run wp-build-prd"  # Adjust to your build command
      node_version: "20"
    secrets:
      CLASP_JSON_TOKEN: ${{ secrets.CLASP_JSON_TOKEN }}
```

#### 4.3 Create Manual Rollback Workflow (Optional)

Create `.github/workflows/rollback.yml`:

```yaml
name: 🔄 Manual Rollback

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to rollback'
        required: true
        type: choice
        options:
          - production
          - dev
      reason:
        description: 'Reason for rollback'
        required: true
        type: string

jobs:
  rollback:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_gapps-rollback.yml@main
    with:
      script_id: "YOUR_SCRIPT_ID"
      project_id: "YOUR_PROJECT_ID"
      environment: ${{ inputs.environment }}
      reason: ${{ inputs.reason }}
      create_issue: true
    secrets:
      CLASP_JSON_TOKEN: ${{ secrets.CLASP_JSON_TOKEN }}
```

### Step 5: Configure Build Commands

Ensure your `package.json` has the build commands referenced in the workflows:

```json
{
  "scripts": {
    "wp-build-dev": "webpack --mode development",
    "wp-build-prd": "webpack --mode production",
    "test": "jest"
  }
}
```

Adjust these to match your actual build process.

### Step 6: Create Branches

```bash
# Create dev branch
git checkout -b dev
git push -u origin dev

# Ensure main exists
git checkout main
```

### Step 7: Test the Setup

#### 7.1 Test Dev Deployment

1. Make a change in a feature branch
2. Commit with conventional commit message:
   ```bash
   git commit -m "feat: Add new feature"
   ```
3. Push to dev:
   ```bash
   git push origin dev
   ```
4. Check GitHub Actions to see the deployment workflow run

#### 7.2 Test Production Deployment

1. Merge dev to main:
   ```bash
   git checkout main
   git merge dev
   git push origin main
   ```
2. Check GitHub Actions for production deployment
3. Verify a new release was created
4. Check that a git tag was created

### Step 8: Configure Web App URLs (Optional)

If your Google Apps Script uses stored URLs, run these functions in the Apps Script editor after deployment:

```javascript
// For dev
setWebAppUrl('https://script.google.com/macros/s/DEV_DEPLOYMENT_ID/dev')

// For production
setWebAppUrl('https://script.google.com/macros/s/PROD_DEPLOYMENT_ID/exec')

// Verify
getWebAppConfig()
```

## Common Customizations

### Custom Build Commands

If your project uses different build commands, update the workflow:

```yaml
with:
  build_command_dev: "npm run build:dev"
  build_command_prod: "npm run build:prod"
```

### Different Branch Names

If you use different branch names:

```yaml
with:
  dev_branch: "develop"
  production_branch: "master"
```

### Custom Version File Location

If your version file is in a different location:

```yaml
with:
  version_file: "config/.version"
```

### Different Node.js Version

If you need a specific Node.js version:

```yaml
with:
  node_version: "18"
```

## Troubleshooting

### Issue: "CLASP_JSON_TOKEN not found"

**Solution**: Verify the secret is added correctly in GitHub Settings → Secrets and variables → Actions.

### Issue: "scriptId not found in config"

**Solution**: Ensure `deployment-config.json` has the correct `scriptId` field.

### Issue: "Deployment failed with 403"

**Solution**:
1. Verify CLASP token is valid (may have expired)
2. Re-run `clasp login` and update the GitHub secret

### Issue: "Build command not found"

**Solution**: Ensure the build command exists in your `package.json` scripts.

### Issue: "Version file not found"

**Solution**: Create `.version` file in project root with initial version (e.g., `1.0.0`).

## Best Practices

1. **Always use conventional commits** for proper version bumping
2. **Test in dev first** before merging to production
3. **Keep .deployment-history.json git-ignored** - it's for rollback tracking only
4. **Monitor deployment workflows** in GitHub Actions
5. **Document your build commands** in package.json
6. **Use semantic versioning** (MAJOR.MINOR.PATCH)

## Next Steps

- Review [README.md](../README.md) for full feature documentation
- Explore semantic versioning with conventional commits
- Set up automatic dev→main promotion (advanced)
- Configure deployment notifications

## Support

For issues or questions:
1. Check workflow logs in GitHub Actions
2. Review this setup guide
3. Create issue in blogpost-tools repository

---

**Last Updated**: 2025-12-10
**Version**: 1.0.0
