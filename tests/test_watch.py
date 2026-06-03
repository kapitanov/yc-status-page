import tempfile
import time
import unittest
from pathlib import Path

from scripts.watch import detect_changes, take_snapshot


class WatchTests(unittest.TestCase):
    def test_detect_changes_for_create_modify_and_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tracked = root / "tracked"
            tracked.mkdir()

            before = take_snapshot([tracked])

            file_path = tracked / "sample.txt"
            file_path.write_text("first")
            created = take_snapshot([tracked])
            self.assertTrue(detect_changes(before, created))

            time.sleep(0.02)
            file_path.write_text("second")
            modified = take_snapshot([tracked])
            self.assertTrue(detect_changes(created, modified))

            file_path.unlink()
            deleted = take_snapshot([tracked])
            self.assertTrue(detect_changes(modified, deleted))
            self.assertFalse(detect_changes(deleted, deleted))


if __name__ == "__main__":
    unittest.main()
