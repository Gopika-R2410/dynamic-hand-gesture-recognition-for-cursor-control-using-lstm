"""Gesture -> action mapping and execution."""
import json
import os
import subprocess
import sys
import webbrowser
import pyautogui

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "data", "config.json")
CONTINUOUS = {"scroll_up", "scroll_down"}  # repeat while the gesture is held


class ActionStore:
    def __init__(self):
        self.map = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                self.map = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.map, f, indent=2)

    def set(self, gesture, action):
        self.map[gesture] = action
        self.save()

    def get(self, gesture):
        return self.map.get(gesture)

    def remove(self, gesture):
        self.map.pop(gesture, None)
        self.save()


def prompt_for_action():
    """Ask the user (in the terminal) what a gesture should do."""
    print("\nWhat should this gesture do?")
    print("  1) Keyboard shortcut   (e.g. ctrl+w)")
    print("  2) Open website / app  (e.g. https://youtube.com or notepad)")
    print("  3) Type text")
    print("  4) Scroll up (while held)")
    print("  5) Scroll down (while held)")
    print("  6) Lock / unlock gesture control")
    print("  7) Nothing")
    choice = input("Choose 1-7: ").strip()
    if choice == "1":
        keys = input("Keys joined with + : ").lower().replace(" ", "").split("+")
        return {"type": "hotkey", "keys": keys}
    if choice == "2":
        return {"type": "open", "target": input("URL or program: ").strip()}
    if choice == "3":
        return {"type": "type", "text": input("Text to type: ")}
    if choice == "4":
        return {"type": "scroll_up"}
    if choice == "5":
        return {"type": "scroll_down"}
    if choice == "6":
        return {"type": "toggle_lock"}
    return None


def run_action(action):
    t = action["type"]
    if t == "hotkey":
        pyautogui.hotkey(*action["keys"])
    elif t == "open":
        target = action["target"]
        if target.startswith("http"):
            webbrowser.open(target)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", target])
        else:
            subprocess.Popen(target, shell=True)
    elif t == "type":
        pyautogui.write(action["text"], interval=0.02)
    elif t == "scroll_up":
        pyautogui.scroll(120)
    elif t == "scroll_down":
        pyautogui.scroll(-120)
