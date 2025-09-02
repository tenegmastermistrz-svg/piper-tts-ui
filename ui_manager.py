import os
import json
from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QPushButton, QLabel, QSlider, QHBoxLayout, QLineEdit, QGroupBox, QFormLayout, QComboBox, QDoubleSpinBox, QCheckBox, QTextEdit, QStackedWidget, QSpacerItem, QSizePolicy, QFileDialog)
from PyQt5.QtCore import Qt

class UIManager:
    def __init__(self, main_window):
        self.main_window = main_window
        main_window.setStyleSheet(self._get_modern_stylesheet())
        self._setup_ui()

    def _get_modern_stylesheet(self):
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

    def _setup_ui(self):
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
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

        # Rule selection
        self.rule_combo = QComboBox()
        piper_form.addRow("Rule Set", self.rule_combo)

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

        self.main_window.resize(520, 680)
        self.scan_and_populate_rule_sets()

    def scan_and_populate_rule_sets(self):
        self.main_window.log_message("[INFO] Scanning for rule sets...")
        self.rule_combo.clear()
        rules_dir = "txt_eng_rules"
        try:
            if not os.path.isdir(rules_dir):
                self.main_window.log_message(f"[WARN] Rules directory not found: {rules_dir}", "orange")
                return

            rule_files = sorted([f for f in os.listdir(rules_dir) if f.endswith(".json")])
            self.rule_combo.addItems(rule_files)
            self.main_window.log_message(f"Found rule sets: {rule_files}", "green")

        except Exception as e:
            self.main_window.log_message(f"[ERROR] Failed to scan for rule sets: {e}", "red")

    def select_piper_path(self):
        path = QFileDialog.getExistingDirectory(self.main_window, "Select Piper Models Directory", self.main_window.piper_path)
        if path and os.path.isdir(path):
            self.main_window.piper_path = path
            self.main_window.log_message(f"[INFO] Piper path set to: {self.main_window.piper_path}")
            self.scan_piper_models()

    def scan_piper_models(self):
        self.main_window.log_message(f"[INFO] Scanning '{self.main_window.piper_path}'...")
        current_model = self.model_combo.currentText()
        self.model_combo.clear()

        try:
            if not os.path.isdir(self.main_window.piper_path):
                raise FileNotFoundError(f"Piper dir not found: {self.main_window.piper_path}")

            models = sorted([f for f in os.listdir(self.main_window.piper_path) if f.endswith(".onnx")])
            self.model_combo.addItems(models)

            if current_model in models:
                self.model_combo.setCurrentText(current_model)
        except Exception as e:
            self.main_window.log_message(f"[ERROR] {e}", "red")

        self.load_model_config(self.model_combo.currentText())

    def load_model_config(self, model_file: str):
        current_speaker = self.speaker_combo.currentData()
        self.speaker_combo.clear()
        self.speaker_combo.setEnabled(False)

        if not model_file:
            self.speaker_combo.addItem("Default (ID: 0)", 0)
            return

        try:
            with open(os.path.join(self.main_window.piper_path, model_file + ".json")) as f:
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
