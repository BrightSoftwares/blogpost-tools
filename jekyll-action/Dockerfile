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

COPY LICENSE README.md /

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
