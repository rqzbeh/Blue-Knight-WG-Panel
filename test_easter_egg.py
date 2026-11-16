"""Unit tests for the meow easter egg feature and timestamp logic."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import panel
from test_base import PanelTestBase


def verify_timestamp_logic(hours=None, minutes=None):
    """Check if hours == minutes, or return all matching HH:MM timestamps in a 24-hour day."""
    if hours is not None and minutes is not None:
        return hours == minutes
    return [f"{h:02d}:{m:02d}" for h in range(24) for m in range(60) if h == m]


class EasterEggTests(PanelTestBase):
    def test_easter_egg_endpoint_success(self):
        """Test that /api/easter-egg/meow returns 200 and audio/mpeg content type with correct size."""
        asset_file = PROJECT_ROOT / 'assets' / 'meow.mp3'
        self.assertTrue(asset_file.is_file(), "assets/meow.mp3 must exist")
        expected_size = asset_file.stat().st_size
        expected_content = asset_file.read_bytes()

        response = self.request('/api/easter-egg/meow')
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'audio/mpeg')

        data = response.read()
        self.assertEqual(len(data), expected_size)
        self.assertEqual(data, expected_content)

    def test_easter_egg_endpoint_not_found(self):
        """Test that /api/easter-egg/meow returns 404 when the audio file is missing."""
        missing_path = Path(self.temp.name) / 'nonexistent.mp3'
        with patch.object(panel, 'EASTER_EGG_ASSET', missing_path), \
             patch.object(panel, 'EASTER_EGG_FALLBACK', missing_path):
            response = self.request('/api/easter-egg/meow')
            self.assertEqual(response.status, 404)

    def test_easter_egg_fallback_path(self):
        """Test that /api/easter-egg/meow falls back to /home/redsnow/meow/meow.mp3 if asset is missing."""
        missing_asset = Path(self.temp.name) / 'missing_asset.mp3'
        fallback_file = Path('/home/redsnow/meow/meow.mp3')
        if not fallback_file.is_file():
            self.skipTest("Fallback file /home/redsnow/meow/meow.mp3 not found on host")

        with patch.object(panel, 'EASTER_EGG_ASSET', missing_asset), \
             patch.object(panel, 'EASTER_EGG_FALLBACK', fallback_file):
            response = self.request('/api/easter-egg/meow')
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get('Content-Type'), 'audio/mpeg')
            self.assertEqual(len(response.read()), fallback_file.stat().st_size)

    def test_verify_timestamp_logic_matches_exactly_24_times(self):
        """Test helper function verify_timestamp_logic() checking that exactly 24 timestamps in a day satisfy hours == minutes."""
        timestamps = verify_timestamp_logic()
        self.assertEqual(len(timestamps), 24)

        expected_timestamps = [f"{i:02d}:{i:02d}" for i in range(24)]
        self.assertEqual(timestamps, expected_timestamps)

        matching_count = 0
        non_matching_count = 0
        for h in range(24):
            for m in range(60):
                if verify_timestamp_logic(h, m):
                    matching_count += 1
                    self.assertEqual(h, m)
                else:
                    non_matching_count += 1
                    self.assertNotEqual(h, m)

        self.assertEqual(matching_count, 24)
        self.assertEqual(non_matching_count, 24 * 60 - 24)  # 1416 non-matching timestamps


if __name__ == '__main__':
    unittest.main()
