# Product Infrastructure Workflows - User Guide

> **Purpose**: This document explains how to use the reusable workflows to set up infrastructure for new products based on the Simplexity project analysis.

---

## Overview

This repository contains reusable GitHub Actions workflows that automate the setup of complete product infrastructure including:

- **Marketing Tools**: Mautic (email marketing) + Matomo (analytics)
- **CRM & Support**: Dolibarr/SuiteCRM + FreeScout
- **Social Media**: Automated registration checklists for all major platforms
- **Deployment**: CI/CD pipelines for various tech stacks
- **Documentation**: Complete setup guides and configuration templates

---

## Available Workflows

### 1. New Product Infrastructure Setup
**File**: `.github/workflows/new-product-infrastructure-setup.yml`

**Purpose**: Creates complete infrastructure documentation, scripts, and checklists for a new product.

**Parameters**:
- `product_name` (required): Display name (e.g., "Simplexity")
- `product_slug` (required): URL-friendly name (e.g., "simplexity")
- `domain_name` (optional): Domain (defaults to `{product_slug}.com`)
- `hosting_provider` (optional): cpanel | netlify | vercel | aws | digitalocean
- `tech_stack` (optional): laravel-vue | nextjs | jekyll | wordpress | django
- `setup_marketing_tools` (optional): Boolean, default true
- `setup_crm` (optional): Boolean, default true
- `setup_support` (optional): Boolean, default true
- `setup_automation` (optional): Boolean, default true
- `setup_social_media` (optional): Boolean, default true
- `budget_tier` (optional): minimal | standard | premium

**Outputs**:
- `infrastructure/{product_slug}/README.md` - Main infrastructure documentation
- `infrastructure/{product_slug}/docs/social-media-registration.md` - Social media checklist
- `infrastructure/{product_slug}/docs/cost-tracking.md` - Budget tracking template
- `infrastructure/{product_slug}/scripts/deploy.sh` - Deployment script

### 2. Setup Marketing Tools
**File**: `.github/workflows/setup-marketing-tools.yml`

**Purpose**: Generate setup guides and configuration for Mautic and Matomo.

**Parameters**:
- `product_slug` (required): Product identifier
- `server_host` (required): Server hostname/IP
- `server_user` (required): SSH username
- `setup_mautic` (optional): Boolean, default true
- `setup_matomo` (optional): Boolean, default true
- `domain_mautic` (optional): Mautic subdomain
- `domain_matomo` (optional): Matomo subdomain

**Outputs**:
- `infrastructure/{product_slug}/marketing/mautic/SETUP_GUIDE.md`
- `infrastructure/{product_slug}/marketing/mautic/config.yml`
- `infrastructure/{product_slug}/marketing/matomo/SETUP_GUIDE.md`

### 3. Setup CRM and Support
**File**: `.github/workflows/setup-crm-support.yml`

**Purpose**: Generate setup guides for CRM (Dolibarr/SuiteCRM) and support (FreeScout).

**Parameters**:
- `product_slug` (required): Product identifier
- `crm_type` (required): dolibarr | suitecrm
- `setup_support` (optional): Boolean, default true

**Outputs**:
- `infrastructure/{product_slug}/crm/DOLIBARR_SETUP.md` or `SUITECRM_SETUP.md`
- `infrastructure/{product_slug}/support/FREESCOUT_SETUP.md`

---

## Usage Examples

### Example 1: Setup Complete Infrastructure for New Product

```bash
# Navigate to Actions tab in GitHub
# Select "New Product Infrastructure Setup" workflow
# Click "Run workflow"
# Fill in parameters:
```

**Parameters**:
```yaml
product_name: "MyAmazingProduct"
product_slug: "myamazingproduct"
domain_name: "myamazingproduct.com"
hosting_provider: "cpanel"
tech_stack: "laravel-vue"
setup_marketing_tools: true
setup_crm: true
setup_support: true
setup_automation: true
setup_social_media: true
budget_tier: "minimal"
```

**Result**: Creates `infrastructure/myamazingproduct/` with complete documentation.

### Example 2: Setup Only Marketing Tools

```bash
# Select "Setup Marketing Tools" workflow
# Fill in parameters:
```

**Parameters**:
```yaml
product_slug: "myamazingproduct"
server_host: "server.example.com"
server_user: "deploy"
setup_mautic: true
setup_matomo: true
domain_mautic: "mail.myamazingproduct.com"
domain_matomo: "analytics.myamazingproduct.com"
```

**Result**: Creates marketing tools setup guides in `infrastructure/myamazingproduct/marketing/`.

### Example 3: Minimal Budget Setup

```bash
# Use "New Product Infrastructure Setup" with:
```

**Parameters**:
```yaml
product_name: "StartupApp"
product_slug: "startupapp"
budget_tier: "minimal"  # < $50/month
setup_marketing_tools: true
setup_crm: false  # Skip to save costs
setup_support: true  # Use free FreeScout
setup_automation: false  # Skip initially
```

**Result**: Creates minimal infrastructure setup (~$175/month).

---

## Infrastructure Components Breakdown

