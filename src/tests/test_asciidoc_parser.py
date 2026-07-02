"""
Unit tests for AsciiDoc parsing: headings, speaker notes, and image references.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from ..exporter.asciidoc_parser import (
    parse_images_from_adoc,
    extract_images_dir,
    validate_and_resolve_images,
    normalize_adoc_content,
    parse_slides_and_notes,
)
from ..exporter.config import ImageReference

class TestAsciiDocParser(unittest.TestCase):
    def test_parse_images_from_adoc(self):
        sample = """
        = Slide Deck Title
        :title-slide-background-image: images/title.png
        
        == Slide 1
        image::images/pic1.jpg[Some Caption]
        Here is inline image:images/pic2.svg[Inline Image]
        
        == Slide 2
        <img src="images/pic3.webp" alt="HTML Tag">
        And lazy image <div data-src="images/pic4.gif"></div>
        
        == Slide 3
        [%notitle, background-image="images/pic5.jpeg"]
        """
        refs = parse_images_from_adoc(sample)
        paths = [r.ref_path for r in refs]
        
        self.assertEqual(len(refs), 6)
        self.assertIn("images/title.png", paths)
        self.assertIn("images/pic1.jpg", paths)
        self.assertIn("images/pic2.svg", paths)
        self.assertIn("images/pic3.webp", paths)
        self.assertIn("images/pic4.gif", paths)
        self.assertIn("images/pic5.jpeg", paths)

    def test_extract_images_dir(self):
        sample_1 = ":imagesdir: test_images"
        self.assertEqual(extract_images_dir(sample_1), "test_images")
        
        sample_2 = "= Title\nNo imagesdir defined"
        self.assertEqual(extract_images_dir(sample_2), ".")

    def test_normalize_adoc_content(self):
        sample = """
        image::images/pic1.png[]
        image:images/pic2.jpg[]
        <img src="images/pic3.svg">
        <img data-src="images/pic4.webp">
        background-image="images/pic5.gif"
        :title-slide-background-image: images/pic6.jpeg
        """
        res = normalize_adoc_content(sample, "images")
        
        self.assertIn("image::pic1.png[]", res)
        self.assertIn("image:pic2.jpg[]", res)
        self.assertIn('src="pic3.svg"', res)
        self.assertIn('data-src="pic4.webp"', res)
        self.assertIn('background-image="pic5.gif"', res)
        self.assertIn(":title-slide-background-image: pic6.jpeg", res)
        self.assertNotIn("images/", res)

    def test_parse_slides_and_notes(self):
        sample = """
        = Presentation Title
        
        [.notes]
        --
        Intro notes
        --
        
        == Slide One
        Content here
        
        [.notes]
        --
        Notes for slide one
        --
        
        === Slide Two
        
        [.notes]
        Notes for slide two without open block
        
        == Slide Three
        No notes here
        """
        slides = parse_slides_and_notes(sample)
        self.assertEqual(len(slides), 4)
        
        self.assertEqual(slides[0]["title"], "Presentation Title")
        self.assertEqual(slides[0]["notes"], "Intro notes")
        self.assertEqual(slides[0]["level"], 1)
        
        self.assertEqual(slides[1]["title"], "Slide One")
        self.assertEqual(slides[1]["notes"], "Notes for slide one")
        self.assertEqual(slides[1]["level"], 2)
        
        self.assertEqual(slides[2]["title"], "Slide Two")
        self.assertEqual(slides[2]["notes"], "Notes for slide two without open block")
        self.assertEqual(slides[2]["level"], 3)
        
        self.assertEqual(slides[3]["title"], "Slide Three")
        self.assertEqual(slides[3]["notes"], "")
        self.assertEqual(slides[3]["level"], 2)

    @patch("urllib.request.urlopen")
    def test_validate_and_resolve_images_remote_success(self, mock_urlopen):
        mock_response = Mock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        refs = [ImageReference(ref_path="https://example.com/logo.png", line_number=10, context_line="")]
        valid, missing = validate_and_resolve_images(refs, Path("docs/presentation.adoc"), Path("docs/images"))
        
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(missing), 0)
        self.assertTrue(valid[0].is_valid)

if __name__ == "__main__":
    unittest.main()
