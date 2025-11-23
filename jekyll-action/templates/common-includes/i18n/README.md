# i18n (Internationalization) Components

Complete multi-language support for Jekyll sites.

## Components

### 1. Language Switcher (`language-switcher.html`)

A dropdown component for switching between languages.

```liquid
{% include common/i18n/language-switcher.html %}
```

### 2. Translation Helper (`t.html`)

Retrieve translations using dot-notation keys.

```liquid
{% include common/i18n/t.html key="navigation.home" %}
{% include common/i18n/t.html key="ui.submit" default="Submit" %}
```

### 3. Localized URL (`localized-url.html`)

Generate URLs with proper language prefixes.

```liquid
{% include common/i18n/localized-url.html url="/about" lang="fr" %}
```

### 4. Localized Date (`localized-date.html`)

Format dates according to locale.

```liquid
{% include common/i18n/localized-date.html date=page.date format="long" %}
```

Formats: `short`, `medium`, `long`, `full`, `iso`, `relative`

## Setup

### 1. Configure `_config.yml`

```yaml
# Language settings
languages: ["en", "fr", "de", "es"]
default_lang: "en"
hide_default_lang: true  # Optional: hide /en/ prefix for default language

# i18n method
# folder: URLs like /fr/about
# param: URLs like /about?lang=fr
i18n_method: "folder"
```

### 2. Create Translation Files

Copy sample files from `sample-data/` to `_data/i18n/`:

```
_data/
└── i18n/
    ├── en.yml
    ├── fr.yml
    ├── de.yml
    └── es.yml
```

### 3. Create Language-Specific Content

#### Option A: Folder-based (Recommended for SEO)

```
/
├── en/
│   ├── index.html
│   └── about.html
├── fr/
│   ├── index.html
│   └── about.html
```

Set `lang` in frontmatter:
```yaml
---
layout: default
title: About Us
lang: en
---
```

#### Option B: Single file with translations

Use the translation helper for all text:
```liquid
<h1>{% include common/i18n/t.html key="pages.about.title" %}</h1>
<p>{% include common/i18n/t.html key="pages.about.description" %}</p>
```

### 4. Add Language Switcher to Layout

```liquid
<header>
  <nav>
    <!-- Navigation items -->
  </nav>
  {% include common/i18n/language-switcher.html %}
</header>
```

## Translation File Structure

```yaml
# _data/i18n/en.yml

# Nested structure for organization
navigation:
  home: Home
  about: About

# UI elements
ui:
  read_more: Read more
  submit: Submit

# Page-specific translations
pages:
  about:
    title: About Us
    description: Learn more about our company

# Dates (for localized-date component)
dates:
  months:
    - January
    - February
    # ... etc
```

## Usage Examples

### Navigation with translations

```liquid
<nav>
  <a href="{% include common/i18n/localized-url.html url='/' %}">
    {% include common/i18n/t.html key="navigation.home" %}
  </a>
  <a href="{% include common/i18n/localized-url.html url='/about' %}">
    {% include common/i18n/t.html key="navigation.about" %}
  </a>
</nav>
```

### Blog post date

```liquid
<article>
  <time datetime="{{ page.date | date_to_xmlschema }}">
    {% include common/i18n/localized-date.html date=page.date format="long" %}
  </time>
</article>
```

### E-commerce button

```liquid
<button onclick="addToCart(...)">
  {% include common/i18n/t.html key="shop.add_to_cart" %}
</button>
```

## Sample Data Files

The `sample-data/` directory contains complete translation files:

- `en.yml` - English (reference)
- `fr.yml` - French

These include translations for:
- Navigation
- UI elements
- Forms
- Blog
- E-commerce
- Date formatting
- Error pages

## SEO Considerations

1. **Hreflang tags**: Use `seo/meta-tags.html` which automatically adds hreflang links
2. **Canonical URLs**: Set per-language canonical URLs in frontmatter
3. **URL structure**: Folder-based is better for SEO than query parameters
4. **Sitemap**: Include all language versions in sitemap