### Marketing Stack (~$80/month minimal)
- **Mautic**: Email marketing automation (self-hosted, ~$50/month server)
- **Matomo**: Privacy-focused analytics (self-hosted, ~$30/month server)

**Features**:
- Email campaigns
- Marketing automation
- Lead scoring
- A/B testing
- Visitor analytics
- Conversion tracking

### CRM Stack (~$50/month minimal)
- **Dolibarr** (recommended): Open-source ERP/CRM
- **SuiteCRM**: Alternative CRM option

**Features**:
- Contact management
- Sales pipeline
- Opportunity tracking
- Invoice generation
- Customer segmentation

### Support Stack (Free - FreeScout)
- **FreeScout**: Open-source helpdesk (free, self-hosted)

**Features**:
- Multi-mailbox support
- Canned responses
- Customer portal
- Team collaboration
- API integration

### Automation Stack (~$40/month minimal)
- **n8n**: Self-hosted automation platform

**Features**:
- Visual workflow builder
- 200+ integrations
- Custom nodes
- Webhook support
- Scheduled workflows

---

## Budget Tiers Comparison

### Minimal Tier (< $50/month)
- Shared hosting (€5/month)
- Shared servers for tools (~$175/month total)
- Basic features
- Good for MVP/early stage

### Standard Tier ($50-$200/month)
- Better hosting (€15/month)
- Dedicated tool servers (~$305/month total)
- Video hosting (Vimeo Pro $20/month)
- Enhanced features
- Good for growing products

### Premium Tier (> $200/month)
- Cloud hosting (€50/month)
- Enterprise tool configurations (~$700/month total)
- Advanced integrations
- High availability
- Good for established products

---

## Implementation Timeline

### Week 1: Foundation
1. Run "New Product Infrastructure Setup" workflow
2. Purchase domain
3. Setup hosting
4. Configure DNS and SSL
5. Deploy base application

### Week 2: Marketing & CRM
1. Run "Setup Marketing Tools" workflow
2. Install Mautic and Matomo
3. Run "Setup CRM and Support" workflow
4. Install CRM
5. Configure email campaigns

### Week 3: Support & Automation
1. Install FreeScout
2. Setup n8n automation
3. Configure workflows
4. Test integrations

### Week 4: Social Media & Launch
1. Follow social media registration checklist
2. Create brand assets
3. Setup social media management
4. Plan launch content
5. Go live!

---

## Post-Setup Maintenance

### Daily
- Monitor application logs
- Check support tickets
- Review error reports

### Weekly
- Backup databases
- Update security patches
- Review analytics
- Process support queue

### Monthly
- Review and optimize costs
- Analyze growth metrics
- Update content calendar
- Test disaster recovery

### Quarterly
- Security audit
- Performance optimization
- Feature planning
- Infrastructure scaling review

---

## Troubleshooting

### Workflow Doesn't Run
- Check GitHub Actions permissions
- Verify workflow file syntax
- Ensure all required parameters provided

### Generated Files Not Created
- Check workflow logs for errors
- Verify directory permissions
- Ensure git push succeeded

### Missing Documentation
- Re-run specific workflow
- Check for merge conflicts
- Verify file paths

---

## Best Practices

### Before Running Workflows

1. **Plan Your Infrastructure**
   - Decide on budget tier
   - Choose tech stack
   - Identify required tools

2. **Prepare Domain & Hosting**
   - Have domain ready (or plan to purchase)
   - Choose hosting provider
   - Get server access details

3. **Review Cost Breakdown**
   - Understand monthly costs
   - Plan for scaling
   - Budget for annual renewals

### After Running Workflows

1. **Review Generated Documentation**
   - Read all setup guides thoroughly
   - Note configuration requirements
   - Understand dependencies

2. **Customize for Your Needs**
   - Update configuration templates
   - Adjust workflows
   - Modify scripts as needed

3. **Follow Security Best Practices**
   - Use strong passwords
   - Enable 2FA everywhere
   - Regular backups
   - Keep software updated

---

## Integration with Bright Softwares Brand

All workflows are designed to align with Bright Softwares company values:

1. **Simplicity Through Intelligence**: Automated setup reduces complexity
2. **Trustworthy Reliability**: Comprehensive documentation ensures consistency
3. **Authentic Success**: Transparent costs and ethical tooling

Reference the company information document for brand consistency:
- `docs/BRIGHT_SOFTWARES_COMPANY_INFO.md`

---

## Support & Questions

### Need Help?
1. Review the generated documentation in `infrastructure/{product_slug}/`
2. Check official tool documentation:
   - Mautic: https://docs.mautic.org
   - Matomo: https://matomo.org/docs/
   - Dolibarr: https://wiki.dolibarr.org
   - FreeScout: https://freescout.net/docs/
   - n8n: https://docs.n8n.io

### Contributing
Feel free to improve these workflows:
1. Test your changes
2. Update documentation
3. Submit pull request
4. Describe improvements clearly

---

## License & Credits

Based on Simplexity project infrastructure analysis from Bright Softwares.

*Last Updated: 2025-11-05*
