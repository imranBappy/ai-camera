# AI Hand Gesture Camera

Desktop camera app built with **PyQt6** and **OpenCV**. Start a live preview, capture photos, and preview the last shot.

## Requirements

- Python 3.9+
- A working webcam (for live preview and capture)
- macOS, Windows, or Linux

## Setup

```bash
# Clone or open the project, then create a virtual environment
python3 -m venv venv

# Activate it
# macOS / Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

1. Click **Start Camera** to open the webcam preview.
2. Click **Capture Photo** to save a frame under `assets/captures/`.
3. Click **Preview Capture** (or the last-capture thumbnail) to open a larger preview.
4. Click **Stop Camera** when you are done.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests use Qt’s offscreen platform, so a display is not required.

## Project layout

```
pc-app/
├── app.py                 # Application entry point
├── requirements.txt       # Python dependencies
├── ui/
│   └── main_window.py     # Main window, camera, and capture UI
├── assets/
│   └── captures/          # Saved photos (created at runtime)
├── models/                # Reserved for future gesture models
├── services/              # Reserved for future services
└── tests/
    └── test_main_window.py
```

## Troubleshooting

- **Camera unavailable** — another app may be using the webcam, or camera permission may be denied. Quit other camera apps and allow access for the terminal/Python.
- **Import errors** — confirm the virtual environment is active and run `pip install -r requirements.txt` again.
- **Blank preview on macOS** — grant Camera access to Terminal (or your IDE) under System Settings → Privacy & Security → Camera.
