import sys, os, json, re, signal, subprocess, time, shlex, typing
from datetime import datetime
from pathlib import Path
# try:
from pynput import keyboard
# except ImportError:
    # keyboard = None
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QSlider, QHBoxLayout, QLineEdit, QGroupBox, QFormLayout, QComboBox, QDoubleSpinBox, QCheckBox, QTextEdit, QStyle, QSystemTrayIcon, QMenu, QStyleFactory, QFileDialog, QStackedWidget, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QProcess, pyqtSignal, QByteArray
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QFocusEvent


CONFIG_DIR = Path(os.path.expanduser("~")) / ".config" / "CompactApp"
CONFIG_FILE = CONFIG_DIR / "settings.json"
class CompactApp(QMainWindow):
    log_signal = pyqtSignal(str, str)
    hotkey_status_signal = pyqtSignal(bool)
    speak_selection_signal = pyqtSignal(str)
    stop_process_signal = pyqtSignal()
    quit_application_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CompactApp • Multi-Tool Runner")
        self.is_quitting, self.was_stopped, self.is_paused = False, False, False
        self.listener = None
        self.piper_path: str = str(Path.home())
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.proc = QProcess(self)
        
        # Apply modern styling
        self.setStyleSheet(self.get_modern_stylesheet())
        
        # Setup UI
        self.setup_ui()
        self.setup_signals()
        self.setup_tray_icon()
        self.setup_hotkey_listener()
        self.load_settings()
        self.log_message("[INFO] App Initialized.")

    def get_modern_stylesheet(self):
        return """
        /* ========== GLOBAL ========== */
        * {
            background: #111417;
            color: #ECEFF4;
            font-family: "Inter", "Roboto", sans-serif;
            font-size: 14px;
            border: none;
        }

        QMainWindow {
            background: #111417;
        }

        /* ========== ACCENT COLOR ========== */
        QPushButton[accent="true"] {
            background: #0AB4FF;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }
        QPushButton[accent="true"]:hover {
            background: #0087D7;
        }
        QPushButton[accent="true"]:pressed {
            background: #006BB3;
        }
        QPushButton[accent="true"]:disabled {
            background: #2E3440;
            color: #606060;
        }

        /* ========== SECONDARY BUTTONS ========== */
        QPushButton {
            background: #1A1D23;
            border: 1px solid #2E3440;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            border-color: #0AB4FF;
        }
        QPushButton:pressed {
            background: #141720;
        }
        QPushButton:disabled {
            background: #1A1D23;
            border-color: #2E3440;
            color: #606060;
        }

        /* ========== INPUTS ========== */
        QLineEdit, QComboBox, QDoubleSpinBox {
            background: #1A1D23;
            border: 1px solid #2E3440;
            border-radius: 4px;
            padding: 6px;
        }
        QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
            border-color: #0AB4FF;
        }

        /* ========== SLIDERS ========== */
        QSlider::groove:horizontal {
            height: 4px;
            background: #2E3440;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            width: 18px;
            height: 18px;
            background: #0AB4FF;
            border-radius: 9px;
            margin: -7px 0;
        }
        QSlider::sub-page:horizontal {
            background: #0AB4FF;
            border-radius: 2px;
        }

        /* ========== CHECKBOX ========== */
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #2E3440;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            background: #0AB4FF;
        }

        /* ========== GROUP BOX ========== */
        QGroupBox {
            font-weight: 600;
            border: 1px solid #2E3440;
            border-radius: 6px;
            margin-top: 6px;
            padding-top: 6px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }

        /* ========== LOG VIEW ========== */
        QTextEdit {
            background: #0C0E11;
            border: 1px solid #2E3440;
            border-radius: 6px;
            padding: 6px;
            font-family: "JetBrains Mono", "Consolas", monospace;
            font-size: 12px;
        }

        /* ========== LABELS ========== */
        QLabel {
            background: transparent;
        }
        
        QLabel[status="ready"] {
            color: #A3BE8C;
            font-weight: 600;
        }
        
        QLabel[status="running"] {
            color: #EBCB8B;
            font-weight: 600;
        }
        
        QLabel[status="error"] {
            color: #BF616A;
            font-weight: 600;
        }
        
        QLabel[hotkey="active"] {
            color: #A3BE8C;
            font-weight: 600;
        }
        
        QLabel[hotkey="inactive"] {
            color: #606060;
            font-weight: 600;
        }

        /* ========== STACKED WIDGET ========== */
        QStackedWidget {
            background: transparent;
        }
        """

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Top controls bar
        top_bar = QHBoxLayout()
        self.always_on_top_cb = QCheckBox("Always on Top")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(25)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setMaximumWidth(120)
        self.opacity_slider.setVisible(False)
        self.opacity_label = QLabel("Opacity")
        
        top_bar.addWidget(self.always_on_top_cb)
        top_bar.addStretch()
        top_bar.addWidget(self.opacity_slider)
        top_bar.addWidget(self.opacity_label)
        
        # Mode selection
        mode_row = QHBoxLayout()
        self.mode_label = QLabel("Mode")
        self.mode_slider = QSlider(Qt.Orientation.Horizontal)
        self.mode_slider.setMinimum(0)
        self.mode_slider.setMaximum(3)
        self.mode_slider.setValue(1)
        self.mode_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.mode_name_label = QLabel("Piper TTS")
        
        mode_row.addWidget(self.mode_label)
        mode_row.addWidget(self.mode_slider)
        mode_row.addWidget(self.mode_name_label)

        # Stacked widget for different modes
        self.stacked_widget = QStackedWidget()
        
        # Custom command page
        self.custom_page = QWidget()
        custom_layout = QVBoxLayout(self.custom_page)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_cmd_input = QLineEdit()
        self.custom_cmd_input.setPlaceholderText("Enter shell command…")
        custom_layout.addWidget(self.custom_cmd_input)
        self.stacked_widget.addWidget(self.custom_page)

        # Piper TTS page
        self.piper_page = QWidget()
        piper_layout = QVBoxLayout(self.piper_page)
        piper_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tts_text_input = QLineEdit()
        self.tts_text_input.setPlaceholderText("Type or select text to speak…")
        piper_layout.addWidget(self.tts_text_input)
        
        # Piper settings group
        self.piper_group = QGroupBox("Voice & Advanced Settings")
        piper_form = QFormLayout(self.piper_group)
        
        # Model selection row
        model_row = QHBoxLayout()
        self.model_combo = QComboBox()
        self.set_path_btn = QPushButton("Set Path")
        self.rescan_btn = QPushButton("Rescan")
        self.preview_btn = QPushButton("Play Sample")
        self.preview_btn.setProperty("accent", True)
        
        model_row.addWidget(self.model_combo)
        model_row.addWidget(self.set_path_btn)
        model_row.addWidget(self.rescan_btn)
        model_row.addWidget(self.preview_btn)
        
        piper_form.addRow("Voice Model", model_row)
        
        # Speaker selection
        self.speaker_combo = QComboBox()
        piper_form.addRow("Speaker", self.speaker_combo)
        
        # Advanced settings
        self.silence_spin = QDoubleSpinBox()
        self.silence_spin.setRange(0.0, 5.0)
        self.silence_spin.setSingleStep(0.1)
        self.silence_spin.setValue(0.0)
        piper_form.addRow("Sentence Silence", self.silence_spin)
        
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(0.1, 3.0)
        self.length_spin.setSingleStep(0.1)
        self.length_spin.setValue(1.0)
        piper_form.addRow("Length Scale", self.length_spin)
        
        self.noise_scale_spin = QDoubleSpinBox()
        self.noise_scale_spin.setRange(0.0, 2.0)
        self.noise_scale_spin.setSingleStep(0.1)
        self.noise_scale_spin.setValue(0.667)
        piper_form.addRow("Noise Scale", self.noise_scale_spin)
        
        self.noise_w_spin = QDoubleSpinBox()
        self.noise_w_spin.setRange(0.0, 2.0)
        self.noise_w_spin.setSingleStep(0.1)
        self.noise_w_spin.setValue(0.8)
        piper_form.addRow("Noise W", self.noise_w_spin)
        
        piper_layout.addWidget(self.piper_group)
        self.stacked_widget.addWidget(self.piper_page)

        # Ping page (empty)
        self.ping_page = QWidget()
        self.stacked_widget.addWidget(self.ping_page)

        # Echo page (empty)
        self.echo_page = QWidget()
        self.stacked_widget.addWidget(self.echo_page)

        # Set initial page
        self.stacked_widget.setCurrentIndex(1)  # Start with Piper TTS

        # Log view
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(120)

        # Playback controls
        playback_bar = QHBoxLayout()
        self.play_btn = QPushButton("▶ Execute")
        self.play_btn.setProperty("accent", True)
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setEnabled(False)
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(75)
        self.volume_slider.setMaximumWidth(100)
        self.volume_icon = QLabel()
        self.update_volume_icon(self.volume_slider.value())
        
        playback_bar.addWidget(self.play_btn)
        playback_bar.addWidget(self.pause_btn)
        playback_bar.addWidget(self.stop_btn)
        playback_bar.addStretch()
        playback_bar.addWidget(self.volume_slider)
        playback_bar.addWidget(self.volume_icon)

        # Status bar
        status_bar = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setProperty("status", "ready")
        self.hotkey_label = QLabel("Right ⇧ to speak selection")
        self.hotkey_label.setProperty("hotkey", "inactive")
        
        status_bar.addWidget(self.status_label)
        status_bar.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        status_bar.addWidget(self.hotkey_label)

        # Add all layouts to main layout
        main_layout.addLayout(top_bar)
        main_layout.addLayout(mode_row)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.log_view, 1)
        main_layout.addLayout(playback_bar)
        main_layout.addLayout(status_bar)
        
        if sys.platform == "win32":
            self.pause_btn.setEnabled(False)
            self.pause_btn.setToolTip("Pause/Resume is not supported on Windows")

        # Set window size
        self.resize(520, 680)

    def setup_signals(self):
        self.proc.readyReadStandardOutput.connect(lambda: self.log_message(self.proc.readAllStandardOutput().data().decode(errors='ignore').strip()))
        self.proc.readyReadStandardError.connect(lambda: self.log_message(f"[ERROR] {self.proc.readAllStandardError().data().decode(errors='ignore').strip()}", 'red'))
        self.proc.finished.connect(self.on_process_finished)
        self.mode_slider.valueChanged.connect(self.update_ui_mode)
        self.model_combo.currentTextChanged.connect(self.load_model_config)
        self.always_on_top_cb.toggled.connect(self.toggle_always_on_top)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        self.opacity_slider.sliderReleased.connect(self.update_opacity)
        self.play_btn.clicked.connect(self.start_process)
        self.pause_btn.clicked.connect(self.toggle_pause_process)
        self.stop_btn.clicked.connect(self.stop_process)
        self.set_path_btn.clicked.connect(self.select_piper_path)
        self.rescan_btn.clicked.connect(self.scan_piper_models)
        self.preview_btn.clicked.connect(self.preview_voice)
        self.volume_slider.valueChanged.connect(self.update_volume_icon)
        self.log_signal.connect(self.log_message)
        self.hotkey_status_signal.connect(self.on_hotkey_toggle)
        self.speak_selection_signal.connect(self.on_speak_selection)
        self.stop_process_signal.connect(self.stop_process)
        self.quit_application_signal.connect(self.quit_application)

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        menu = QMenu()
        toggle_action = menu.addAction("Show / Hide")
        toggle_action.triggered.connect(self.toggle_visibility)
        menu.addSeparator()
        menu.addAction("Exit", self.quit_application)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def toggle_visibility(self):
        """Toggles the main window's visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    def on_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Handle tray icon activation to toggle window visibility on left-click."""
        if reason == QSystemTrayIcon.Trigger:  # Standard left-click
            self.toggle_visibility()

    def setup_hotkey_listener(self):
        if not keyboard:
            self.log_message("[WARN] pynput not found, hotkeys disabled.", "orange")
            return
        self.hotkeys_enabled = False
        self.last_lshift_press_time, self.last_esc_press_time = 0, 0
        try:
            self.listener = keyboard.Listener(on_press=self.on_hotkey_press)
            self.listener.start()
        except Exception as e:
            self.log_message(f"[ERROR] Failed to start hotkey listener: {e}", "red")

    def preview_voice(self):
        """Preview the selected voice with a sample text."""
        sample_text = "Hello, this is a voice preview."
        if self.model_combo.currentText():
            original_text = self.tts_text_input.text()
            self.tts_text_input.setText(sample_text)
            self.start_process()
            self.tts_text_input.setText(original_text)

    def start_process(self):
        self.was_stopped = False
        mode = self.mode_slider.value()
        cmd_str = ""
        
        if mode == 1:  # Piper TTS
            text = self.tts_text_input.text().strip()
            text = processor(text)
            model = self.model_combo.currentText()
            if not text or not model or not Path(self.piper_path, model).exists():
                return self.update_status("Error: TTS text/model invalid", True)
            
            quoted_text = shlex.quote(text)
            quoted_model_path = shlex.quote(os.path.join(self.piper_path, model))
            
            speaker_id = self.speaker_combo.currentData()
            speaker_arg = f"--speaker {int(speaker_id)} " if self.is_multi_speaker(model) and speaker_id is not None else ""
            
            adv_args = (f"--sentence-silence {self.silence_spin.value()} "
                       f"--length-scale {self.length_spin.value()} "
                       f"--noise-scale {self.noise_scale_spin.value()} "
                       f"--noise-w {self.noise_w_spin.value()} ")

            # Map slider 0-100 to pacat volume 0-65536
            volume_level = int((self.volume_slider.value() / 100.0) * 65536)
            volume_arg = f"--volume={volume_level}"
            
            cmd_str = (f"set -o pipefail; echo {quoted_text} | /usr/bin/python3 -m piper "
                      f"--model {quoted_model_path} {speaker_arg}{adv_args}"
                      f"--output-raw | pacat --rate=22050 --format=s16le --channels=1 {volume_arg}")
        elif mode == 0:  # Custom
            cmd_str = self.custom_cmd_input.text().strip()
        elif mode == 2:  # Ping
            cmd_str = "ping -c 4 127.0.0.1"
        elif mode == 3:  # Echo
            cmd_str = "echo 'Hello from QProcess!'"
        
        if not cmd_str:
            return
        
        if self.tray_icon.isVisible():
            mode_names = {0: 'Custom Command', 1: 'Piper TTS', 2: 'Ping Test', 3: 'Echo Test'}
            title = mode_names.get(mode, 'Process') + " Started"
            message = "The requested task is now running."

            if mode == 1:
                text = self.tts_text_input.text().strip()
                if text == "Hello, this is a voice preview.":
                    title = "Voice Preview"
                    message = "Playing a sample of the selected voice."
                else:
                    title = "Text-to-Speech Started"
                    message = f"Reading: '{text[:40].strip()}...'"
            
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 2500)
        
        self.log_message(f"[CMD] {cmd_str}")
        self.update_status("Running...", False, "running")
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        if sys.platform != "win32":
            self.pause_btn.setEnabled(True)
            self.is_paused = False
            self.pause_btn.setText("⏸ Pause")
        self.proc.start("setsid", ["bash", "-c", cmd_str])

    def stop_process(self):
        if self.proc.state() != QProcess.ProcessState.Running:
            return
        self.was_stopped = True
        self.log_message("[INFO] Stop initiated.", "orange")
        self.update_status("Stopping...", False, "running")
        
        if sys.platform != "win32" and self.proc.processId() is not None:
            try:
                os.killpg(os.getpgid(self.proc.processId()), signal.SIGTERM)
            except (ProcessLookupError, PermissionError) as e:
                self.log_message(f"[WARN] Could not kill process group: {e}", "orange")
                self.proc.terminate()
        else:
            self.proc.terminate()

    def toggle_pause_process(self):
        if self.proc.state() != QProcess.ProcessState.Running or sys.platform == "win32":
            return
        
        try:
            pgid = os.getpgid(self.proc.processId())
            if not self.is_paused:
                os.killpg(pgid, signal.SIGSTOP)
                self.is_paused = True
                self.pause_btn.setText("▶ Resume")
                self.update_status("Paused", False, "running")
                self.log_message("[INFO] Process paused.", "orange")
            else:
                os.killpg(pgid, signal.SIGCONT)
                self.is_paused = False
                self.pause_btn.setText("⏸ Pause")
                self.update_status("Running...", False, "running")
                self.log_message("[INFO] Process resumed.", "orange")
        except (ProcessLookupError, PermissionError) as e:
            self.log_message(f"[ERROR] Could not toggle pause: {e}", "red")

    def on_process_finished(self, code: int, status: QProcess.ExitStatus):
        msg = "Stopped by user" if self.was_stopped else f"Completed (code {code})"
        is_err = status != QProcess.ExitStatus.NormalExit or (code != 0 and not self.was_stopped)
        
        if self.tray_icon.isVisible():
            if self.was_stopped:
                title, message, icon = "Process Stopped", "The task was manually stopped by the user.", QSystemTrayIcon.Warning
                self.tray_icon.showMessage(title, message, icon, 3000)
            elif is_err:
                title, message, icon = "Process Error", "The task failed to complete.", QSystemTrayIcon.Warning
                self.tray_icon.showMessage(title, message, icon, 3000)
            elif not self.isVisible():
                title, message, icon = "Process Finished", "Task completed successfully.", QSystemTrayIcon.Information
                self.tray_icon.showMessage(title, message, icon, 3000)

        status_type = "error" if is_err else "ready"
        self.update_status(msg, is_err, status_type)
        self.log_message(f"[INFO] {msg}", "red" if is_err else "green")
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if sys.platform != "win32":
            self.pause_btn.setEnabled(False)
            self.is_paused = False
            self.pause_btn.setText("⏸ Pause")

    def log_message(self, message: str, color: str = "white"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_view.append(f'<span style="color: #888;">{timestamp}</span> <span style="color: {color};">{message}</span>')

    def update_status(self, text: str, is_error: bool = False, status_type: str = "ready"):
        self.status_label.setText(text)
        self.status_label.setProperty("status", status_type)
        self.status_label.setStyle(self.status_label.style())

    def update_ui_mode(self, value: int):
        self.stacked_widget.setCurrentIndex(value)
        mode_names = {0: 'Custom', 1: 'Piper TTS', 2: 'Ping', 3: 'Echo'}
        self.mode_name_label.setText(mode_names.get(value, 'Unknown'))

    def update_volume_icon(self, value: int):
        if value == 0:
            self.volume_icon.setText("🔇")
        elif value <= 50:
            self.volume_icon.setText("🔉")
        else:
            self.volume_icon.setText("🔊")

    def select_piper_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Piper Models Directory", self.piper_path)
        if path and os.path.isdir(path):
            self.piper_path = path
            self.log_message(f"[INFO] Piper path set to: {self.piper_path}")
            self.scan_piper_models()

    def scan_piper_models(self):
        self.log_message(f"[INFO] Scanning '{self.piper_path}'...")
        current_model = self.model_combo.currentText()
        self.model_combo.clear()
        
        try:
            if not os.path.isdir(self.piper_path):
                raise FileNotFoundError(f"Piper dir not found: {self.piper_path}")
            
            models = sorted([f for f in os.listdir(self.piper_path) if f.endswith(".onnx")])
            self.model_combo.addItems(models)
            
            if current_model in models:
                self.model_combo.setCurrentText(current_model)
        except Exception as e:
            self.log_message(f"[ERROR] {e}", "red")
        
        self.load_model_config(self.model_combo.currentText())

    def load_model_config(self, model_file: str):
        current_speaker = self.speaker_combo.currentData()
        self.speaker_combo.clear()
        self.speaker_combo.setEnabled(False)
        
        if not model_file:
            self.speaker_combo.addItem("Default (ID: 0)", 0)
            return
        
        try:
            with open(os.path.join(self.piper_path, model_file + ".json")) as f:
                config = json.load(f)
            
            speaker_map = config.get('speaker_id_map', {})
            if speaker_map and len(speaker_map) > 1:
                for name, sid in sorted(speaker_map.items()):
                    self.speaker_combo.addItem(f"{name} (ID:{sid})", sid)
                
                idx = self.speaker_combo.findData(current_speaker)
                if idx != -1:
                    self.speaker_combo.setCurrentIndex(idx)
                
                self.speaker_combo.setEnabled(True)
                return
        except Exception:
            pass
        
        self.speaker_combo.addItem("Default (ID: 0)", 0)

    def is_multi_speaker(self, model_file: str):
        return self.speaker_combo.count() > 1 and self.speaker_combo.isEnabled()

    def on_hotkey_press(self, key: keyboard.Key):
        now = time.time()
        if key == keyboard.Key.shift_l:
            if now - self.last_lshift_press_time < 0.4:
                self.hotkeys_enabled = not self.hotkeys_enabled
                self.hotkey_status_signal.emit(self.hotkeys_enabled)
            self.last_lshift_press_time = now
        elif self.hotkeys_enabled and key == keyboard.Key.esc:
            if now - self.last_esc_press_time < 0.4:
                self.quit_application_signal.emit()
            else:
                self.stop_process_signal.emit()
            self.last_esc_press_time = now
        elif self.hotkeys_enabled and key == keyboard.Key.shift_r and sys.platform == "linux":
            try:
                text = subprocess.run(['xsel', '-o'], capture_output=True, text=True, check=True, timeout=1).stdout.strip()
                if text:
                    self.speak_selection_signal.emit(text)
            except Exception as e:
                self.log_signal.emit(f"[ERROR] Hotkey failed: {e}", "red")

    def on_hotkey_toggle(self, enabled: bool):
        status = "active" if enabled else "inactive"
        text = f"Hotkeys: {'ON' if enabled else 'OFF'}"
        self.hotkey_label.setText(text)
        self.hotkey_label.setProperty("hotkey", status)
        self.hotkey_label.setStyle(self.hotkey_label.style())
        
        self.log_message(f"[INFO] {text}", '#32CD32' if enabled else 'grey')
        
        if self.tray_icon.isVisible():
            title = "Hotkeys Activated" if enabled else "Hotkeys Deactivated"
            message = f"Global hotkeys are now {'ON' if enabled else 'OFF'}."
            icon = QSystemTrayIcon.Information
            self.tray_icon.showMessage(title, message, icon, 2000)

    def on_speak_selection(self, text: str):
        self.mode_slider.setValue(1)
        self.tts_text_input.setText(text)
        self.start_process()

    def toggle_always_on_top(self, checked: bool):
        flags = self.windowFlags()
        if checked:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        
        self.opacity_slider.setVisible(checked)
        self.update_opacity()
        self.show()

    def update_opacity(self, _=None):
        opacity = 1.0
        
        if self.always_on_top_cb.isChecked():
            is_slider_pressed = self.opacity_slider.isSliderDown()
            
            if not self.isActiveWindow() or is_slider_pressed:
                opacity = self.opacity_slider.value() / 100.0
        
        self.setWindowOpacity(opacity)

    def focusInEvent(self, e: QFocusEvent):
        super().focusInEvent(e)
        self.update_opacity()

    def focusOutEvent(self, e: QFocusEvent):
        super().focusOutEvent(e)
        self.update_opacity()

    def save_settings(self):
        settings: dict[str, typing.Any] = {
            'piper_path': self.piper_path,
            'custom_cmd': self.custom_cmd_input.text(),
            'tts_text': self.tts_text_input.text(),
            'on_top': self.always_on_top_cb.isChecked(),
            'transparency': self.opacity_slider.value(),
            'volume': self.volume_slider.value(),
            'silence': self.silence_spin.value(),
            'length': self.length_spin.value(),
            'noise_s': self.noise_scale_spin.value(),
            'noise_w': self.noise_w_spin.value(),
            'mode': self.mode_slider.value(),
            'model': self.model_combo.currentText(),
            'speaker': self.speaker_combo.currentData(),
            'geometry': self.saveGeometry().toBase64().data().decode()
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=2)

    def load_settings(self):
        try:
            with open(CONFIG_FILE) as f:
                s: dict[str, typing.Any] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            s = {}
        
        self.piper_path = s.get('piper_path', self.piper_path)
        self.custom_cmd_input.setText(s.get('custom_cmd', "echo 'Hello!'"))
        self.tts_text_input.setText(s.get('tts_text', "Hello from Piper."))
        self.always_on_top_cb.setChecked(s.get('on_top', False))
        self.opacity_slider.setValue(s.get('transparency', 100))
        self.volume_slider.setValue(s.get('volume', 75))
        self.silence_spin.setValue(s.get('silence', 0.0))
        self.length_spin.setValue(s.get('length', 1.0))
        self.noise_scale_spin.setValue(s.get('noise_s', 0.667))
        self.noise_w_spin.setValue(s.get('noise_w', 0.8))
        self.mode_slider.setValue(s.get('mode', 1))

        if 'geometry' in s:
            try:
                self.restoreGeometry(QByteArray.fromBase64(s['geometry'].encode()))
            except Exception as e:
                self.log_message(f"[WARN] Could not restore window geometry: {e}", "orange")

        self.scan_piper_models()
        
        saved_model = s.get('model')
        if saved_model:
            index = self.model_combo.findText(saved_model)
            if index != -1:
                self.model_combo.setCurrentIndex(index)
        
        saved_speaker_id = s.get('speaker')
        if saved_speaker_id is not None:
            index = self.speaker_combo.findData(saved_speaker_id)
            if index != -1:
                self.speaker_combo.setCurrentIndex(index)
        
        self.log_message("[INFO] Settings loaded.")

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Handle window close event."""
        if self.is_quitting:
            self.save_settings()
            if self.listener:
                try:
                    self.listener.stop()
                except Exception as e:
                    self.log_message(f"[WARN] Could not stop listener: {e}", "orange")
            self.proc.kill()
            event.accept()
        else:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "CompactApp is running",
                "Application minimized to system tray.",
                QSystemTrayIcon.Information,
                2000
            )

    def quit_application(self):
        """Prepare for and initiate application exit."""
        self.log_message("[INFO] Quitting application...", "orange")
        self.is_quitting = True
        self.close()

class TextProcessorEngine:
    def __init__(self, rules_file_path: str = 'rules_definitions.json'):
        self.rules = self._load_rules(rules_file_path)

    def _load_rules(self, rules_file_path: str) -> dict:
        with open(rules_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def __call__(self, text: str) -> str:
        processed_text = text
        processed_text = self._apply_block_replacements(processed_text)
        processed_text = self._apply_regex_patterns_replacements(processed_text)  # Move regex first
        processed_text = self._normalize_newlines(processed_text)  # Then normalize
        processed_text = self._apply_string_replacements(processed_text)
        processed_text = self._apply_character_replacements(processed_text)
        return processed_text
        
    def _normalize_newlines(self, text: str) -> str:
        # 1. Normalize all newlines to Unix style
        text = text.replace('\r\n', '\n')

        # 2. Replace single newlines with a space, preserving paragraph breaks (double newlines)
        # This regex replaces a newline that is NOT followed by another newline.
        # It effectively turns soft wraps into spaces.
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

        # 3. Collapse multiple newlines into exactly two newlines (paragraph breaks)
        text = re.sub(r'\n{2,}', '\n\n', text)
        return text

    def _apply_block_replacements(self, text: str) -> str:
        # Block replacements are for removing or isolating large sections.
        # Each rule is [start_delimiter, end_delimiter, replacement].
        # We use regex to find and replace content between the delimiters.
        for start_delim, end_delim, replacement in self.rules.get('block_replacements', []):
            if start_delim and end_delim is not None:
                # Construct a regex to match the block including delimiters
                # re.escape() is used to treat delimiters as literal strings
                # [\s\S]*? matches any character (including newline) non-greedily
                pattern = re.escape(start_delim) + r'[\s\S]*?' + re.escape(end_delim)
                text = re.sub(pattern, replacement, text)
        return text

    def _apply_regex_patterns_replacements(self, text: str) -> str:
        for pattern, replacement in self.rules.get('regex_patterns_replacements', []):
            if pattern: # Ensure pattern is not empty
                text = re.sub(pattern, replacement, text)
        return text

    def _apply_string_replacements(self, text: str) -> str:
        # String replacements are for simple string-to-string transformations.
        # It's important to apply these carefully to avoid unintended side effects
        # if one replacement is a substring of another.
        # For now, a simple replace is used. Order might matter for some rules.
        for old, new in self.rules.get('string_replacements', []):
            if old and new is not None: # Ensure old is not empty and new is defined
                text = text.replace(old, new)
        return text

    def _apply_character_replacements(self, text: str) -> str:
        # Character replacements are for single character transformations.
        # The design document mentions "removing any remaining individual characters".
        # This implies a mapping from a set of characters to an empty string or another character.
        # The current rules_definitions.json example shows a single rule for this.
        # We'll iterate through the characters in the 'old' string and replace them with 'new'.
        for old_chars, new_char in self.rules.get('character_replacements', []):
            if old_chars and new_char is not None: # Ensure old_chars is not empty and new_char is defined
                for char in old_chars:
                    text = text.replace(char, new_char)
        return text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if "Fusion" in QStyleFactory.keys():
        app.setStyle(QStyleFactory.create("Fusion"))
    
    window = CompactApp()
    processor = TextProcessorEngine(rules_file_path=os.path.join(os.path.dirname(__file__), 'rules_definitions.json'))

    window.show()
    sys.exit(app.exec_())
