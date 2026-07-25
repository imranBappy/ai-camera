from datetime import datetime
from pathlib import Path

import cv2
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)


def save_frame_to_file(frame, output_path):
    if frame is None:
        return False

    try:
        return bool(cv2.imwrite(output_path, frame))
    except Exception:
        return False


def frame_to_pixmap(frame, size):
    if frame is None:
        return QPixmap()

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape

    image = QImage(
        rgb.data,
        w,
        h,
        ch * w,
        QImage.Format.Format_RGB888,
    )

    pixmap = QPixmap.fromImage(image.copy())
    return pixmap.scaled(
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


class ClickableLabel(QLabel):
    def __init__(self, *args, on_click=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if self._on_click is not None and event.button() == Qt.MouseButton.LeftButton:
            self._on_click()
        super().mousePressEvent(event)


class CapturePreviewDialog(QDialog):
    def __init__(self, pixmap, filename, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Captured Photo — {filename}")
        self.resize(720, 540)

        layout = QVBoxLayout(self)

        preview = QLabel()
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setMinimumSize(640, 480)
        preview.setStyleSheet("background-color: black;")
        preview.setPixmap(
            pixmap.scaled(
                preview.minimumSize(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        layout.addWidget(preview)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.camera = None
        self.last_capture_path = None
        self.last_capture_pixmap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.capture_display_timer = QTimer(self)
        self.capture_display_timer.setSingleShot(True)
        self.capture_display_timer.timeout.connect(self.resume_preview)

        self.setWindowTitle("AI Hand Gesture Camera")
        self.resize(980, 620)

        central_widget = QWidget()
        main_layout = QHBoxLayout()

        self.camera_label = QLabel("Camera Preview")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("""
            border:2px solid gray;
            background-color: black;
            color: white;
        """)

        right_layout = QVBoxLayout()

        self.start_btn = QPushButton("Start Camera")
        self.stop_btn = QPushButton("Stop Camera")
        self.capture_btn = QPushButton("Capture Photo")
        self.preview_btn = QPushButton("Preview Capture")
        self.gesture_label = QLabel("Gesture: None")

        self.last_capture_label = ClickableLabel(
            "No capture yet",
            on_click=self.preview_capture,
        )
        self.last_capture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.last_capture_label.setMinimumSize(200, 150)
        self.last_capture_label.setStyleSheet("""
            border:1px solid gray;
            background-color: #1a1a1a;
            color: #aaaaaa;
        """)

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.capture_btn.clicked.connect(self.capture_photo)
        self.preview_btn.clicked.connect(self.preview_capture)

        self.stop_btn.setEnabled(False)
        self.capture_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)

        right_layout.addWidget(self.start_btn)
        right_layout.addWidget(self.stop_btn)
        right_layout.addWidget(self.capture_btn)
        right_layout.addWidget(self.preview_btn)
        right_layout.addWidget(self.gesture_label)
        right_layout.addWidget(QLabel("Last Capture"))
        right_layout.addWidget(self.last_capture_label)
        right_layout.addStretch()

        main_layout.addWidget(self.camera_label, 3)
        main_layout.addLayout(right_layout, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def start_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            self.gesture_label.setText("Gesture: Camera unavailable")
            return

        self.timer.start(30)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.capture_btn.setEnabled(True)

    def resume_preview(self):
        if self.camera is not None and self.camera.isOpened():
            self.timer.start(30)

    def stop_camera(self):
        self.timer.stop()
        self.capture_display_timer.stop()

        if self.camera is not None and self.camera.isOpened():
            self.camera.release()
            self.camera = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.capture_btn.setEnabled(False)
        self.camera_label.clear()
        self.camera_label.setText("Camera Preview")

    def update_frame(self):
        if self.camera is None or not self.camera.isOpened():
            return

        success, frame = self.camera.read()
        if not success:
            return

        self.show_frame(frame)

    def show_frame(self, frame):
        self.camera_label.setPixmap(frame_to_pixmap(frame, self.camera_label.size()))

    def update_capture_preview(self, frame, output_path):
        pixmap = frame_to_pixmap(frame, self.last_capture_label.size())
        self.last_capture_path = Path(output_path)
        self.last_capture_pixmap = frame_to_pixmap(frame, (1280, 960))
        self.last_capture_label.setPixmap(pixmap)
        self.preview_btn.setEnabled(True)

    def preview_capture(self):
        if self.last_capture_pixmap is None or self.last_capture_path is None:
            self.gesture_label.setText("Gesture: No capture to preview")
            return

        dialog = CapturePreviewDialog(
            self.last_capture_pixmap,
            self.last_capture_path.name,
            parent=self,
        )
        dialog.exec()

    def capture_photo(self):
        if self.camera is None or not self.camera.isOpened():
            self.gesture_label.setText("Gesture: Camera not running")
            return

        success, frame = self.camera.read()
        if not success:
            self.gesture_label.setText("Gesture: Could not read frame")
            return

        output_dir = Path(__file__).resolve().parent.parent / "assets" / "captures"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"capture_{timestamp}.png"

        if save_frame_to_file(frame, str(output_path)):
            self.timer.stop()
            self.show_frame(frame)
            self.update_capture_preview(frame, output_path)
            self.capture_display_timer.start(1500)
            self.gesture_label.setText(f"Gesture: Saved {output_path.name}")
        else:
            self.gesture_label.setText("Gesture: Failed to save photo")

    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)

