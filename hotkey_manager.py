import sys
import time
import subprocess
try:
    from pynput import keyboard
except ImportError:
    keyboard = None
from PyQt5.QtCore import QObject, pyqtSignal

class HotkeyManager(QObject):
    hotkey_status_changed = pyqtSignal(bool)
    speak_selection = pyqtSignal(str)
    stop_process = pyqtSignal()
    quit_application = pyqtSignal()
    log_message = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.listener = None
        self.hotkeys_enabled = False
        self.last_lshift_press_time = 0
        self.last_esc_press_time = 0
        self._start_listener()

    def _start_listener(self):
        if not keyboard:
            self.log_message.emit("[WARN] pynput not found or display not available, hotkeys disabled.", "orange")
            return
        try:
            self.listener = keyboard.Listener(on_press=self._on_hotkey_press)
            self.listener.start()
        except Exception as e:
            self.log_message.emit(f"[ERROR] Failed to start hotkey listener: {e}", "red")

    def stop_listener(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception as e:
                self.log_message.emit(f"[WARN] Could not stop listener: {e}", "orange")

    def _on_hotkey_press(self, key):
        now = time.time()
        if key == keyboard.Key.shift_l:
            if now - self.last_lshift_press_time < 0.4:
                self.hotkeys_enabled = not self.hotkeys_enabled
                self.hotkey_status_changed.emit(self.hotkeys_enabled)
            self.last_lshift_press_time = now
        elif self.hotkeys_enabled and key == keyboard.Key.esc:
            if now - self.last_esc_press_time < 0.4:
                self.quit_application.emit()
            else:
                self.stop_process.emit()
            self.last_esc_press_time = now
        elif self.hotkeys_enabled and key == keyboard.Key.shift_r and sys.platform == "linux":
            try:
                text = subprocess.run(['xsel', '-o'], capture_output=True, text=True, check=True, timeout=1).stdout.strip()
                if text:
                    self.speak_selection.emit(text)
            except Exception as e:
                self.log_message.emit(f"[ERROR] Hotkey failed: {e}", "red")
