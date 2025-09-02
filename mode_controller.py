import os
import shlex
from pathlib import Path

class ModeController:
    def __init__(self, text_processor):
        self.text_processor = text_processor

    def create_command(self, mode: int, ui_state: dict) -> str:
        cmd_str = ""
        if mode == 1:  # Piper TTS
            cmd_str = self._create_piper_command(ui_state)
        elif mode == 0:  # Custom
            cmd_str = ui_state.get('custom_cmd', '').strip()
        elif mode == 2:  # Ping
            cmd_str = "ping -c 4 127.0.0.1"
        elif mode == 3:  # Echo
            cmd_str = "echo 'Hello from QProcess!'"
        return cmd_str

    def _create_piper_command(self, ui_state: dict) -> str:
        text = ui_state.get('tts_text', '').strip()
        text = self.text_processor(text)
        model = ui_state.get('model')
        piper_path = ui_state.get('piper_path')

        if not text or not model or not Path(piper_path, model).exists():
            return ""

        quoted_text = shlex.quote(text)
        quoted_model_path = shlex.quote(os.path.join(piper_path, model))

        speaker_id = ui_state.get('speaker_id')
        speaker_arg = f"--speaker {int(speaker_id)} " if ui_state.get('is_multi_speaker') and speaker_id is not None else ""

        adv_args = (f"--sentence-silence {ui_state.get('silence', 0.0)} "
                   f"--length-scale {ui_state.get('length', 1.0)} "
                   f"--noise-scale {ui_state.get('noise_s', 0.667)} "
                   f"--noise-w {ui_state.get('noise_w', 0.8)} ")

        volume_level = int((ui_state.get('volume', 75) / 100.0) * 65536)
        volume_arg = f"--volume={volume_level}"

        cmd_str = (f"set -o pipefail; echo {quoted_text} | /usr/bin/python3 -m piper "
                  f"--model {quoted_model_path} {speaker_arg}{adv_args}"
                  f"--output-raw | pacat --rate=22050 --format=s16le --channels=1 {volume_arg}")

        return cmd_str
