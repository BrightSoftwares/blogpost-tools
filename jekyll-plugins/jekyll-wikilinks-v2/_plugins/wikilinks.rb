# frozen_string_literal: true

# Jekyll WikiLinks Plugin v2.0
# Compatible with Jekyll 4.3.4+
#
# Converts WikiLinks syntax [[Page Name]] to proper Jekyll links
#
# Usage:
#   [[Page Name]] -> links to page with that title
#   [[Page Name|Display Text]] -> links to page with custom display text
#   [[/path/to/page]] -> links to specific path
#

module Jekyll
  module WikiLinks
    # Converter for WikiLinks syntax in Markdown files
    class Converter < Jekyll::Converter
      safe true
      priority :low

      def matches(ext)
        ext =~ /^\.md$/i
      end

      def output_ext(ext)
        ".html"
      end

      def convert(content)
        return content unless content.include?('[[')

        # Process WikiLinks
        content.gsub(/\[\[([^\]]+)\]\]/) do |match|
          link_text = ::Regexp.last_match(1)
          process_wikilink(link_text)
        end
      end

      private

      def process_wikilink(link_text)
        # Handle alias syntax: [[Page Name|Display Text]]
        if link_text.include?('|')
          page_name, display_text = link_text.split('|', 2).map(&:strip)
        else
          page_name = link_text.strip
          display_text = page_name
        end

        # Handle direct path links: [[/path/to/page]]
        if page_name.start_with?('/')
          url = page_name
        else
          # Find matching page or post
          url = find_page_url(page_name)
        end

        if url
          "[#{display_text}](#{url})"
        else
          # If page not found, return original text with warning class
          "<span class=\"wikilink-broken\" title=\"Page not found: #{page_name}\">#{display_text}</span>"
        end
      end

      def find_page_url(page_name)
        site = @config['site']
        return nil unless site

        # Normalize page name for matching
        normalized_name = normalize_name(page_name)

        # Search in pages
        page = find_in_collection(site.pages, normalized_name)
        return page.url if page

        # Search in posts
        post = find_in_collection(site.posts.docs, normalized_name)
        return post.url if post

        # Search in all collections
        site.collections.each do |name, collection|
          next if name == 'posts' # Already searched

          doc = find_in_collection(collection.docs, normalized_name)
          return doc.url if doc
        end

        nil
      end

      def find_in_collection(collection, normalized_name)
        collection.find do |item|
          item_title = item.data['title']
          next unless item_title

          normalize_name(item_title) == normalized_name
        end
      end

      def normalize_name(name)
        name.downcase.strip.gsub(/\s+/, ' ')
      end
    end

    # Generator to inject site reference into converter config
    class Generator < Jekyll::Generator
      safe true
      priority :highest

      def generate(site)
        # Make site available to converter
        site.config['site'] = site
      end
    end

    # Liquid filter for WikiLinks in templates
    module Filters
      def wikilink(input, display_text = nil)
        return '' unless input

        page_name = input.to_s.strip
        display = display_text || page_name

        site = @context.registers[:site]
        url = find_page_url_filter(site, page_name)

        if url
          "<a href=\"#{url}\">#{display}</a>"
        else
          "<span class=\"wikilink-broken\" title=\"Page not found: #{page_name}\">#{display}</span>"
        end
      end

      private

      def find_page_url_filter(site, page_name)
        return nil unless site

        normalized_name = normalize_name_filter(page_name)

        # Search in pages
        page = site.pages.find do |p|
          title = p.data['title']
          title && normalize_name_filter(title) == normalized_name
        end
        return page.url if page

        # Search in posts
        post = site.posts.docs.find do |p|
          title = p.data['title']
          title && normalize_name_filter(title) == normalized_name
        end
        return post.url if post

        nil
      end

      def normalize_name_filter(name)
        name.downcase.strip.gsub(/\s+/, ' ')
      end
    end
  end
end

Liquid::Template.register_filter(Jekyll::WikiLinks::Filters)
