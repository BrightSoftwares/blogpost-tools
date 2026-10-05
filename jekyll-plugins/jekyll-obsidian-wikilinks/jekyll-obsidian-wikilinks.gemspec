# frozen_string_literal: true

require_relative 'lib/jekyll-obsidian-wikilinks/version'

Gem::Specification.new do |spec|
  spec.name          = 'jekyll-obsidian-wikilinks'
  spec.version       = Jekyll::WikiLinks::VERSION
  spec.authors       = ['Bright Softwares']
  spec.summary       = 'Obsidian-style [[wikilinks]] for Jekyll (skips code blocks)'
  spec.description   = 'Converts [[Page]], [[Page|alias]], [[Page#anchor]] and [[/path]] to links at ' \
                       'pre_render time; fenced code and inline code spans are left untouched. ' \
                       'Shared by all Bright Softwares / Afanou Jekyll sites.'
  spec.homepage      = 'https://github.com/BrightSoftwares/blogpost-tools/tree/main/jekyll-plugins/jekyll-obsidian-wikilinks'
  spec.license       = 'MIT'
  spec.required_ruby_version = '>= 3.0'

  spec.files         = Dir['lib/**/*.rb', 'README.md']
  spec.require_paths = ['lib']

  spec.add_dependency 'jekyll', '>= 4.0', '< 5.0'
  spec.add_development_dependency 'minitest', '~> 5.20'
end
