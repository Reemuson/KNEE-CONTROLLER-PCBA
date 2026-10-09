# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path

from boardwright.config import BoardwrightConfig
from boardwright.legal import render_notice


class LegalTests(unittest.TestCase):
    def test_notice_contains_downstream_license_and_safety(self) -> None:
        config = BoardwrightConfig(
            root=Path("."),
            project={"project": {"name": "Test Board"}},
            branches={"branches": {}},
            legal={
                "boardwright": {"default_profile": "public-hardware"},
                "downstream_project_defaults": {
                    "profile": "compatibility-friendly",
                    "hardware_design_license": "CERN-OHL-W-2.0",
                    "branding_reserved": True,
                    "compatibility": {"enabled": False},
                    "safety_notice": "Verify safety before use.",
                    "third_party_notice_file": "THIRD_PARTY_NOTICES.md",
                }
            },
            revision_history={"revision_history": {}},
        )

        notice = render_notice(config)

        self.assertIn("CERN-OHL-W-2.0", notice)
        self.assertIn("compatibility-friendly", notice)
        self.assertIn("downstream hardware-project license", notice)
        self.assertIn("does not\ndefine the license of the Boardwright", notice)
        self.assertIn("Verify safety before use.", notice)
        self.assertIn("not legal advice", notice)

    def test_notice_supports_legacy_legal_shape(self) -> None:
        config = BoardwrightConfig(
            root=Path("."),
            project={"project": {"name": "Legacy Board"}},
            branches={"branches": {}},
            legal={
                "legal": {
                    "hardware_license": "CERN-OHL-W-2.0",
                    "branding_reserved": False,
                    "compatibility": {"enabled": False},
                    "safety_notice": "Legacy safety.",
                }
            },
            revision_history={"revision_history": {}},
        )

        notice = render_notice(config)

        self.assertIn("CERN-OHL-W-2.0", notice)
        self.assertIn("Legacy safety.", notice)


if __name__ == "__main__":
    unittest.main()
