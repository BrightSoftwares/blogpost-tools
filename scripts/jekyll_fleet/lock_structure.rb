# Prints the structure of a Gemfile.lock read from STDIN as JSON, using Bundler's own (pure) parser, so the
# fleet aligner compares locks the way Bundler reads them instead of the way Python splits text.
# Reads only STDIN, runs no Gemfile or plugin code, touches no network. Called by fleet_align_gems.py.
require "bundler"
require "json"

lock = Bundler::LockfileParser.new($stdin.read)
sources = lock.sources.to_a
idx = ->(src) { sources.index { |s| s.equal?(src) } }

out = {
  "sources" => sources.map do |s|
    if s.class.name.end_with?("Rubygems")
      { "class" => s.class.name, "remotes" => s.remotes.map(&:to_s) }
    else
      { "class" => s.class.name, "options" => s.options.map { |k, v| [k.to_s, v.to_s] }.sort.to_h }
    end
  end,
  "specs" => lock.specs.map do |sp|
    { "name" => sp.name, "version" => sp.version.to_s, "platform" => sp.platform.to_s, "source" => idx.call(sp.source),
      "deps" => sp.dependencies.map(&:to_s).sort }
  end,
  "dependencies" => lock.dependencies.values.map do |d|
    { "name" => d.name, "req" => d.requirement.to_s, "platforms" => d.platforms.map(&:to_s).sort,
      "source" => d.source ? idx.call(d.source) : nil }
  end,
  "platforms" => lock.platforms.map(&:to_s),
  "bundler_version" => lock.bundler_version.to_s,
  "ruby_version" => lock.ruby_version.to_s
}
puts JSON.generate(out)
