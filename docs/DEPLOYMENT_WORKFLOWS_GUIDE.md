# Deployment Workflows Guide

> **Complete guide to deploying applications using reusable GitHub Actions workflows**
> **All workflows are idempotent** - they check if resources exist before creating them

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Supported Hosting Providers](#supported-hosting-providers)
- [Workflow Reference](#workflow-reference)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

This repository includes **idempotent deployment workflows** that:

✅ Check if applications are already deployed (avoiding duplicate deployments)
✅ Support multiple hosting providers (o2switch, AWS, GCP, Azure)
✅ Use free tier resources by default
✅ Handle secrets securely
✅ Provide detailed deployment summaries
✅ Can be called from other workflows

### Key Features

- **Idempotent**: Safe to run multiple times
- **Multi-Cloud**: Deploy to any major provider
- **Free-Tier First**: Default to free tier options
- **Type-Safe**: Strongly typed inputs with validation
- **Comprehensive**: Full deployment lifecycle support

---

## Quick Start

### Option 1: Use Master Orchestrator (Recommended)

```yaml
name: Deploy My App

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: ./.github/workflows/reusable_deploy-application.yml
    with:
      app_name: "my-awesome-app"
      hosting_provider: "gcp"  # o2switch, aws, gcp, azure
      gcp_project_id: "my-project-123"
      gcp_deployment_target: "cloud-run"
      use_free_tier: true
    secrets:
      GCP_SERVICE_ACCOUNT_KEY: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
```

### Option 2: Use Provider-Specific Workflow

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/reusable_deploy-to-gcp.yml
    with:
      app_name: "my-app"
      deployment_target: "cloud-run"
      gcp_project_id: "my-project"
    secrets:
      GCP_SERVICE_ACCOUNT_KEY: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
```

---

## Supported Hosting Providers

### 1. o2switch (cPanel Shared Hosting)

**File**: `reusable_deploy-to-o2switch.yml`

**Best For**: PHP/Laravel apps, Node.js apps, static sites

**Monthly Cost**: €7/month (~€84/year)

**Features**:
- SSH/SFTP deployment
- cPanel Node.js Selector support
- PostgreSQL databases
- Unlimited bandwidth

**Free Tier**: No free tier, but very affordable

**Example**:
```yaml
uses: ./.github/workflows/reusable_deploy-to-o2switch.yml
with:
  app_name: "myapp"
  app_type: "php-laravel"  # nodejs, php-laravel, static-site, python
  domain_name: "myapp.com"
  cpanel_username: "myusername"
secrets:
  CPANEL_SSH_KEY: ${{ secrets.CPANEL_SSH_KEY }}
  # OR use password:
  # CPANEL_PASSWORD: ${{ secrets.CPANEL_PASSWORD }}
```

**Idempotency**: Checks if app directory exists and application is running

---

### 2. AWS (Amazon Web Services)

**File**: `reusable_deploy-to-aws.yml`

**Deployment Targets**:
- `s3-cloudfront`: Static websites (S3 + CloudFront CDN)
- `lambda`: Serverless functions
- `ecs-fargate`: Docker containers
- `ec2`: Virtual machines
- `elastic-beanstalk`: Platform as a Service

**Free Tier**:
- S3: 5 GB storage, 20,000 GET requests
- Lambda: 1M requests/month, 400,000 GB-seconds
- EC2: 750 hours/month t2.micro instance
- CloudFront: 50 GB data transfer

**Example**:
```yaml
uses: ./.github/workflows/reusable_deploy-to-aws.yml
with:
  app_name: "myapp"
  deployment_target: "s3-cloudfront"  # or lambda, ecs-fargate, ec2
  aws_region: "us-east-1"
  app_type: "static-site"
  s3_bucket_name: "myapp-website"
  use_free_tier: true
secrets:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**Idempotency**: Checks if S3 bucket, Lambda function, or EC2 instance exists

---

### 3. GCP (Google Cloud Platform)

**File**: `reusable_deploy-to-gcp.yml`

**Deployment Targets**:
- `cloud-run`: Serverless containers (recommended)
- `app-engine`: Platform as a Service
- `cloud-functions`: Serverless functions
- `gce`: Compute Engine VMs
- `cloud-storage`: Static websites

**Free Tier**:
- Cloud Run: 2M requests/month, 360,000 GB-seconds memory
- App Engine: 28 instance hours/day
- Cloud Functions: 2M invocations/month
- GCE: 1 e2-micro instance, 30 GB storage
- Cloud Storage: 5 GB storage

**Example**:
```yaml
uses: ./.github/workflows/reusable_deploy-to-gcp.yml
with:
  app_name: "myapp"
  deployment_target: "cloud-run"  # cloud-run, app-engine, cloud-functions
  gcp_project_id: "my-project-id"
  gcp_region: "us-central1"
  app_type: "nodejs"
  cloudrun_min_instances: 0  # Free tier friendly
  use_free_tier: true
secrets:
  GCP_SERVICE_ACCOUNT_KEY: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
```

**Idempotency**: Checks if Cloud Run service, Function, or GCE instance exists

---

### 4. Azure (Microsoft Azure)

**File**: `reusable_deploy-to-azure.yml`

**Deployment Targets**:
- `app-service`: Web Apps (recommended)
- `functions`: Azure Functions
- `container-instances`: Docker containers
- `static-web-apps`: Static websites

**Free Tier**:
- App Service: 10 web apps, F1 tier (60 CPU minutes/day)
- Functions: 1M executions/month, 400,000 GB-seconds
- Static Web Apps: Unlimited static sites with staging

**Example**:
```yaml
uses: ./.github/workflows/reusable_deploy-to-azure.yml
with:
  app_name: "myapp"
  deployment_target: "app-service"  # app-service, functions
  azure_subscription_id: "sub-id-here"
  resource_group: "myresourcegroup"
  location: "eastus"
  app_service_sku: "F1"  # Free tier
  use_free_tier: true
secrets:
  AZURE_CREDENTIALS: ${{ secrets.AZURE_CREDENTIALS }}
```

**Idempotency**: Checks if App Service or Function App exists

---

## Workflow Reference

### Master Orchestrator

**File**: `reusable_deploy-application.yml`

**Purpose**: Intelligent routing to provider-specific workflows

**Key Inputs**:
```yaml
app_name: string (required)
hosting_provider: choice (required) - o2switch|aws|gcp|azure
app_type: string - nodejs|python|php-laravel|docker|static-site
force_redeploy: boolean - Force even if exists (default: false)
use_free_tier: boolean - Use free tier (default: true)
```

**Outputs**:
```yaml
deployment_status: success|skipped|failed
deployment_url: Application URL
hosting_provider: Provider used
```

---

## Examples

### Example 1: Deploy Static Site to AWS S3

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: ./.github/workflows/reusable_deploy-to-aws.yml
    with:
      app_name: "portfolio-website"
      deployment_target: "s3-cloudfront"
      aws_region: "us-east-1"
      app_type: "static-site"
      s3_bucket_name: "my-portfolio-site"
      source_directory: "./dist"
      use_free_tier: true
      force_redeploy: false
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**Result**:
- ✅ Checks if S3 bucket exists
- ✅ Creates bucket if needed with website hosting enabled
- ✅ Syncs files to S3
- ✅ Invalidates CloudFront cache
- ✅ Returns website URL

### Example 2: Deploy Node.js App to GCP Cloud Run

```yaml
name: Deploy to GCP

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: ./.github/workflows/reusable_deploy-to-gcp.yml
    with:
      app_name: "api-server"
      deployment_target: "cloud-run"
      gcp_project_id: "my-project-12345"
      gcp_region: "us-central1"
      app_type: "nodejs"
      cloudrun_min_instances: 0  # Scale to zero
      cloudrun_max_instances: 10
      cloudrun_memory: "512Mi"
      allow_unauthenticated: true
      use_free_tier: true
    secrets:
      GCP_SERVICE_ACCOUNT_KEY: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
      ENV_FILE_CONTENT: ${{ secrets.ENV_FILE }}
```

**Result**:
- ✅ Checks if Cloud Run service exists
- ✅ Builds container image
- ✅ Deploys to Cloud Run with free tier settings
- ✅ Sets environment variables
- ✅ Returns service URL

### Example 3: Deploy Laravel App to o2switch

```yaml
name: Deploy to o2switch

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: ./.github/workflows/reusable_deploy-to-o2switch.yml
    with:
      app_name: "laravel-crm"
      app_type: "php-laravel"
      domain_name: "crm.mycompany.com"
      cpanel_username: "myaccount"
      deployment_path: "public_html/crm"
      run_migrations: true
      install_dependencies: true
      build_assets: true
    secrets:
      CPANEL_SSH_KEY: ${{ secrets.O2SWITCH_SSH_KEY }}
      ENV_FILE_CONTENT: ${{ secrets.LARAVEL_ENV }}
      DATABASE_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

**Result**:
- ✅ Checks if app is deployed and running
- ✅ Creates backup of existing installation
- ✅ Uploads deployment package via SSH
- ✅ Runs composer install
- ✅ Builds assets (npm run build)
- ✅ Runs migrations
- ✅ Caches Laravel config/routes/views

### Example 4: Multi-Environment Deployment

```yaml
name: Deploy to Multiple Environments

on:
  push:
    branches: [main, staging, develop]

jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    uses: ./.github/workflows/reusable_deploy-application.yml
    with:
      app_name: "myapp-staging"
      hosting_provider: "gcp"
      gcp_project_id: "myproject-staging"
      gcp_deployment_target: "cloud-run"
    secrets:
      GCP_SERVICE_ACCOUNT_KEY: ${{ secrets.GCP_KEY_STAGING }}

  deploy-production:
    if: github.ref == 'refs/heads/main'
    uses: ./.github/workflows/reusable_deploy-application.yml
    with:
      app_name: "myapp-production"
      hosting_provider: "aws"
      aws_deployment_target: "ecs-fargate"
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY_PROD }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_PROD }}

  deploy-development:
    if: github.ref == 'refs/heads/develop'
    uses: ./.github/workflows/reusable_deploy-application.yml
    with:
      app_name: "myapp-dev"
      hosting_provider: "o2switch"
      cpanel_username: "devaccount"
    secrets:
      CPANEL_SSH_KEY: ${{ secrets.O2SWITCH_KEY }}
