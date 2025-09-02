import sys, os, json, re, signal, subprocess, time, shlex, typing
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QStyleFactory)
from PyQt5.QtCore import Qt, QProcess, pyqtSignal, QByteArray
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QFocusEvent

from settings_manager import SettingsManager
from tray_manager import TrayManager
from hotkey_manager import HotkeyManager
from ui_manager import UIManager
from process_manager import ProcessManager
from mode_controller import ModeController
from text_processor import TextProcessorEngine


class MainWindow(QMainWindow):
    log_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CompactApp • Multi-Tool Runner")
        self.is_quitting = False
        self.piper_path: str = str(Path.home())
        
        self.settings_manager = SettingsManager()
        self.ui = UIManager(self)
        self.tray_manager = TrayManager(self)
        self.hotkey_manager = HotkeyManager()
        self.process_manager = ProcessManager()
        self.text_processor = None
        self.mode_controller = None
        
        self.setup_signals()
        self._on_rule_changed(self.ui.rule_combo.currentText()) # Initial setup
        self.load_settings()
        self.log_message("[INFO] App Initialized.")

    def setup_signals(self):
        # Process Manager Signals
        self.process_manager.log_message.connect(self.log_message)
        self.process_manager.status_update.connect(self.update_status)
        self.process_manager.process_finished.connect(self.on_process_finished)

        # UI Signals
        self.ui.rule_combo.currentTextChanged.connect(self._on_rule_changed)
        self.ui.mode_slider.valueChanged.connect(self.update_ui_mode)
        self.ui.model_combo.currentTextChanged.connect(self.ui.load_model_config)
        self.ui.always_on_top_cb.toggled.connect(self.toggle_always_on_top)
        self.ui.opacity_slider.valueChanged.connect(self.update_opacity)
        self.ui.opacity_slider.sliderReleased.connect(self.update_opacity)
        self.ui.play_btn.clicked.connect(self.start_process)
        self.ui.pause_btn.clicked.connect(self.toggle_pause_process)
        self.ui.stop_btn.clicked.connect(self.stop_process)
        self.ui.set_path_btn.clicked.connect(self.ui.select_piper_path)
        self.ui.rescan_btn.clicked.connect(self.ui.scan_piper_models)
        self.ui.preview_btn.clicked.connect(self.preview_voice)
        self.ui.volume_slider.valueChanged.connect(self.update_volume_icon)
        
        # Main App Signals
        self.log_signal.connect(self.log_message)

        # Hotkey Manager Signals
        self.hotkey_manager.hotkey_status_changed.connect(self.on_hotkey_toggle)
        self.hotkey_manager.speak_selection.connect(self.on_speak_selection)
        self.hotkey_manager.stop_process.connect(self.stop_process)
        self.hotkey_manager.quit_application.connect(self.quit_application)
        self.hotkey_manager.log_message.connect(self.log_message)

    def preview_voice(self):
        """Preview the selected voice with a sample text."""
        sample_text = "Hello, this is a voice preview."
        if self.ui.model_combo.currentText():
            original_text = self.ui.tts_text_input.text()
            self.ui.tts_text_input.setText(sample_text)
            self.start_process()
            self.ui.tts_text_input.setText(original_text)

    def start_process(self):
        ui_state = self._get_ui_state_for_command()
        cmd_str = self.mode_controller.create_command(ui_state['mode'], ui_state)

        if not cmd_str:
            if ui_state['mode'] == 1: # Piper TTS mode
                self.update_status("Error: TTS text/model invalid", "error")
            return

        self._notify_process_start(ui_state['mode'])
        self.process_manager.start(cmd_str)
        self._update_ui_for_process_start()

    def stop_process(self):
        self.process_manager.stop()

    def toggle_pause_process(self):
        self.process_manager.toggle_pause()
        if self.process_manager.is_paused:
            self.ui.pause_btn.setText("▶ Resume")
        else:
            self.ui.pause_btn.setText("⏸ Pause")

    def on_process_finished(self, code: int, status: QProcess.ExitStatus, was_stopped: bool):
        msg = "Stopped by user" if was_stopped else f"Completed (code {code})"
        is_err = status != QProcess.ExitStatus.NormalExit or (code != 0 and not was_stopped)
        
        self._notify_process_finish(was_stopped, is_err)

        status_type = "error" if is_err else "ready"
        self.update_status(msg, status_type)
        self.log_message(f"[INFO] {msg}", "red" if is_err else "green")

        self._update_ui_for_process_finish()

    def log_message(self, message: str, color: str = "white"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.ui.log_view.append(f'<span style="color: #888;">{timestamp}</span> <span style="color: {color};">{message}</span>')

    def update_status(self, text: str, status_type: str = "ready"):
        self.ui.status_label.setText(text)
        self.ui.status_label.setProperty("status", status_type)
        self.ui.status_label.setStyle(self.ui.status_label.style())

    def _get_ui_state_for_command(self) -> dict:
        """Gathers the UI state needed for command creation."""
        return {
            'mode': self.ui.mode_slider.value(),
            'custom_cmd': self.ui.custom_cmd_input.text(),
            'tts_text': self.ui.tts_text_input.text(),
            'model': self.ui.model_combo.currentText(),
            'piper_path': self.piper_path,
            'speaker_id': self.ui.speaker_combo.currentData(),
            'is_multi_speaker': self.ui.is_multi_speaker(self.ui.model_combo.currentText()),
            'silence': self.ui.silence_spin.value(),
            'length': self.ui.length_spin.value(),
            'noise_s': self.ui.noise_scale_spin.value(),
            'noise_w': self.ui.noise_w_spin.value(),
            'volume': self.ui.volume_slider.value(),
        }

    def _notify_process_start(self, mode: int):
        """Shows a tray notification when a process starts."""
        mode_names = {0: 'Custom Command', 1: 'Piper TTS', 2: 'Ping Test', 3: 'Echo Test'}
        title = mode_names.get(mode, 'Process') + " Started"
        message = "The requested task is now running."

        if mode == 1:
            text = self.ui.tts_text_input.text().strip()
            if text == "Hello, this is a voice preview.":
                title = "Voice Preview"
                message = "Playing a sample of the selected voice."
            else:
                title = "Text-to-Speech Started"
                message = f"Reading: '{text[:40].strip()}...'"

        self.tray_manager.showMessage(title, message)

    def _update_ui_for_process_start(self):
        """Disables and enables UI elements when a process starts."""
        self.ui.play_btn.setEnabled(False)
        self.ui.stop_btn.setEnabled(True)
        if sys.platform != "win32":
            self.ui.pause_btn.setEnabled(True)
            self.ui.pause_btn.setText("⏸ Pause")

    def _notify_process_finish(self, was_stopped: bool, is_err: bool):
        """Shows a tray notification when a process finishes."""
        if was_stopped:
            title, message, icon = "Process Stopped", "The task was manually stopped by the user.", QSystemTrayIcon.Warning
            self.tray_manager.showMessage(title, message, icon, 3000)
        elif is_err:
            title, message, icon = "Process Error", "The task failed to complete.", QSystemTrayIcon.Warning
            self.tray_manager.showMessage(title, message, icon, 3000)
        elif not self.isVisible():
            title, message, icon = "Process Finished", "Task completed successfully.", QSystemTrayIcon.Information
            self.tray_manager.showMessage(title, message, icon, 3000)

    def _update_ui_for_process_finish(self):
        """Disables and enables UI elements when a process finishes."""
        self.ui.play_btn.setEnabled(True)
        self.ui.stop_btn.setEnabled(False)
        if sys.platform != "win32":
            self.ui.pause_btn.setEnabled(False)
            self.ui.pause_btn.setText("⏸ Pause")

    def _on_rule_changed(self, rule_file: str):
        if not rule_file:
            return
        self.log_message(f"Activating rule set: {rule_file}", "green")
        rules_dir = "txt_eng_rules"
        rule_path = os.path.join(rules_dir, rule_file)
        self.text_processor = TextProcessorEngine(rules_file_path=rule_path)
        self.mode_controller = ModeController(self.text_processor)

    def update_ui_mode(self, value: int):
        self.ui.stacked_widget.setCurrentIndex(value)
        mode_names = {0: 'Custom', 1: 'Piper TTS', 2: 'Ping', 3: 'Echo'}
        self.ui.mode_name_label.setText(mode_names.get(value, 'Unknown'))

    def update_volume_icon(self, value: int):
        if value == 0:
            self.ui.volume_icon.setText("🔇")
        elif value <= 50:
            self.ui.volume_icon.setText("🔉")
        else:
            self.ui.volume_icon.setText("🔊")

    def on_hotkey_toggle(self, enabled: bool):
        status = "active" if enabled else "inactive"
        text = f"Hotkeys: {'ON' if enabled else 'OFF'}"
        self.ui.hotkey_label.setText(text)
        self.ui.hotkey_label.setProperty("hotkey", status)
        self.ui.hotkey_label.setStyle(self.ui.hotkey_label.style())
        
        self.log_message(f"[INFO] {text}", '#32CD32' if enabled else 'grey')
        
        title = "Hotkeys Activated" if enabled else "Hotkeys Deactivated"
        message = f"Global hotkeys are now {'ON' if enabled else 'OFF'}."
        icon = QSystemTrayIcon.Information
        self.tray_manager.showMessage(title, message, icon, 2000)

    def on_speak_selection(self, text: str):
        self.ui.mode_slider.setValue(1)
        self.ui.tts_text_input.setText(text)
        self.start_process()

    def toggle_always_on_top(self, checked: bool):
        flags = self.windowFlags()
        if checked:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        
        self.ui.opacity_slider.setVisible(checked)
        self.update_opacity()
        self.show()

    def update_opacity(self, _=None):
        opacity = 1.0
        
        if self.ui.always_on_top_cb.isChecked():
            is_slider_pressed = self.ui.opacity_slider.isSliderDown()
            
            if not self.isActiveWindow() or is_slider_pressed:
                opacity = self.ui.opacity_slider.value() / 100.0
        
        self.setWindowOpacity(opacity)

    def focusInEvent(self, e: QFocusEvent):
        super().focusInEvent(e)
        self.update_opacity()

    def focusOutEvent(self, e: QFocusEvent):
        super().focusOutEvent(e)
        self.update_opacity()

    def _get_current_settings(self) -> dict:
        """Gathers the current state of all UI settings into a dictionary."""
        return {
            'piper_path': self.piper_path,
            'custom_cmd': self.ui.custom_cmd_input.text(),
            'tts_text': self.ui.tts_text_input.text(),
            'on_top': self.ui.always_on_top_cb.isChecked(),
            'transparency': self.ui.opacity_slider.value(),
            'volume': self.ui.volume_slider.value(),
            'silence': self.ui.silence_spin.value(),
            'length': self.ui.length_spin.value(),
            'noise_s': self.ui.noise_scale_spin.value(),
            'noise_w': self.ui.noise_w_spin.value(),
            'mode': self.ui.mode_slider.value(),
            'model': self.ui.model_combo.currentText(),
            'speaker': self.ui.speaker_combo.currentData(),
            'rule_set': self.ui.rule_combo.currentText(),
            'geometry': self.saveGeometry().toBase64().data().decode()
        }

    def _apply_settings(self, s: dict):
        """Applies a dictionary of settings to the UI."""
        self.piper_path = s.get('piper_path', self.piper_path)
        self.ui.custom_cmd_input.setText(s.get('custom_cmd', "echo 'Hello!'"))
        self.ui.tts_text_input.setText(s.get('tts_text', "Hello from Piper."))
        self.ui.always_on_top_cb.setChecked(s.get('on_top', False))
        self.ui.opacity_slider.setValue(s.get('transparency', 100))
        self.ui.volume_slider.setValue(s.get('volume', 75))
        self.ui.silence_spin.setValue(s.get('silence', 0.0))
        self.ui.length_spin.setValue(s.get('length', 1.0))
        self.ui.noise_scale_spin.setValue(s.get('noise_s', 0.667))
        self.ui.noise_w_spin.setValue(s.get('noise_w', 0.8))
        self.ui.mode_slider.setValue(s.get('mode', 1))

        if 'geometry' in s:
            try:
                self.restoreGeometry(QByteArray.fromBase64(s['geometry'].encode()))
            except Exception as e:
                self.log_message(f"[WARN] Could not restore window geometry: {e}", "orange")

        self.ui.scan_piper_models()
        
        saved_model = s.get('model')
        if saved_model:
            index = self.ui.model_combo.findText(saved_model)
            if index != -1:
                self.ui.model_combo.setCurrentIndex(index)
        
        saved_speaker_id = s.get('speaker')
        if saved_speaker_id is not None:
            index = self.ui.speaker_combo.findData(saved_speaker_id)
            if index != -1:
                self.ui.speaker_combo.setCurrentIndex(index)

        saved_rule_set = s.get('rule_set')
        if saved_rule_set:
            index = self.ui.rule_combo.findText(saved_rule_set)
            if index != -1:
                self.ui.rule_combo.setCurrentIndex(index)

    def save_settings(self):
        """Saves current settings using the SettingsManager."""
        settings = self._get_current_settings()
        self.settings_manager.save_settings(settings)

    def load_settings(self):
        """Loads settings using the SettingsManager and applies them to the UI."""
        settings = self.settings_manager.load_settings()
        self._apply_settings(settings)
        self.log_message("[INFO] Settings loaded.")

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Handle window close event."""
        if self.is_quitting:
            self.save_settings()
            self.hotkey_manager.stop_listener()
            self.proc.kill()
            event.accept()
        else:
            event.ignore()
            self.hide()
            self.tray_manager.showMessage(
                "CompactApp is running",
                "Application minimized to system tray."
            )

    def quit_application(self):
        """Prepare for and initiate application exit."""
        self.log_message("[INFO] Quitting application...", "orange")
        self.is_quitting = True
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if "Fusion" in QStyleFactory.keys():
        app.setStyle(QStyleFactory.create("Fusion"))
    
    window = CompactApp()
    window.show()
    sys.exit(app.exec_())
