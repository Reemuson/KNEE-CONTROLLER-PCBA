# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path


class KiBotRevisionHistoryTests(unittest.TestCase):
    def test_preflight_defines_revision_history_ceiling(self) -> None:
        text = Path("boardwright_resources/kibot/yaml/kibot_pre_set_text_variables.yaml").read_text(
            encoding="utf-8"
        )

        self.assertIn("REVTABLE_1_REV", text)
        self.assertIn("REVTABLE_1_DATE", text)
        self.assertIn("REVTABLE_1_DESC", text)
        self.assertNotIn("REVTABLE_6_CHECKED", text)
        self.assertIn("REVTABLE_NOTE", text)
        self.assertNotIn("REVHIST_", text)
        self.assertNotIn("RELEASE_BODY_VAR", text)

    def test_revision_sheet_uses_title_body_slots(self) -> None:
        text = Path("revision-history.kicad_sch").read_text(encoding="utf-8")

        self.assertIn("${REVTABLE_1_REV}", text)
        self.assertIn("${REVTABLE_4_DESC}", text)
        self.assertNotIn("${REVHIST_", text)
        self.assertNotIn("RELEASE_BODY_", text)


if __name__ == "__main__":
    unittest.main()
