# Jekyll Action

A GitHub Action to build and publish Jekyll sites to GitHub Pages with Algolia search support.

This action is based on [helaili/jekyll-action](https://github.com/helaili/jekyll-action) with additional features including Algolia search integration.

## Features

- Build Jekyll sites with custom gems (not limited to GitHub's whitelist)
- Automatic deployment to GitHub Pages
- Algolia search data upload support
- Configurable source/target branches
- Multi-version publishing support
- Build caching support
- Pre-build commands execution
- Custom bundler version support

## Usage

### Basic Usage

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

      # Use cache to speed up builds
      - uses: actions/cache@v4
        with:
          path: vendor/bundle
          key: ${{ runner.os }}-gems-${{ hashFiles('**/Gemfile') }}
          restore-keys: |
            ${{ runner.os }}-gems-

      - uses: brightsoftwares/blogpost-tools/jekyll-action@main
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
```

### With Algolia Search

```yaml
- uses: brightsoftwares/blogpost-tools/jekyll-action@main
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    algolia_api_key: ${{ secrets.ALGOLIA_API_KEY }}
```

### Build Only (No Publish)

```yaml
- uses: brightsoftwares/blogpost-tools/jekyll-action@main
  with:
    build_only: true
```

### Specify Source Directory

```yaml
- uses: brightsoftwares/blogpost-tools/jekyll-action@main
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    jekyll_src: 'docs'
```

### Multi-Version Publishing

```yaml
jobs:
  publish-current:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
      - uses: brightsoftwares/blogpost-tools/jekyll-action@main
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          target_branch: gh-pages
          target_path: /
          keep_history: true

  publish-v2:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: v2.0
      - uses: brightsoftwares/blogpost-tools/jekyll-action@main
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          target_branch: gh-pages
          target_path: v2.0
          keep_history: true
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

## Requirements

Your Jekyll site should have:

1. A `Gemfile` declaring dependencies
2. A `_config.yml` configuration file

### Example Gemfile

```ruby
source 'https://rubygems.org'

gem 'jekyll', '~> 4.3'

group :jekyll_plugins do
  gem 'jekyll-feed'
  gem 'jekyll-seo-tag'
  gem 'jekyll-algolia'  # For Algolia search
end
```

### Algolia Configuration

To use Algolia search, add to your `_config.yml`:

```yaml
algolia:
  application_id: 'YOUR_APP_ID'
  index_name: 'YOUR_INDEX_NAME'
  search_only_api_key: 'YOUR_SEARCH_KEY'
```

## Troubleshooting

### Enable Debug Mode

Create a repository secret `ACTIONS_STEP_DEBUG` with value `true` and run the workflow again.

### Custom Domains

If using a custom domain, ensure the `CNAME` file exists in your repository root on the main branch.

## Migration from fullbright/jekyll-action

Replace:
```yaml
- uses: fullbright/jekyll-action@master
```

With:
```yaml
- uses: brightsoftwares/blogpost-tools/jekyll-action@main
```

All inputs remain compatible.

## License

MIT License - See [LICENSE](LICENSE) for details.

Based on [helaili/jekyll-action](https://github.com/helaili/jekyll-action) by Alain Helaili.
