# Common Includes for Jekyll Sites

Reusable Jekyll include templates that can be shared across all your Jekyll sites via the `jekyll-theme-common-includes` submodule.

## Installation

### Option 1: Git Submodule (Recommended)

Add as a submodule to your Jekyll site:

```bash
git submodule add https://github.com/BrightSoftwares/jekyll-theme-common-includes.git _includes/common
```

Update your `.gitmodules`:
```
[submodule "_includes/common"]
    path = _includes/common
    url = https://github.com/BrightSoftwares/jekyll-theme-common-includes.git
```

### Option 2: Direct Copy

Copy the desired includes directly to your `_includes/common/` directory.

## Available Components

### i18n (Internationalization)

#### Language Switcher
```liquid
{% include common/i18n/language-switcher.html %}
```

Configuration in `_config.yml`:
```yaml
languages: ["en", "fr", "de", "es"]
default_lang: "en"
i18n_method: "folder"  # or "param"
```

#### Translation Helper
```liquid
{% include common/i18n/t.html key="navigation.home" %}
{% include common/i18n/t.html key="buttons.submit" default="Submit" %}
```

Create `_data/i18n/en.yml`:
```yaml
navigation:
  home: Home
  about: About
buttons:
  submit: Submit
```

### Analytics

#### Google Analytics 4
```liquid
{% include common/analytics/google-analytics.html %}
```

Configuration:
```yaml
google_analytics: "G-XXXXXXXXXX"
require_cookie_consent: true  # Optional: defer until consent
```

### GDPR Compliance

#### Cookie Consent Banner
```liquid
{% include common/gdpr/cookie-consent.html %}
```

Configuration:
```yaml
cookie_consent:
  enabled: true
  privacy_page: "/privacy"
  button_text: "Accept"
  message: "We use cookies to improve your experience."
  expires_days: 365
```

### SEO

#### Meta Tags
```liquid
{% include common/seo/meta-tags.html %}
```

Provides:
- Primary meta tags (title, description, author)
- Open Graph tags (Facebook)
- Twitter Cards
- Canonical URLs
- Language alternates (hreflang)
- JSON-LD structured data
- Breadcrumb schema

Configuration:
```yaml
title: Site Title
description: Site description
url: https://example.com
author: Author Name
twitter:
  username: "@twitterhandle"
  card: summary_large_image
facebook:
  app_id: "123456789"
logo: /assets/images/logo.png
default_image: /assets/images/og-default.png
```

Per-page frontmatter:
```yaml
---
title: Page Title
description: Page description
image: /path/to/image.png
author: Author Name
keywords: [keyword1, keyword2]
canonical_url: https://example.com/page
noindex: false
---
```

### Social

#### Share Buttons
```liquid
{% include common/social/share-buttons.html %}
```

Configuration:
```yaml
social_share:
  enabled: true
  platforms:
    - twitter
    - facebook
    - linkedin
    - whatsapp
    - email
    - copy
```

Disable on specific pages:
```yaml
---
share: false
---
```

## Directory Structure

```
common-includes/
├── README.md
├── i18n/
│   ├── language-switcher.html
│   └── t.html
├── analytics/
│   └── google-analytics.html
├── gdpr/
│   └── cookie-consent.html
├── seo/
│   └── meta-tags.html
└── social/
    └── share-buttons.html
```

## Creating New Shared Components

When creating new components for the common includes:

1. **Self-contained**: Include all CSS/JS within the file
2. **Configurable**: Use `site.` variables for configuration
3. **Fallbacks**: Provide sensible defaults
4. **Documentation**: Add usage instructions as Liquid comments
5. **No external dependencies**: Minimize reliance on external libraries

### Example Template Structure

```liquid
{% comment %}
  Component Name

  Usage:
    {% include common/category/component.html param="value" %}

  Configuration in _config.yml:
    component_setting: value
{% endcomment %}

{% assign config = site.component_config | default: site.data.component %}
{% assign setting = config.setting | default: "default_value" %}

<!-- HTML content here -->

<style>
/* Scoped CSS */
</style>

<script>
// JavaScript
</script>
```

## Updating Submodule

To update the common includes in your sites:

```bash
git submodule update --remote _includes/common
git add _includes/common
git commit -m "Update common includes"
```

## Contributing

To add new shared components:

1. Create the component in the appropriate category folder
2. Add documentation to this README
3. Test across multiple Jekyll sites
4. Submit a pull request

## License

MIT License - See the main repository for details.
