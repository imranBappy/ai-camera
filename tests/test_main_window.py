import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np

from ui.main_window import frame_to_pixmap, save_frame_to_file


class SaveFrameToFileTest(unittest.TestCase):
    def test_saves_frame_to_file(self):
        frame = np.zeros((20, 20, 3), dtype=np.uint8)

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "capture.png"
            saved = save_frame_to_file(frame, str(output_path))

            self.assertTrue(saved)
            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)

    def test_converts_frame_to_pixmap(self):
        frame = np.zeros((20, 20, 3), dtype=np.uint8)
        pixmap = frame_to_pixmap(frame, (80, 80))

        self.assertFalse(pixmap.isNull())


if __name__ == "__main__":
    unittest.main()
