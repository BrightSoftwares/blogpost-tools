"""Unit tests for src/text_utils.py (shared Phase 3 body-parsing helpers)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from text_utils import (  # noqa: E402
    compute_forbidden_regions,
    compute_paragraphs,
    find_paragraph_index,
    find_section_containing,
    is_inside_any_region,
    merge_intervals,
    segment_into_sections,
)


class TestMergeIntervals(unittest.TestCase):
    def test_merges_overlapping(self):
        self.assertEqual(merge_intervals([(0, 5), (3, 8)]), [(0, 8)])

    def test_merges_adjacent(self):
        self.assertEqual(merge_intervals([(0, 5), (5, 8)]), [(0, 8)])

    def test_keeps_disjoint_separate(self):
        self.assertEqual(merge_intervals([(0, 2), (10, 12)]), [(0, 2), (10, 12)])

    def test_empty_input(self):
        self.assertEqual(merge_intervals([]), [])


class TestForbiddenRegions(unittest.TestCase):
    def test_fenced_code_block_is_forbidden(self):
        body = "Some text.\n```\ncode here\n```\nMore text."
        regions = compute_forbidden_regions(body)
        code_start = body.index("```")
        code_end = body.index("```", code_start + 3) + 3
        self.assertTrue(is_inside_any_region(code_start + 1, code_start + 2, regions))
        self.assertFalse(is_inside_any_region(0, 4, regions))
        self.assertTrue(code_end <= len(body))

    def test_inline_code_is_forbidden(self):
        body = "Run `pip install nginx` to install it."
        regions = compute_forbidden_regions(body)
        start = body.index("`pip")
        end = body.index("nginx`") + len("nginx`")
        self.assertTrue(is_inside_any_region(start, end, regions))

    def test_existing_wikilink_is_forbidden(self):
        body = "See [[install-nginx]] for details."
        regions = compute_forbidden_regions(body)
        start = body.index("[[")
        end = body.index("]]") + 2
        self.assertTrue(is_inside_any_region(start, end, regions))

    def test_existing_markdown_link_is_forbidden(self):
        body = "See [nginx docs](https://example.com/nginx) for details."
        regions = compute_forbidden_regions(body)
        start = body.index("[nginx")
        end = body.index(")") + 1
        self.assertTrue(is_inside_any_region(start, end, regions))

    def test_bare_url_in_prose_is_forbidden(self):
        # Real production bug: a keyword match on "localhost" landed inside
        # a bare (non-markdown-wrapped) URL and got wikilink-wrapped mid-URL,
        # corrupting it to http://[[...|localhost]]:3000/.
        body = "Run the app then visit http://localhost:3000/ in your browser."
        regions = compute_forbidden_regions(body)
        start = body.index("localhost")
        end = start + len("localhost")
        self.assertTrue(is_inside_any_region(start, end, regions))

    def test_html_tag_is_forbidden(self):
        body = "Some <span class='x'>text</span> here."
        regions = compute_forbidden_regions(body)
        start = body.index("<span")
        end = start + len("<span class='x'>")
        self.assertTrue(is_inside_any_region(start, end, regions))

    def test_liquid_tag_is_forbidden(self):
        body = "Value: {{ site.title }} end."
        regions = compute_forbidden_regions(body)
        start = body.index("{{")
        end = body.index("}}") + 2
        self.assertTrue(is_inside_any_region(start, end, regions))

    def test_plain_text_not_forbidden(self):
        body = "Just plain prose with no special regions at all."
        regions = compute_forbidden_regions(body)
        self.assertFalse(is_inside_any_region(0, len(body), regions))


class TestParagraphs(unittest.TestCase):
    def test_splits_on_blank_lines(self):
        body = "Para one.\n\nPara two.\n\nPara three."
        paragraphs = compute_paragraphs(body)
        self.assertEqual(len(paragraphs), 3)
        texts = [body[s:e] for s, e in paragraphs]
        self.assertEqual(texts, ["Para one.", "Para two.", "Para three."])

    def test_find_paragraph_index_exact(self):
        body = "Para one.\n\nPara two.\n\nPara three."
        paragraphs = compute_paragraphs(body)
        offset = body.index("Para two")
        self.assertEqual(find_paragraph_index(offset, paragraphs), 1)

    def test_find_paragraph_index_empty_list(self):
        self.assertEqual(find_paragraph_index(5, []), 0)


class TestSectionSegmentation(unittest.TestCase):
    def test_intro_section_before_first_heading(self):
        body = "Intro text.\n\n## First Heading\n\nBody one."
        sections = segment_into_sections(body)
        self.assertEqual(sections[0].heading_level, 0)
        self.assertEqual(sections[0].heading_text, "(intro)")
        self.assertEqual(sections[1].heading_level, 2)
        self.assertEqual(sections[1].heading_text, "First Heading")

    def test_sections_are_contiguous(self):
        body = "Intro.\n\n## A\n\nBody A.\n\n### B\n\nBody B."
        sections = segment_into_sections(body)
        for i in range(len(sections) - 1):
            self.assertEqual(sections[i].end_offset, sections[i + 1].start_offset)
        self.assertEqual(sections[-1].end_offset, len(body))

    def test_find_section_containing(self):
        body = "Intro.\n\n## A\n\nBody A text here."
        sections = segment_into_sections(body)
        offset = body.index("Body A")
        section = find_section_containing(offset, sections)
        self.assertEqual(section.heading_text, "A")

    def test_find_section_containing_out_of_range_returns_none(self):
        body = "Intro.\n\n## A\n\nBody A."
        sections = segment_into_sections(body)
        self.assertIsNone(find_section_containing(len(body) + 100, sections))

    def test_no_headings_single_section(self):
        body = "Just one paragraph, no headings at all."
        sections = segment_into_sections(body)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].heading_level, 0)
        self.assertEqual(sections[0].start_offset, 0)
        self.assertEqual(sections[0].end_offset, len(body))


if __name__ == "__main__":
    unittest.main()
