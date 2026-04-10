
<div align="center">

# 🧪 Forensic Video Player

**A high-precision, feature-rich video analysis tool built with Python and PyQt6.**
Designed for investigators, editors, and developers who need frame-accurate control and real-time visual diagnostics.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Shortcuts](#%EF%B8%8F-keyboard-shortcuts) • [Architecture](#%EF%B8%8F-architecture)

</div>

----

## 📸 Media & Demos

<div align="center">
  
## Main Interface
*Showcase the dark/light theme, the timeline, and the main playback controls.*
<br>
![Main Interface Dark](https://via.placeholder.com/800x450/232326/5849e2?text=ADD+YOUR+SCREENSHOT+HERE)
<br>
![Main Interface Light](https://via.placeholder.com/800x450/f8f8f9/5849e2?text=ADD+LIGHT+MODE+SCREENSHOT+HERE)

## Forensic Tools in Action
*Showcase the motion detection overlay, blur detection graph, or scene change list.*
<br>
![Motion Detection](https://via.placeholder.com/800x450/232326/4caf50?text=ADD+MOTION+DETECTION+GIF+HERE)

## Zoom & ROI Selection
*Show a GIF of drawing an ROI or using the dynamic zoom slider.*
<br>
![Zoom Feature](https://via.placeholder.com/800x450/232326/ff9800?text=ADD+ZOOM+DEMO+GIF+HERE)

## 🎥 Video Demo
*For video demos, it is recommended to upload an MP4 to the repo and link it, or use a YouTube embed.*
<br>
<a href="https://www.youtube.com/watch?v=YOUR_VIDEO_ID" target="_blank">
  <img src="https://via.placeholder.com/800x450/111113/e0e0e0?text=CLICK+TO+WATCH+YOUTUBE+DEMO" alt="Video Demo" width="800"/>
</a>
</div>


---
---

## 🖼️ Screenshots

<div align="center">
   
## 🎥 Demo Video
<!-- Add your video below -->
![video-demo](screenshots/video-demo.gif)
*( Demonstrating GUI Usage )*

<br>

## Dark Mode
<!-- Add your screenshot below -->
![Dark Mode Screenshot](screenshots/dark-mode.png)
*( The default dark theme with the full interface layout )*

<br>

## Light Mode
<!-- Add your screenshot below -->
![Light Mode Screenshot](screenshots/light-mode.png)
*( Clean light theme for bright environments )*

<br>

## Collapsible Advanced Parameters
<!-- Add your screenshot below -->
![Parameters Expanded](screenshots/collapsible-parameters.png)
*( Organized parameter sections with expand/collapse functionality )*

<br>

## Search & Filter
<!-- Add your screenshot below -->
![Search Filter](screenshots/search-filter.png)
*( Quickly find any parameter by name or description )*

<br>

</div>

---
---

## ✨ Features

### 🎬 Core Playback
- **Frame-Accurate Seeking:** Precise timeline slider with scroll-to-skip (500ms/1000ms).
- **Advanced Speed Control:** Playback rates from 0.25x to 2.0x.
- **A→B Looping:** Set custom in/out points for forensic review.
- **Segment Export:** Record and export specific clips directly via FFmpeg.

### 🕵️ Forensic Analysis Suite
- **Real-Time Motion Detection:** Live overlay with customizable sensitivity, minimum object area, and Region of Interest (ROI) support.
- **Clip Analyzer:** Generates motion frequency bar charts. Click the graph to jump to high-action segments.
- **Scene Change Detection:** Automatic histogram-based scene boundary detection.
- **Blur Detection:** Laplacian variance analysis to find out-of-focus or blurry frames.
- **Brightness Analysis:** Track overexposure and underexposure across the entire timeline.

### 🎨 UI & UX
- **Dynamic Theming:** Seamless Dark and Light modes.
- **Interactive Zoom:** Minimap navigator with draggable selection and a vertical zoom slider.
- **Clickable Graphs:** Click directly on Matplotlib timelines to seek to that exact millisecond.
- **Modern Aesthetics:** Rounded corners, custom QSS styling, and smooth transitions.

---

## 📦 Installation

### Prerequisites
- **Python 3.10 or higher**
- **FFmpeg** (Required for segment recording/exporting) 
  *(e.g., `sudo apt install ffmpeg` or `brew install ffmpeg`)*

### Clone & Setup

```bash
# Clone the repository
git clone https://github.com/Himanshu-369/ForensicVideoPlayer.git
cd ForensicVideoPlayer

# Create and activate a virtual environment (Recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install PyQt6 PyQt6-Multimedia

# Install forensic dependencies
pip install opencv-python numpy matplotlib
```

### Run the Application

```bash
python ForensicVideoPlayer.py
```

---

## 🚀 Usage

1. **Load Media:** Click `📂 Open` or drag and drop a video file (`.mp4`, `.mkv`, `.avi`, etc.).
2. **Basic Controls:** Use `▶ Play`, `⏹ Stop`, and the `Speed` dropdown to control playback.
3. **Zoom:** Click `🔍 Zoom` to open the mini-preview map. Drag the box or use the vertical slider to zoom.
4. **Forensics:** Click `🧪 Forensics` to open the analysis menu. Choose an analysis type (e.g., Blur Detection).
5. **Interact with Graphs:** Once an analysis finishes, click directly on the peaks/bars in the graph to instantly jump the video to that timestamp.
6. **Export:** Click `⏺ Record` to set point A, then click again to set point B and save the clip.

---

## ⌨️ Keyboard Shortcuts

<details>
<summary>Click to expand shortcuts</summary>

| Key | Action |
| :--- | :--- |
| `Space` | Play / Pause |
| `←` (Left Arrow) | Seek backward 5 seconds |
| `→` (Right Arrow) | Seek forward 5 seconds |
| `Shift + ←` | Seek backward 1 second |
| `Shift + →` | Seek forward 1 second |
| `↑` (Up Arrow) | Increase volume by 5% |
| `↓` (Down Arrow) | Decrease volume by 5% |
| `Z` | Toggle Zoom Mode |
| `F` | Toggle Real-time Motion Detection Panel |

</details>

---

## 🏗️ Architecture

The application is built using a modular Model-View-Controller-ish architecture using PyQt6:

- **`VideoPlayer` (Main Window):** The central coordinator handling UI state, theme management, and media routing.
- **`FrameDisplayWidget`:** Custom `QWidget` utilizing `QPainter` to render video frames, zoom crops, and geometric overlays (Motion, ROI) at high frame rates without DOM overhead.
- **`MotionDetector`:** Standalone processing class using OpenCV background subtraction (`cv2.absdiff`) and contour finding, completely decoupled from the UI thread.
- **`VideoAnalysisThread`:** A `QThread` subclass that handles heavy offline analysis (Scene Change, Blur, Brightness) to keep the UI completely responsive.
- **`ClickableTimeline`:** A custom `FigureCanvasQTAgg` (Matplotlib) implementation capturing mouse events and converting data coordinates back into video milliseconds.
- **`AnalysisDialog` Base Class:** A template method pattern for all forensic dialogs, handling threading, progress bars, cancellation, and cleanup automatically.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the [issues page](https://github.com/Himanshu-369/ForensicVideoPlayer/issues).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
Made with ❤️ by <b>Your Name</b>
</div>


### 💡 Tips for adding your media:
1. **Screenshots:** Create a folder in your repo called `docs/images/`. Save your PNGs there, and update the links in the README to `![Alt Text](docs/images/your-file.png)`.
2. **GIFs:** Record your screen using a tool like **ShareX** (Windows), **RecordIt** (Mac), or **OBS Studio**. Save them as `.gif` files in the same folder. GIFs are highly recommended for showing the "Zoom" and "Motion Detection" features.
3. **YouTube Video:** Upload your full walkthrough to YouTube as "Unlisted", grab the video ID (the string of letters/numbers after `v=` in the URL), and replace `YOUR_VIDEO_ID` in the Markdown link provided.