```

---

## Best Practices

### 1. Use Idempotency

Always leverage the idempotency feature:

```yaml
# This is safe to run multiple times:
force_redeploy: false  # Will skip if already deployed

# Only when you actually need to redeploy:
force_redeploy: true  # Forces redeployment
```

### 2. Start with Free Tier

```yaml
use_free_tier: true  # Default, but be explicit
cloudrun_min_instances: 0  # Scale to zero for GCP
app_service_sku: "F1"  # Free tier for Azure
```

### 3. Secure Your Secrets

```yaml
# ✅ Good: Use GitHub Secrets
secrets:
  API_KEY: ${{ secrets.API_KEY }}

# ❌ Bad: Hardcode secrets
env:
  API_KEY: "hardcoded-key-here"
```

### 4. Use Environment Files

```yaml
secrets:
  ENV_FILE_CONTENT: ${{ secrets.ENV_FILE }}
```

Store in GitHub Secrets as:
```
NODE_ENV=production
API_URL=https://api.example.com
DATABASE_URL=postgres://...
```

### 5. Backup Before Deploy

```yaml
skip_backup: false  # Always backup (default)
```

### 6. Test in Staging First

```yaml
# Deploy to staging on PR
on:
  pull_request:
    branches: [main]

# Deploy to production on merge
on:
  push:
    branches: [main]
