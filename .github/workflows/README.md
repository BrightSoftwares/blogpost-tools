# Reusable Jekyll Build Workflow

This repository provides a reusable GitHub Actions workflow for building Jekyll sites with standardized configuration.

## Features

✅ **Standardized Jekyll 4.3.4 + Ruby 3.4.1** build environment
✅ **Flexible configuration** via workflow inputs
✅ **Algolia search indexing** support
✅ **Pre-build command execution**
✅ **Build artifact uploads**
✅ **Automatic build summaries**
✅ **Runner flexibility** (ubuntu-latest or self-hosted)

## Usage

### Basic Example

Create `.github/workflows/jekyll.yml` in your repository:

```yaml
name: Build Jekyll Site

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      ruby-version: '3.4.1'
      jekyll-version: '4.3.4'
```

### With Algolia Search

```yaml
name: Build with Algolia

on:
  push:
    branches: [ main ]

jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      enable-algolia: true
      runner: 'ubuntu-latest'
    secrets:
      ALGOLIA_API_KEY: ${{ secrets.ALGOLIA_API_KEY }}
```

### With Pre-build Commands

```yaml
name: Build with Custom Steps

on:
  push:
    branches: [ main ]

jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      pre-build-commands: |
        npm install
        npm run build
        bundle exec rake generate_data
      build-destination: './public'
```

## Configuration Options

### Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ruby-version` | string | No | `3.4.1` | Ruby version to use |
| `jekyll-version` | string | No | `4.3.4` | Jekyll version (informational) |
| `pre-build-commands` | string | No | `''` | Commands to run before Jekyll build |
| `build-destination` | string | No | `./build` | Jekyll build output directory |
| `enable-algolia` | boolean | No | `false` | Enable Algolia search indexing |
| `runner` | string | No | `ubuntu-latest` | GitHub Actions runner type |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `ALGOLIA_API_KEY` | Only if `enable-algolia` is `true` | Algolia API key for indexing |

### Outputs

| Output | Description |
|--------|-------------|
| `build-status` | Build completion status (`success` or `failure`) |
| `build-time` | Build duration in seconds |

## Migration Guide

### Migrating from Custom Workflows

#### Before (Custom Workflow)

```yaml
name: Jekyll Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.4.1'
          bundler-cache: true

      - run: |
          bundle install
          bundle exec jekyll build

      - uses: actions/upload-artifact@v4
        with:
          name: site
          path: ./_site
```

#### After (Reusable Workflow)

```yaml
name: Jekyll Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      build-destination: './_site'
```

**Benefits:**
- ✅ Reduced from ~20 lines to ~10 lines
- ✅ Standardized across all repos
- ✅ Centralized updates (fix once, applies everywhere)
- ✅ Built-in best practices
- ✅ Automatic summaries and artifacts

## Advanced Usage

### Using Outputs

```yaml
jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Check build status
        run: |
          echo "Build status: ${{ needs.build.outputs.build-status }}"
          echo "Build time: ${{ needs.build.outputs.build-time }}s"

      - name: Deploy
        if: needs.build.outputs.build-status == 'success'
        run: |
          echo "Deploying site..."
```

### Self-hosted Runners

```yaml
jobs:
  build:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable-jekyll-build.yml@main
    with:
      runner: 'self-hosted'
```

## Requirements

Your Jekyll project must have:
1. `Gemfile` with Jekyll and plugin dependencies
2. `_config.yml` for Jekyll configuration
3. For Algolia: `ALGOLIA_API_KEY` secret configured in repository settings

## Troubleshooting

### Build Fails with Missing Dependencies

**Problem:** `bundle install` fails with missing gems
**Solution:** Ensure all plugins are listed in your `Gemfile`

### Algolia Indexing Fails

**Problem:** Algolia step fails with authentication error
**Solution:** Verify `ALGOLIA_API_KEY` secret is set in repository settings

### Pre-build Commands Not Working

**Problem:** Custom commands in `pre-build-commands` fail
**Solution:** Ensure commands are available in the runner environment. You may need to install additional tools.

## Support

For issues or questions:
1. Check the [examples/](examples/) directory for reference implementations
2. Review build logs in GitHub Actions
3. Open an issue in this repository

## Changelog

### v1.0.0 (2025-11-24)
- Initial release
- Jekyll 4.3.4 + Ruby 3.4.1 support
- Algolia integration
- Pre-build commands
- Artifact uploads
- Build summaries
