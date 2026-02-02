# 🖐️ MPHCI - MediaPipe Hand-Computer Interface

A real-time hand gesture control system for computer mouse and click operations. Built with MediaPipe for hand tracking and advanced filtering algorithms for ultra-precise, smooth cursor control.
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)

## 🎯 What is MPHCI?

MPHCI (MediaPipe Hand-Computer Interface) enables touchless computer control through intuitive hand gestures detected via webcam. Move your cursor by pointing your index finger, click and drag by pinching - all without touching your mouse or trackpad.

**Perfect for:**
- 🎤 **Presentations** - Control slides without touching keyboard
- ♿ **Accessibility** - Alternative input for users with mobility challenges  
- 🎓 **Education** - Teaching computer vision and signal processing
- 🧪 **Research** - Baseline for HCI and gesture recognition studies

## ✨ Key Features

- **Ultra-Smooth Cursor Control** - Multi-stage filtering pipeline using One Euro Filter
- **Smart Gesture Recognition** - Automatic differentiation between clicks and drags
  - Quick pinch (<200ms) = Click
  - Pinch + hold/move = Drag & drop
- **Real-Time Performance** - Optimized for 30-60 FPS with minimal latency
- **Adaptive Smoothing** - Intelligent filtering that adapts to movement speed
- **Highly Configurable** - Easy parameter tuning via config file with presets
- **Non-Intrusive** - Use trackpad/mouse simultaneously while system runs

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam (built-in or external)
- Operating System: Windows, macOS, or Linux

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Gislain-Mar/MCHPI.git
cd mphci
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download MediaPipe hand model**
   - Download `hand_landmarker.task` from [MediaPipe Solutions](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
   - Place it in the `models/` directory

### Usage

```bash
python main.py
```

**Gesture Controls:**
- 👆 **Index finger** - Controls cursor position
- 🤏 **Pinch** (thumb + middle finger):
  - Quick pinch & release → **Click**
  - Pinch & hold (>200ms) → **Drag start**
  - Move while pinching → **Dragging**
  - Release → **Drop**

## 🔧 Configuration

MPHCI uses a centralized configuration system. All parameters can be tuned in `config.py`.

### Smoothness Presets

Choose a preset in `main.py` before starting:

```python
# Presets.ultra_smooth()   # Maximum smoothness, slight lag
# Presets.balanced()       # Default - good for most users
# Presets.responsive()     # Fast response, minimal smoothing
```

### Manual Tuning

Edit `config.py` for fine-grained control:

```python
class FilterConfig:
    MIN_CUTOFF = 1.0    # Lower = smoother, Higher = more responsive
    BETA = 0.01         # Velocity adaptation (keep 0.005-0.02)
    
class MovementConfig:
    GAIN = 3.0          # Cursor speed multiplier
    MAX_SPEED = 35      # Maximum pixels per frame
    VELOCITY_SMOOTHING = 0.5  # Acceleration smoothing

class GestureConfig:
    PINCH_THRESHOLD = 0.05           # Pinch detection sensitivity
    CLICK_TIME_THRESHOLD = 0.2       # Max time for click (seconds)
    DRAG_DISTANCE_THRESHOLD = 0.01   # Min movement for drag
```

## 🧠 How It Works

### Smoothing Pipeline

MPHCI uses a sophisticated multi-stage filtering pipeline:

```
Raw Hand Landmarks (MediaPipe)
    ↓
[Stage 1] One Euro Filter → Removes high-frequency jitter
    ↓
[Stage 2] Velocity Calculation → Converts position to movement
    ↓
[Stage 3] Exponential Smoothing → Smooths acceleration
    ↓
[Stage 4] Speed Limiting → Prevents sudden jumps
    ↓
[Stage 5] Screen Mapping → Final cursor position
```

### One Euro Filter

The core algorithm is the **One Euro Filter** - an adaptive low-pass filter that:
- Applies heavy smoothing when hand is still (eliminates jitter)
- Reduces smoothing when hand is moving (minimizes lag)
- Smooths both position AND velocity for optimal stability

**Result:** Butter-smooth cursor that responds instantly to intentional movements.

### Click vs Drag Detection

Smart temporal and spatial analysis differentiates gestures:

1. **Pinch detected** → Start timer, record position
2. **Held >200ms OR moved >10px** → Trigger drag mode
3. **Released before threshold** → Execute click
4. **Released after drag** → End drag (drop)

## 🛠️ Technical Details

**Technologies:**
- **MediaPipe** - Hand landmark detection (21 3D points per hand)
- **OpenCV** - Video capture and processing
- **PyAutoGUI** - Cross-platform mouse control
- **One Euro Filter** - Adaptive signal smoothing algorithm

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Additional gesture recognition (peace sign, fist, etc.)
- [ ] Two-hand support for advanced controls
- [ ] Gesture customization UI
- [ ] Calibration wizard for different hand sizes
- [ ] Performance profiling and optimization

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **One Euro Filter** - [Géry Casiez & Nicolas Roussel (2012)](http://cristal.univ-lille.fr/~casiez/1euro/)
- **MediaPipe** - [Google Research](https://mediapipe.dev/)
- Inspired by various hand tracking projects in the computer vision community

## 📧 Support

Found a bug? Have a feature request?
- Open an issue on [GitHub Issues](https://github.com/Gislain-Mar/MCHPI/issues)
- Check existing issues first to avoid duplicates

## 🌟 Show Your Support

If you find MPHCI useful:
- ⭐ Star this repository
- 🐛 Report bugs and suggest features
- 🔀 Fork and contribute improvements
- 📢 Share with others who might benefit