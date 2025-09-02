from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QStyle
from PyQt5.QtCore import QObject

class TrayManager(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.tray_icon = QSystemTrayIcon(main_window)
        self._setup_tray_icon()

    def _setup_tray_icon(self):
        """Sets up the system tray icon and its context menu."""
        self.tray_icon.setIcon(self.main_window.style().standardIcon(QStyle.SP_ComputerIcon))
        menu = QMenu()
        toggle_action = menu.addAction("Show / Hide")
        toggle_action.triggered.connect(self._toggle_visibility)
        menu.addSeparator()
        menu.addAction("Exit", self.main_window.quit_application)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_icon_activated)
        self.tray_icon.show()

    def _toggle_visibility(self):
        """Toggles the main window's visibility."""
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
            self.main_window.activateWindow()

    def _on_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Handles tray icon activation to toggle window visibility on left-click."""
        if reason == QSystemTrayIcon.Trigger:  # Standard left-click
            self._toggle_visibility()

    def showMessage(self, title, message, icon=QSystemTrayIcon.Information, msecs=2000):
        """Displays a message from the tray icon."""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, msecs)
