import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from estimate_text_layout import estimate_text_layout


class EstimateTextLayoutTests(unittest.TestCase):
    def test_empty_text_and_whitespace_lines(self):
        self.assertEqual(estimate_text_layout("")["total_lines"], 0)
        self.assertEqual(estimate_text_layout("")["total_pages"], 0)
        self.assertEqual(estimate_text_layout("  \n\t")["total_lines"], 2)

    def test_word_wrapping_at_default_average(self):
        for count, lines in [(15, 1), (16, 2), (31, 2), (32, 3)]:
            with self.subTest(words=count):
                result = estimate_text_layout(" ".join(["word"] * count))
                self.assertEqual(result["total_lines"], lines)
                self.assertEqual(result["word_count"], count)

    def test_explicit_breaks_blank_lines_and_wrapping(self):
        text = " ".join(["word"] * 32) + "\r\n\r\nshort\r\n"
        result = estimate_text_layout(text)
        self.assertEqual(result["total_lines"], 5)
        self.assertEqual(result["word_count"], 33)

    def test_terminal_newline_is_not_an_extra_blank_line(self):
        self.assertEqual(estimate_text_layout("text\n")["total_lines"], 1)
        self.assertEqual(estimate_text_layout("text\n\n")["total_lines"], 2)
        self.assertEqual(estimate_text_layout("\n")["total_lines"], 1)

    def test_page_boundaries(self):
        for lines, pages in [(51, 1), (52, 1), (53, 2), (104, 2), (105, 3)]:
            with self.subTest(lines=lines):
                result = estimate_text_layout("\n".join(["line"] * lines))
                self.assertEqual(result["total_lines"], lines)
                self.assertEqual(result["total_pages"], pages)
        self.assertEqual(estimate_text_layout("line")["page_equivalent"], 0.0192)

    def test_custom_limits_and_unicode_words(self):
        result = estimate_text_layout("ação\tIA revisão dados", words_per_line=2, lines_per_page=1)
        self.assertEqual(result["word_count"], 4)
        self.assertEqual(result["total_lines"], 2)
        self.assertEqual(result["total_pages"], 2)

    def test_invalid_limits(self):
        for value in [0, -1, float("nan"), float("inf")]:
            with self.subTest(words_per_line=value), self.assertRaises(ValueError):
                estimate_text_layout("text", words_per_line=value)
        for value in [0, -1, 1.5, True]:
            with self.subTest(lines_per_page=value), self.assertRaises(ValueError):
                estimate_text_layout("text", lines_per_page=value)

    def test_cli_stdin_and_file(self):
        script = str(SCRIPTS / "estimate_text_layout.py")
        result = subprocess.run([sys.executable, script], input="first\n\nlast",
                                text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)["total_lines"], 3)
        result = subprocess.run([sys.executable, script, "--file", str(Path(__file__))],
                                text=True, capture_output=True, check=True)
        self.assertGreater(json.loads(result.stdout)["total_lines"], 0)

    def test_cli_errors_and_empty_argument(self):
        script = str(SCRIPTS / "estimate_text_layout.py")
        result = subprocess.run([sys.executable, script, "--text", ""],
                                text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)["total_lines"], 0)
        result = subprocess.run([sys.executable, script, "--text", "test", "--words-per-line", "0"],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("greater than zero", result.stderr)


if __name__ == "__main__":
    unittest.main()
