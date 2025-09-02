import os
import json
import typing
from pathlib import Path

class SettingsManager:
    def __init__(self, app_name: str = "CompactApp"):
        self.config_dir = Path(os.path.expanduser("~")) / ".config" / app_name
        self.config_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_settings(self, settings: dict[str, typing.Any]):
        """Saves the given settings dictionary to the config file."""
        with open(self.config_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def load_settings(self) -> dict[str, typing.Any]:
        """Loads the settings from the config file and returns them as a dictionary."""
        try:
            with open(self.config_file) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
