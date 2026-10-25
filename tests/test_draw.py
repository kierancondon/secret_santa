import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from generate_draw import (  # noqa: E402
    draw_assignments,
    normalize_name,
    read_js_data,
    validate_draw,
    validate_secrets,
    write_draw,
    write_js_data,
)

SYNTHETIC = ["A", "B", "C", "D", "E", "F"]


class DrawTests(unittest.TestCase):
    def test_valid_draws_without_self_matches(self):
        for _ in range(300):
            validate_draw(SYNTHETIC, draw_assignments(SYNTHETIC))

    def test_two_people(self):
        validate_draw(["X", "Y"], draw_assignments(["X", "Y"]))

    def test_rejects_too_few_or_duplicates(self):
        with self.assertRaises(ValueError):
            draw_assignments(["solo"])
        with self.assertRaises(ValueError):
            draw_assignments(["A", "A", "B"])

    def test_validate_draw_rejects_bad_draws(self):
        with self.assertRaises(ValueError):
            validate_draw(["A", "B"], {"A": "A", "B": "B"})
        with self.assertRaises(ValueError):
            validate_draw(["A", "B", "C"], {"A": "B", "B": "B", "C": "A"})
        with self.assertRaises(ValueError):
            validate_draw(["A", "B"], {"A": "B"})

    def test_duplicate_aliases_after_normalization(self):
        with self.assertRaises(ValueError):
            validate_secrets(
                [
                    {"realName": "A", "secretName": "Holly  Star"},
                    {"realName": "B", "secretName": "holly star"},
                ]
            )

    def test_normalize_name(self):
        self.assertEqual(normalize_name("  Holly   STAR "), "holly star")

    def test_write_draw_refuses_overwrite_without_redraw(self):
        with tempfile.TemporaryDirectory() as tmp:
            secrets_path = Path(tmp) / "secrets.js"
            out_path = Path(tmp) / "assignments.js"
            write_js_data(
                secrets_path,
                "SECRETS",
                [{"realName": n, "secretName": f"alias {n}"} for n in SYNTHETIC],
            )
            write_draw(secrets_path, out_path)
            with self.assertRaises(FileExistsError):
                write_draw(secrets_path, out_path)
            write_draw(secrets_path, out_path, redraw=True)

    def test_persisted_data_is_consistent(self):
        entries = read_js_data(ROOT / "data" / "secrets.js", "SECRETS")
        draw = read_js_data(ROOT / "data" / "assignments.js", "ASSIGNMENTS")
        validate_secrets(entries)
        validate_draw([e["realName"] for e in entries], draw)


if __name__ == "__main__":
    unittest.main()
