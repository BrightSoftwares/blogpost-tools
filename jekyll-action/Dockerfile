FROM ruby:3.4.1-alpine

LABEL version="2.0.2"
LABEL repository="https://github.com/brightsoftwares/blogpost-tools"
LABEL homepage="https://github.com/brightsoftwares/blogpost-tools"
LABEL maintainer="BrightSoftwares"

# Install base build dependencies
RUN apk add --no-cache git build-base

# Allow for timezone setting in _config.yml
RUN apk add --update tzdata

# Use curl to send API requests
RUN apk add --update curl

# Install ruby-dev for native gem extensions
RUN apk add --no-cache ruby-dev

# Install ImageMagick with full format support (needed for jekyll-responsive-image, jekyll-minimagick)
RUN apk add --no-cache imagemagick imagemagick-dev imagemagick-libs \
    libjpeg-turbo libjpeg-turbo-dev libpng-dev libwebp-dev

# Install libxml2 and libxslt for nokogiri (common Jekyll dependency)
RUN apk add --no-cache libxml2-dev libxslt-dev

# Install libffi for ffi gem
RUN apk add --no-cache libffi-dev

# Debug: show bundler version
RUN bundle version

# Pre-install common gems to speed up builds
# Ruby 3.4+ stdlib gems (no longer bundled)
RUN gem install csv logger base64 bigdecimal observer ostruct mutex_m --no-document

# Jekyll core and common plugins
RUN gem install jekyll -v 4.2.2 --no-document && \
    gem install bundler --no-document && \
    gem install webrick --no-document && \
    gem install rexml --no-document

# Common Jekyll plugins
RUN gem install jekyll-feed jekyll-sitemap jekyll-seo-tag jekyll-paginate-v2 \
    jekyll-archives jekyll-redirect-from jekyll-timeago --no-document

# jekyll-last-modified-at 1.3.2 (without posix-spawn dependency issues)
RUN gem install jekyll-last-modified-at -v 1.3.2 --no-document

# Additional common gems
RUN gem install minima kramdown kramdown-parser-gfm rouge --no-document

# Image processing plugins
RUN gem install jekyll-responsive-image jekyll-minimagick mini_magick --no-document || true

# Algolia search (optional, may fail if not needed)
RUN gem install jekyll-algolia algoliasearch --no-document || true

COPY LICENSE README.md /

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
