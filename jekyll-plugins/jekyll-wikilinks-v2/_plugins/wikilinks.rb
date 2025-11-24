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
    class << self
      def process_wikilinks(content, site)
        return content unless content.include?('[[')

        content.gsub(/\[\[([^\]]+)\]\]/) do |match|
          link_text = ::Regexp.last_match(1)
          process_wikilink(link_text, site)
        end
      end

      private

      def process_wikilink(link_text, site)
        # Handle alias syntax: [[Page Name|Display Text]]
        if link_text.include?('|')
          page_name, display_text = link_text.split('|', 2).map(&:strip)
        else
          page_name = link_text.strip
          display_text = page_name
        end

        # Handle anchor links: [[Page Name#anchor|Display Text]]
        anchor = nil
        if page_name.include?('#')
          page_name, anchor = page_name.split('#', 2)
          page_name = page_name.strip
          anchor = anchor.strip
        end

        # Handle direct path links: [[/path/to/page]]
        if page_name.start_with?('/')
          url = page_name
        else
          # Find matching page or post
          url = find_page_url(page_name, site)
        end

        # Append anchor if present
        url = "#{url}##{anchor}" if url && anchor

        if url
          "[#{display_text}](#{url})"
        else
          # If page not found, return original text with warning class
          "<span class=\"wikilink-broken\" title=\"Page not found: #{page_name}\">#{display_text}</span>"
        end
      end

      def find_page_url(page_name, site)
        return nil unless site

        # Normalize page name for matching
        normalized_name = normalize_name(page_name)

        # Search in pages (by title and slug)
        page = find_in_collection(site.pages, normalized_name)
        return page.url if page

        # Search in posts (by title and slug)
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
          # Match by title
          item_title = item.data['title']
          return item if item_title && normalize_name(item_title) == normalized_name

          # Match by slug (filename without extension)
          if item.respond_to?(:basename_without_ext)
            slug = item.basename_without_ext
            return item if normalize_name(slug) == normalized_name
          end

          # Match by relative path (for posts like "2022-09-14-post-name")
          if item.respond_to?(:relative_path)
            path_slug = File.basename(item.relative_path, '.*')
            return item if normalize_name(path_slug) == normalized_name
          end

          false
        end
      end

      def normalize_name(name)
        name.downcase.strip.gsub(/\s+/, ' ')
      end
    end

    # Liquid filter for WikiLinks in templates
    module Filters
      def wikilink(input, display_text = nil)
        return '' unless input

        page_name = input.to_s.strip
        display = display_text || page_name

        site = @context.registers[:site]
        url = WikiLinks.send(:find_page_url, page_name, site)

        if url
          "<a href=\"#{url}\">#{display}</a>"
        else
          "<span class=\"wikilink-broken\" title=\"Page not found: #{page_name}\">#{display}</span>"
        end
      end
    end
  end
end

# Register hooks to process WikiLinks before markdown conversion
Jekyll::Hooks.register [:pages, :posts, :documents], :pre_render do |doc|
  doc.content = Jekyll::WikiLinks.process_wikilinks(doc.content, doc.site)
end

Liquid::Template.register_filter(Jekyll::WikiLinks::Filters)
