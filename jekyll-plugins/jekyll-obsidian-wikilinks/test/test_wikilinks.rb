# frozen_string_literal: true

# Run: bundle exec ruby -Ilib -Itest test/test_wikilinks.rb
require 'minitest/autorun'
require 'jekyll'
require_relative '../lib/jekyll-obsidian-wikilinks'

class WikiLinksTest < Minitest::Test
  Doc = Struct.new(:data, :url, :basename_without_ext, :relative_path)

  class FakeSite
    def pages = [Doc.new({ 'title' => 'About Me' }, '/about/', 'about', 'about.md')]
    def posts = Struct.new(:docs).new([])
    def collections = {}
  end

  def render(text)
    Jekyll::WikiLinks.process_wikilinks(text, FakeSite.new)
  end

  def test_converts_prose_wikilink
    assert_equal 'See [About Me](/about/) now', render('See [[About Me]] now')
  end

  def test_alias_and_anchor
    assert_equal '[me](/about/#team)', render('[[About Me#team|me]]')
  end

  def test_broken_link_gets_span
    assert_includes render('[[Nope]]'), 'wikilink-broken'
  end

  def test_skips_backtick_fenced_block
    src = "before\n```bash\nif [[ \" $* \" == *x* ]]; then :; fi\n```\nafter [[About Me]]\n"
    out = render(src)
    assert_includes out, 'if [[ " $* " == *x* ]]; then :; fi'
    refute_includes out, 'wikilink-broken'
    assert_includes out, 'after [About Me](/about/)'
  end

  def test_skips_tilde_fence_and_longer_fence
    src = "~~~\n[[About Me]]\n~~~\n````\n```\n[[About Me]]\n```\n````\n[[About Me]]\n"
    out = render(src)
    assert_equal 2, out.scan('[[About Me]]').length
    assert_equal 1, out.scan('[About Me](/about/)').length
  end

  def test_unclosed_fence_runs_to_end
    out = render("```\n[[About Me]]\n")
    assert_includes out, '[[About Me]]'
  end

  def test_skips_inline_code
    out = render('Use `[[ -n "$x" ]]` and [[About Me]]')
    assert_includes out, '`[[ -n "$x" ]]`'
    assert_includes out, '[About Me](/about/)'
  end

  def test_double_backtick_inline_code
    out = render('``a ` [[About Me]]`` then [[About Me]]')
    assert_includes out, '``a ` [[About Me]]``'
    assert_includes out, 'then [About Me](/about/)'
  end

  def test_unmatched_backtick_does_not_swallow_prose
    assert_includes render('a ` b [[About Me]]'), '[About Me](/about/)'
  end

  def test_no_wikilinks_returns_unchanged
    assert_equal 'plain `code`', render('plain `code`')
  end

  def test_stray_backtick_does_not_span_paragraphs
    out = render("a ` b\n\n[[About Me]]\n\nc ` d")
    assert_includes out, '[About Me](/about/)'
  end
end