```

---

## Troubleshooting

### Issue: "Resource already exists" Error

**Solution**: This is actually good! The workflow detected an existing deployment.

```yaml
# To redeploy anyway:
force_redeploy: true
```

### Issue: Authentication Failed (AWS/GCP/Azure)

**Check**:
1. Secrets are set in GitHub repo settings
2. Service account has correct permissions
3. Credentials haven't expired

### Issue: o2switch SSH Connection Failed

**Check**:
1. IP is whitelisted (max 5 IPs for o2switch)
2. SSH key is correctly formatted
3. Username is correct

**Add IP to whitelist**:
1. Login to o2switch cPanel
2. Go to Security > SSH Access
3. Add GitHub Actions IP ranges

### Issue: Deployment Skipped

**This is expected behavior!** The workflow is idempotent.

To force deployment:
```yaml
force_redeploy: true
```

### Issue: Free Tier Limits Exceeded

**Monitor usage**:
- AWS: CloudWatch
- GCP: Cloud Monitoring
- Azure: Azure Monitor

**Set up billing alerts!**

---

## Cost Comparison

| Provider | Free Tier | Monthly Cost (Paid) | Best For |
|----------|-----------|---------------------|----------|
| **o2switch** | None | €7/month | cPanel users, PHP apps |
| **AWS S3** | 5GB, 20K requests | ~$1-5/month | Static sites |
| **AWS Lambda** | 1M requests | ~$0-10/month | Serverless functions |
| **GCP Cloud Run** | 2M requests | ~$0-20/month | Containers, APIs |
| **Azure App Service** | F1 tier | ~$0-50/month | .NET, Node.js apps |

**Recommendation**: Start with free tiers, monitor usage, scale as needed.

---

## Additional Resources

- [o2switch Documentation](https://faq.o2switch.fr)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [GCP Free Tier](https://cloud.google.com/free)
- [Azure Free Tier](https://azure.microsoft.com/free/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

*For infrastructure setup workflows (Mautic, Matomo, CRM, etc.), see [PRODUCT_INFRASTRUCTURE_WORKFLOWS.md](./PRODUCT_INFRASTRUCTURE_WORKFLOWS.md)*
