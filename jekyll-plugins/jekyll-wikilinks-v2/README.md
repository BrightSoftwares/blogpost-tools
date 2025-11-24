# Jekyll WikiLinks v2

A modern, Jekyll 4.3.4+ compatible WikiLinks plugin that converts Wikipedia-style `[[links]]` to proper Jekyll links.

## Features

✅ **Jekyll 4.3.4+ compatible** - Works with modern Jekyll and Ruby 3.4+
✅ **Simple syntax** - Use familiar `[[Page Name]]` syntax
✅ **Alias support** - Create custom link text with `[[Page Name|Display Text]]`
✅ **Direct paths** - Link directly with `[[/path/to/page]]`
✅ **Broken link detection** - Highlights missing pages with CSS class
✅ **Multi-collection** - Searches across pages, posts, and custom collections
✅ **Liquid filter** - Use in templates with `{{ "Page Name" | wikilink }}`

## Installation

### Method 1: Plugin Directory (Recommended)

1. Copy `_plugins/wikilinks.rb` to your Jekyll site's `_plugins/` directory:

```bash
mkdir -p _plugins
cp wikilinks.rb _plugins/
```

2. That's it! Jekyll will automatically load the plugin.

### Method 2: Gem Installation (Future)

Add to your `Gemfile`:

```ruby
gem 'jekyll-wikilinks-v2'
```

Add to `_config.yml`:

```yaml
plugins:
  - jekyll-wikilinks-v2
```

## Usage

### Basic WikiLinks

```markdown
# In your Markdown files

Check out my [[About]] page!

Read my post about [[Getting Started with Jekyll]].

Visit the [[/contact]] page.
```

### With Custom Display Text

```markdown
Learn more about [[Ruby Programming|Ruby]] here.

See the [[installation-guide|installation instructions]].
```

### In Liquid Templates

```liquid
<!-- Link to a page by title -->
{{ "About Us" | wikilink }}

<!-- With custom display text -->
{{ "Contact" | wikilink: "Get in touch" }}
```

## How It Works

### 1. Page Resolution

The plugin searches for pages/posts by title in this order:
1. Pages (`pages/`)
2. Posts (`_posts/`)
3. Custom collections

### 2. Name Matching

Page names are normalized for matching:
- Case-insensitive
- Whitespace normalized
- Leading/trailing spaces trimmed

**Examples:**
- `[[about]]` matches a page with title "About"
- `[[Getting  Started]]` matches "Getting Started"
- `[[my-post]]` matches "My Post"

### 3. Broken Links

If a page isn't found, the plugin wraps the text in a `<span>` with class `wikilink-broken`:

```html
<span class="wikilink-broken" title="Page not found: Missing Page">Missing Page</span>
```

Add CSS to highlight broken links:

```css
.wikilink-broken {
  color: #d32f2f;
  text-decoration: line-through;
  cursor: help;
}
```

## Configuration

No configuration needed! The plugin works out of the box.

### Optional: Customize Broken Link Styling

Add to your CSS:

```css
/* Broken WikiLinks */
.wikilink-broken {
  color: red;
  background: #ffebee;
  padding: 2px 4px;
  border-radius: 2px;
}

.wikilink-broken::before {
  content: "⚠ ";
}
```

## Examples

### Example 1: Internal Navigation

**Input:**
```markdown
---
title: Home
---

Welcome! Check out:
- [[About|About Us]]
- [[Blog]]
- [[Contact Us]]
```

**Output:**
```html
<p>Welcome! Check out:</p>
<ul>
  <li><a href="/about">About Us</a></li>
  <li><a href="/blog">Blog</a></li>
  <li><a href="/contact">Contact Us</a></li>
</ul>
```

### Example 2: Cross-referencing Posts

**Input:**
```markdown
---
title: Advanced Jekyll Tips
date: 2025-11-24
---

This builds on my previous post: [[Getting Started with Jekyll]].

Also see: [[Jekyll Plugins|my guide to plugins]].
```

**Output:**
```html
<p>This builds on my previous post: <a href="/2025/01/15/getting-started-with-jekyll">Getting Started with Jekyll</a>.</p>

<p>Also see: <a href="/guides/jekyll-plugins">my guide to plugins</a>.</p>
```

### Example 3: Broken Links

**Input:**
```markdown
Check out [[This Page Doesn't Exist]].
```

**Output:**
```html
<p>Check out <span class="wikilink-broken" title="Page not found: This Page Doesn't Exist">This Page Doesn't Exist</span>.</p>
```

## Comparison with Original jekyll-wikilinks

| Feature | Original | WikiLinks v2 |
|---------|----------|--------------|
| Jekyll 4.3.4+ | ❌ | ✅ |
| Ruby 3.4+ | ❌ | ✅ |
| Basic WikiLinks | ✅ | ✅ |
| Alias support | ✅ | ✅ |
| Direct paths | ❌ | ✅ |
| Broken link detection | ⚠️ Limited | ✅ Full |
| Liquid filters | ❌ | ✅ |
| Multi-collection | ⚠️ Limited | ✅ Full |

## Troubleshooting

### Links Not Working

**Problem:** WikiLinks aren't being converted
**Solution:**
1. Ensure `wikilinks.rb` is in `_plugins/` directory
2. Rebuild your site: `bundle exec jekyll clean && bundle exec jekyll build`
3. Check that your files have `.md` extension

### Page Not Found

**Problem:** Link shows as broken but page exists
**Solution:**
1. Check the page has a `title` in front matter
2. Verify title matches exactly (case-insensitive)
3. Ensure page is not in `_drafts/` or excluded in `_config.yml`

### Syntax Highlighting Issues

**Problem:** WikiLinks interfere with code blocks
**Solution:** WikiLinks inside fenced code blocks (```) are automatically preserved

## Performance

The plugin is optimized for performance:
- **Lazy matching:** Only processes files with `[[` syntax
- **Normalized search:** Single pass through collections
- **Cached references:** Site object reused across conversions

Typical impact: <100ms additional build time for sites with <1000 pages.

## Development

### Running Tests

```bash
bundle exec rspec
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Changelog

### v2.0.0 (2025-11-24)
- Complete rewrite for Jekyll 4.3.4+ compatibility
- Ruby 3.4+ support
- Added Liquid filter support
- Improved broken link detection
- Multi-collection search
- Direct path linking

### v1.x (deprecated)
- Original jekyll-wikilinks (incompatible with Jekyll 4.3.4+)

## Credits

Inspired by the original `jekyll-wikilinks` plugin.
Rewritten for modern Jekyll compatibility.

## Support

For issues, questions, or contributions:
- GitHub Issues: [BrightSoftwares/blogpost-tools](https://github.com/BrightSoftwares/blogpost-tools)
- Documentation: This README
