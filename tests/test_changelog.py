# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest

from boardwright.changelog import (
    _insert_unreleased_entry,
    parse_releases,
    promote_unreleased,
    unreleased_has_content,
)
from boardwright.errors import BoardwrightError


class ChangelogTests(unittest.TestCase):
    def test_parse_unreleased(self) -> None:
        text = "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- First item\n"

        releases = parse_releases(text)

        self.assertEqual("Unreleased", releases[0].name)
        self.assertTrue(unreleased_has_content(text))

    def test_add_unreleased_entry_to_existing_section(self) -> None:
        text = "# Changelog\n\n## [Unreleased]\n\n### Changed\n\n- Existing\n"

        updated = _insert_unreleased_entry(text, "Changed", "New item")

        self.assertIn("- Existing\n- New item", updated)

    def test_add_unreleased_entry_keeps_blank_before_next_section(self) -> None:
        text = (
            "# Changelog\n\n"
            "## [Unreleased]\n\n"
            "### Added\n\n"
            "- Existing\n\n"
            "### Changed\n\n"
            "- Other\n"
        )

        updated = _insert_unreleased_entry(text, "Added", "New item")

        self.assertIn("- Existing\n- New item\n\n### Changed", updated)

    def test_add_unreleased_entry_formats_multiline_as_bullets(self) -> None:
        text = "# Changelog\n\n## [Unreleased]\n\n### Changed\n\n- Existing\n"

        updated = _insert_unreleased_entry(text, "Changed", "First\nSecond")

        self.assertIn("- Existing\n- First\n- Second", updated)

    def test_add_unreleased_entry_preserves_wrapped_explicit_bullets(self) -> None:
        text = "# Changelog\n\n## [Unreleased]\n\n### Changed\n\n"

        updated = _insert_unreleased_entry(text, "Changed", "- First\n  wrapped\n* Second")

        self.assertIn("- First\n  wrapped\n- Second", updated)

    def test_promote_unreleased(self) -> None:
        text = "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Thing\n"

        updated = promote_unreleased(text, "0.1.0")

        self.assertIn("## [Unreleased]\n\n## [0.1.0] - ", updated)

    def test_promote_unreleased_can_create_no_change_release_note(self) -> None:
        text = "# Changelog\n\n## [Unreleased]\n"

        updated = promote_unreleased(text, "0.1.0", allow_empty=True)

        self.assertIn("## [0.1.0] - ", updated)
        self.assertIn("- No changelog entries recorded for this release.", updated)

    def test_promote_unreleased_keeps_empty_changelog_strict_by_default(self) -> None:
        text = "# Changelog\n\n## [Unreleased]\n"

        with self.assertRaises(BoardwrightError):
            promote_unreleased(text, "0.1.0")


if __name__ == "__main__":
    unittest.main()
