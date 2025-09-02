import os
import sys
import signal
from PyQt5.QtCore import QObject, QProcess, pyqtSignal

class ProcessManager(QObject):
    process_finished = pyqtSignal(int, QProcess.ExitStatus, bool)
    log_message = pyqtSignal(str, str)
    status_update = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.proc = QProcess(self)
        self.was_stopped = False
        self.is_paused = False

        self.proc.readyReadStandardOutput.connect(self._handle_stdout)
        self.proc.readyReadStandardError.connect(self._handle_stderr)
        self.proc.finished.connect(self._on_process_finished)

    def _handle_stdout(self):
        message = self.proc.readAllStandardOutput().data().decode(errors='ignore').strip()
        if message:
            self.log_message.emit(message, 'white')

    def _handle_stderr(self):
        message = f"[ERROR] {self.proc.readAllStandardError().data().decode(errors='ignore').strip()}"
        if message:
            self.log_message.emit(message, 'red')

    def start(self, command: str):
        if not command:
            return

        self.was_stopped = False
        self.log_message.emit(f"[CMD] {command}", "white")
        self.status_update.emit("Running...", "running")

        # Using 'setsid' ensures that the process and its children are in their own process group,
        # which allows us to terminate them all at once.
        self.proc.start("setsid", ["bash", "-c", command])

    def stop(self):
        if self.proc.state() != QProcess.ProcessState.Running:
            return
        self.was_stopped = True
        self.log_message.emit("[INFO] Stop initiated.", "orange")
        self.status_update.emit("Stopping...", "running")

        if sys.platform != "win32" and self.proc.processId() is not None:
            try:
                os.killpg(os.getpgid(self.proc.processId()), signal.SIGTERM)
            except (ProcessLookupError, PermissionError) as e:
                self.log_message.emit(f"[WARN] Could not kill process group: {e}", "orange")
                self.proc.terminate()
        else:
            self.proc.terminate()

    def toggle_pause(self):
        if self.proc.state() != QProcess.ProcessState.Running or sys.platform == "win32":
            return

        try:
            pgid = os.getpgid(self.proc.processId())
            if not self.is_paused:
                os.killpg(pgid, signal.SIGSTOP)
                self.is_paused = True
                self.status_update.emit("Paused", "running")
                self.log_message.emit("[INFO] Process paused.", "orange")
            else:
                os.killpg(pgid, signal.SIGCONT)
                self.is_paused = False
                self.status_update.emit("Running...", "running")
                self.log_message.emit("[INFO] Process resumed.", "orange")
        except (ProcessLookupError, PermissionError) as e:
            self.log_message.emit(f"[ERROR] Could not toggle pause: {e}", "red")

    def _on_process_finished(self, code: int, status: QProcess.ExitStatus):
        self.is_paused = False
        self.process_finished.emit(code, status, self.was_stopped)

    def kill(self):
        """Kills the process immediately."""
        self.proc.kill()
