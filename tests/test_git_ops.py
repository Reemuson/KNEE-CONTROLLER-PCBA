# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path
from unittest.mock import patch

from boardwright.git_ops import latest_tag


class GitOpsTests(unittest.TestCase):
    def test_latest_tag_prefers_latest_stable_semver_release(self) -> None:
        tags = "\n".join(("0.1.0", "0.2.0-rc.1", "not-a-release", "0.1.1"))

        with patch("boardwright.git_ops._git", return_value=tags):
            self.assertEqual("0.1.1", latest_tag(Path(".")))

    def test_latest_tag_uses_prerelease_when_no_stable_release_exists(self) -> None:
        tags = "\n".join(("0.2.0-alpha.1", "0.2.0-rc.1", "notes"))

        with patch("boardwright.git_ops._git", return_value=tags):
            self.assertEqual("0.2.0-rc.1", latest_tag(Path(".")))

    def test_latest_tag_returns_none_when_no_semver_tags_exist(self) -> None:
        with patch("boardwright.git_ops._git", return_value="prototype\nnotes"):
            self.assertIsNone(latest_tag(Path(".")))


if __name__ == "__main__":
    unittest.main()
