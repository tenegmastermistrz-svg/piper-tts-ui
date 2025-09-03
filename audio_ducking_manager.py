import re
import subprocess

class AudioDuckingManager:
    def __init__(self, logger):
        self.logger = logger
        self.original_volumes = {}

    def _get_sink_inputs(self):
        """Gets a list of all current audio sink inputs using pactl."""
        try:
            result = subprocess.run(['pactl', 'list', 'sink-inputs'], capture_output=True, text=True, check=True)
            return result.stdout
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            self.logger(f"[ERROR] pactl command failed: {e}", "red")
            return None

    def duck_audio(self, own_pid: int):
        """Lowers the volume of all other audio streams."""
        self.logger("[INFO] Ducking audio for other applications.", "blue")
        sink_inputs_str = self._get_sink_inputs()
        if not sink_inputs_str:
            return

        self.original_volumes = {}

        # This regex is complex; it captures the sink input index, volume, and process ID.
        # It looks for blocks of text starting with "Sink Input #"
        pattern = re.compile(
            r"Sink Input #(\d+)\s*.*?Volume:.*?(\d+) /.*?\((\d+\.\d+)%\).*?unix-process-id = \"(\d+)\"",
            re.DOTALL
        )

        for match in pattern.finditer(sink_inputs_str):
            index, vol_val, vol_percent, pid = match.groups()
            index, pid = int(index), int(pid)

            # We need a way to check if 'pid' belongs to our process group.
            # For now, we'll just check against the main PID. This might need refinement.
            if pid != own_pid:
                try:
                    new_volume = int(int(vol_val) * 0.3) # 70% reduction
                    self.logger(f"Ducking sink input #{index} (PID: {pid}) from {vol_percent}% to {int(float(vol_percent) * 0.3)}%", "blue")
                    # Store the original volume percentage
                    self.original_volumes[index] = f"{vol_percent}%"
                    subprocess.run(['pactl', 'set-sink-input-volume', str(index), str(new_volume)], check=True)
                except Exception as e:
                    self.logger(f"[ERROR] Failed to duck volume for sink input #{index}: {e}", "red")

    def restore_audio(self):
        """Restores the volume of all previously ducked audio streams."""
        if not self.original_volumes:
            return

        self.logger("[INFO] Restoring audio for other applications.", "blue")
        for index, volume in self.original_volumes.items():
            try:
                self.logger(f"Restoring sink input #{index} to {volume}", "blue")
                subprocess.run(['pactl', 'set-sink-input-volume', str(index), volume], check=True)
            except Exception as e:
                self.logger(f"[ERROR] Failed to restore volume for sink input #{index}: {e}", "red")

        self.original_volumes = {}
