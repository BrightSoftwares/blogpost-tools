# Jekyll Action

A GitHub Action to build and publish Jekyll sites to GitHub Pages with Algolia search support.

This action is based on [helaili/jekyll-action](https://github.com/helaili/jekyll-action) with additional features including Algolia search integration.

## Features

- **Ruby 3.4 compatible** - Works with Ruby 3.2-3.4
- **Pre-installed dependencies** - ImageMagick, libxml2, libffi built into Docker image
- Build Jekyll sites with custom gems (not limited to GitHub's whitelist)
- Automatic deployment to GitHub Pages
- Algolia search data upload support
- Configurable source/target branches
- Multi-version publishing support
- Build caching support
- Pre-build commands execution
- Custom bundler version support

## Quick Start

### Using the Reusable Workflow (Recommended)

The simplest way to use this action is via the reusable workflow:

```yaml
name: Jekyll Build and Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-deploy:
    uses: BrightSoftwares/blogpost-tools/.github/workflows/reusable_jekyll_build_and_deploy.yml@main
    with:
      build_dir: './build'
      deploy_to_netlify: true
    secrets:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      algolia_api_key: ${{ secrets.ALGOLIA_API_KEY }}
      netlify_auth_token: ${{ secrets.NETLIFY_AUTH_TOKEN }}
      netlify_site_id: ${{ secrets.NETLIFY_SITE_ID }}
```

### Direct Usage

```yaml
name: Build and Deploy Jekyll Site

on:
  push:
    branches: [main]

jobs:
  jekyll:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/cache@v4
        with:
          path: vendor/bundle
          key: ${{ runner.os }}-gems-${{ hashFiles('**/Gemfile') }}
          restore-keys: |
            ${{ runner.os }}-gems-

      - uses: BrightSoftwares/blogpost-tools/jekyll-action@main
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
```

## Inputs

| Input | Description | Required |
|-------|-------------|----------|
| `token` | GitHub token for authentication | No (required unless `build_only: true`) |
| `jekyll_env` | Jekyll environment to build (default: `production`) | No |
| `jekyll_src` | Jekyll website source directory | No |
| `jekyll_build_options` | Additional Jekyll build arguments | No |
| `gem_src` | Jekyll Gemfile directory | No |
| `target_branch` | Target branch for deployment | No |
| `target_path` | Relative path where site gets pushed | No |
| `build_only` | Build without publishing | No |
| `build_dir` | Directory to build project in | No |
| `keep_history` | Preserve existing content on target branch | No |
| `pre_build_commands` | Commands to run before build | No |
| `bundler_version` | Override default bundler version | No |
| `commit_author` | Author name for commits | No |
| `algolia_api_key` | Algolia Admin API key for search data upload | No |

## Outputs

| Output | Description |
|--------|-------------|
| `sha` | Generated commit SHA1 that will be published |

---

## Standardizing Jekyll Sites

This section provides guidelines for standardizing multiple Jekyll sites to use the same build process.

### Standardized Gemfile

Use the templates in `templates/` directory:

- **`Gemfile.standard`** - Basic Jekyll site with common plugins
- **`Gemfile.full`** - Full-featured with image processing and admin

#### Key Requirements for Ruby 3.4 Compatibility

```ruby
# Required for Ruby 3.4+ (no longer bundled in stdlib)
gem "csv"
gem "logger"
gem "base64"
gem "bigdecimal"
gem "observer"
gem "ostruct"

# Core Jekyll - pin to 4.2.x for stability
gem 'jekyll', '~> 4.2.2'

# Pin ffi to avoid native extension issues
gem 'ffi', '= 1.16.3'
```

### Standardized Plugin Versions

| Plugin | Recommended Version |
|--------|---------------------|
| jekyll | ~> 4.2.2 |
| jekyll-feed | ~> 0.16.0 |
| jekyll-sitemap | ~> 1.4.0 |
| jekyll-seo-tag | ~> 2.8.0 |
| jekyll-archives | ~> 2.2.1 |
| jekyll-paginate-v2 | ~> 3.0 |
| jekyll-toc | ~> 0.18.0 |
| jekyll-algolia | ~> 1.7.1 |
| jekyll-wikilinks | ~> 0.0.8 |
| jekyll-redirect-from | ~> 0.16.0 |
| jekyll-last-modified-at | ~> 1.3.0 |
| jekyll-timeago | ~> 0.13.1 |

### Pre-installed in Docker Image

The following are **already installed** in the Docker image - no `pre_build_commands` needed:

- ImageMagick (with JPEG, PNG, WebP support)
- ruby-dev
- libxml2-dev, libxslt-dev (for nokogiri)
- libffi-dev
- build-base, git, curl

---

## Migration Guide

### From fullbright/jekyll-action

**Before:**
```yaml
- uses: fullbright/jekyll-action@master
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    pre_build_commands: apk --update add ruby-dev imagemagick imagemagick-dev
```

**After:**
```yaml
- uses: BrightSoftwares/blogpost-tools/jekyll-action@main
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    # pre_build_commands no longer needed - ImageMagick is built-in!
```

### From helaili/jekyll-action

**Before:**
```yaml
- uses: helaili/jekyll-action@v2
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
```

**After:**
```yaml
- uses: BrightSoftwares/blogpost-tools/jekyll-action@main
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
```

### Updating Gemfile for Ruby 3.4

Add these gems to the top of your Gemfile:

```ruby
# Required for Ruby 3.4+
gem "csv"
gem "logger"
gem "base64"
gem "bigdecimal"
gem "observer"
gem "ostruct"
```

---

## Workflow Templates

### Simple Site

See `templates/workflow-simple.yml`

### Multi-language Site (en/fr)

See `templates/workflow-multilang.yml`

---

## Algolia Search Configuration

Add to your `_config.yml`:

```yaml
algolia:
  application_id: 'YOUR_APP_ID'
  index_name: 'YOUR_INDEX_NAME'
  search_only_api_key: 'YOUR_SEARCH_KEY'
```

Add to your Gemfile:

```ruby
gem 'jekyll-algolia', '~> 1.7.1'
```

Use in workflow:

```yaml
- uses: BrightSoftwares/blogpost-tools/jekyll-action@main
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    algolia_api_key: ${{ secrets.ALGOLIA_API_KEY }}
```

---

## Troubleshooting

### Enable Debug Mode

Create a repository secret `ACTIONS_STEP_DEBUG` with value `true`.

### Common Issues

| Issue | Solution |
|-------|----------|
| `Could not locate included file` | Clone submodules before build |
| `ffi gem build fails` | Use `gem 'ffi', '= 1.16.3'` |
| `csv/logger not found` | Add Ruby 3.4 stdlib gems to Gemfile |
| `ImageMagick not found` | Already built-in; remove from pre_build_commands |

### Custom Domains

Ensure `CNAME` file exists in repository root.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

Based on [helaili/jekyll-action](https://github.com/helaili/jekyll-action) by Alain Helaili.
