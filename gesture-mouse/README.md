<div align="center">

# 🖐️ GestureMouse

### Your hand is the mouse. Your gestures, your rules.

Control any website or desktop app with just a webcam, no extra hardware needed.

![Python](https://img.shields.io/badge/Python-3.9--3.11-3776AB?logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-00A67E)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Offline-success)
![License](https://img.shields.io/badge/License-MIT-blue)

**[Quick Start](#-quick-start)** · **[Gestures](#-gesture-cheat-sheet)** · **[How It Works](#-how-it-works)** · **[Customize](#-make-it-yours)** · **[FAQ](#-faq)**

<!-- Add a demo GIF here: ![demo](assets/demo.gif) -->

</div>

---

## ✨ Why GestureMouse?

Most hand-tracking mouse projects ship with fixed gestures. **GestureMouse lets
you define your own.**

| | Feature | What it does |
|---|---|---|
| 🎯 | **Smooth pointer** | A One-Euro filter removes jitter without adding lag |
| 🤏 | **Pinch to click & drag** | Hold the pinch and move to drag |
| ✌️ | **Built-in scroll mode** | Peace sign, then raise or lower your hand |
| 🧠 | **Train your own gestures** | Record a pose for 4 seconds and it's learned instantly |
| ⚡ | **Map to anything** | Shortcuts, websites, apps, typed text, lock/unlock |
| 🔒 | **Lock gesture** | Pause everything so you can talk with your hands |
| 🛡️ | **Private by design** | All processing is local, and no video is stored or sent |

---

## 🚀 Quick Start

```bash
# 1. Get the code
git clone https://github.com/<your-username>/gesture-mouse.git
cd gesture-mouse

# 2. Create an environment
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # Mac / Linux

# 3. Install
pip install -r requirements.txt

# 4. Run
python main.py
```

> 🍎 **Mac users:** allow your terminal under *System Settings → Privacy &
> Security* for both **Camera** and **Accessibility**, or the cursor won't move.

**First 60 seconds checklist**

- [ ] A window opens and a green skeleton follows your hand
- [ ] Moving your index finger inside the yellow box moves the cursor
- [ ] Pinching thumb + index clicks
- [ ] A peace sign ✌️ scrolls pages

---

## 🎮 Gesture Cheat Sheet

| Gesture | Action |
|---|---|
| ☝️ Point (index finger) | Move the cursor |
| 🤏 Pinch (thumb + index) | Left click |
| 🤏 + move | Click and drag |
| 🤏🤏 Two quick pinches | Double click |
| ✌️ Peace sign, hand **high** | Scroll up |
| ✌️ Peace sign, hand **low** | Scroll down |
| ✌️ Peace sign, hand **middle** | Stop scrolling |
| 🧩 *Your own gestures* | Anything you choose |

### 🎚️ Keyboard controls (in the preview window)

| Key | Action |
|---|---|
| `R` | Record a new gesture |
| `M` | Change what a gesture does |
| `D` | Delete a gesture |
| `L` | Lock / unlock control |
| `+` / `-` | Make clicking easier / harder |
| `Q` or `Esc` | Quit |

---

## 🧪 Create Your Own Gesture

<details>
<summary><b>👉 Click to expand: step-by-step</b></summary>

1. Press **`R`** in the preview window.
2. Type a name in the terminal, e.g. `fist`.
3. Hold the pose and slowly tilt your hand a little while the app records 120 samples.
4. Pick an action from the menu:
   - ⌨️ Keyboard shortcut (e.g. `ctrl+w`)
   - 🌐 Open a website or app
   - 📝 Type text
   - 🔒 Lock / unlock
5. Hold the gesture for about 0.3 seconds. It fires and the action name flashes on screen.

**💡 Pro tip:** first record a gesture named `neutral` (a relaxed open hand).
It teaches the app what *not* to react to.

**Starter pack**

| Name | Action |
|---|---|
| `neutral` | (none) relaxed hand |
| `fist` | `ctrl + w` close tab |
| `thumbs_up` | open your favourite site |
| `palm` | lock / unlock |

</details>

---

## 🔬 How It Works

```text
 Webcam ──► Mirror ──► MediaPipe ──► 21 hand landmarks
                                          │
                  ┌───────────────────────┴──────────────────────┐
                  ▼                                              ▼
        Cursor + pinch + scroll                     Normalize → KNN classifier
        (One-Euro smoothing)                                     │
                  │                                   Held for 8 frames?
                  ▼                                              │
              Mouse input ◄──────────── PyAutoGUI ◄──── Run mapped action
```

<details>
<summary><b>🧠 The key ideas (click to expand)</b></summary>

- **21 landmarks, not video.** MediaPipe reduces your hand to 21 (x, y, z) points,
  so the rest of the app works with tiny numbers instead of images.
- **Position and size don't matter.** Every gesture is re-centred on the wrist
  and divided by hand size, so a fist looks the same near or far.
- **Instant training.** K-Nearest-Neighbors just stores examples, so a new
  gesture works seconds after you record it.
- **No accidental triggers.** A gesture must be held for 8 frames, and unknown
  shapes are rejected by a distance threshold.
- **Hysteresis on clicks.** Pressing and releasing use different thresholds, so
  the click never flickers.

</details>

---

## 🛠️ Make It Yours

<details>
<summary><b>⚙️ Tuning guide (click to expand)</b></summary>

| Problem | Fix | File |
|---|---|---|
| Cursor is jittery | Lower `min_cutoff` (e.g. 0.5) | `smoothing.py` |
| Cursor lags | Raise `beta` (e.g. 15) | `smoothing.py` |
| Click is hard to trigger | Press `+` in the app | live |
| Gestures fire by accident | Lower `threshold` (e.g. 0.8) | `classifier.py` |
| Gestures never fire | Raise `threshold` (e.g. 1.6) | `classifier.py` |
| Scroll too fast / slow | Change `scroll_speed` | `cursor.py` |
| Wrong camera | `VideoCapture(1)` | `main.py` |

</details>

```text
gesture-mouse/
├── main.py          # app loop + on-screen display
├── tracker.py       # webcam hand landmarks
├── cursor.py        # pointer, pinch click, scroll
├── smoothing.py     # One-Euro filter
├── classifier.py    # record + recognise custom gestures
├── actions.py       # gesture → action mapping
└── data/            # your gestures and mappings (created automatically)
```

---

## ❓ FAQ

<details>
<summary><b>Does it record or upload my video?</b></summary>
No. Frames are processed in memory and discarded. Nothing is saved or sent.
</details>

<details>
<summary><b>Can I reset everything?</b></summary>
Yes. Delete the files inside the <code>data/</code> folder.
</details>

<details>
<summary><b>It works badly in my room</b></summary>
Use good front lighting, keep your whole hand in view, and avoid a busy
background. Record gestures in the same lighting you'll use them in.
</details>

<details>
<summary><b>Can I use my left hand?</b></summary>
Yes. Gestures are recorded from whichever hand you use.
</details>

---

## 🗺️ Roadmap

- [x] Cursor, click, drag
- [x] Built-in scroll mode
- [x] Custom gesture recorder
- [x] Lock gesture
- [ ] Desktop GUI for gesture management
- [ ] Per-application gesture profiles
- [ ] Multi-step macros
- [ ] Shareable gesture packs
- [ ] Dwell-click mode for accessibility

---

## 🤝 Contributing

Ideas, bug reports and pull requests are welcome. Fork the repo, create a
branch, and open a PR.

## 🙌 Built With

[MediaPipe](https://developers.google.com/mediapipe) ·
[OpenCV](https://opencv.org/) ·
[PyAutoGUI](https://pyautogui.readthedocs.io/) ·
[scikit-learn](https://scikit-learn.org/)

---

<div align="center">

**If this project helped you, give it a ⭐ and wave hello to your webcam 👋**

</div>
