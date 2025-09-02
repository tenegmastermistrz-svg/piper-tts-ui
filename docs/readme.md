# CompactApp • Multi-Tool Runner

CompactApp is a versatile desktop utility for Linux, designed to provide a clean graphical interface for various command-line tools. Its primary feature is a powerful front-end for the [Piper text-to-speech (TTS) engine](https://github.com/rhasspy/piper), but it can also be used to run custom shell commands.

![App Screenshot](https://i.imgur.com/your-screenshot.png) <!-- placeholder -->

## Key Features

- **Multiple Execution Modes**:
    - **Piper TTS**: A comprehensive GUI for Piper, allowing for voice model selection, speaker selection (for multi-speaker models), and fine-tuning of voice characteristics.
    - **Custom Command**: Run any shell command directly from the app.
    - **Ping & Echo**: Simple modes for testing connectivity and process execution.
- **Advanced Text Processing**: An integrated text processing engine cleans up input text before sending it to the TTS engine. It uses customizable rule sets to remove unwanted characters, formatting, and artifacts from sources like e-books or chatbot conversations.
- **Modern User Interface**:
    - A sleek, dark-themed UI built with PyQt5.
    - "Always on Top" mode with adjustable opacity for seamless integration into your workflow.
    - System tray icon for easy access and notifications.
- **Global Hotkeys**:
    - Activate/deactivate hotkeys with a double-press of `Left Shift`.
    - Speak selected text from any application with `Right Shift`.
    - Stop the current task or quit the app with `Escape`.
- **Persistent Configuration**: Your settings, including the last-used text, voice model, and window position, are saved and restored automatically.

## Getting Started

### Prerequisites

- Python 3
- PyQt5
- pynput (for hotkeys)
- Piper TTS (and its dependencies)
- `xsel` (for the "Speak Selection" hotkey on Linux)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/CompactApp.git
    cd CompactApp
    ```

2.  **Install dependencies:**
    ```bash
    pip install PyQt5 pynput
    ```

3.  **Set up Piper:**
    Follow the official [Piper installation instructions](https://github.com/rhasspy/piper). You will also need to download voice models.

### Running the Application

1.  Launch the application:
    ```bash
    python3 piperui.py
    ```

2.  **Configure Piper Path**:
    - The first time you run the app, go to `Voice & Advanced Settings`.
    - Click "Set Path" and select the directory where you have downloaded your Piper voice models (`.onnx` files).
    - The app will automatically scan this directory for available voices.

3.  **Enjoy!**
    - Select a voice, type some text, and click "Execute".

## How to Use

- **Switch Modes**: Use the slider at the top to switch between Piper TTS, Custom Command, and other modes.
- **Speak Text**: In Piper TTS mode, type your text in the input box and click "Execute".
- **Use Hotkeys**: Double-press `Left Shift` to turn on hotkeys. Then, select text anywhere on your screen and press `Right Shift` to have it spoken.
- **Minimize to Tray**: Close the main window to minimize it to the system tray. Right-click the tray icon to show the window or exit the application.

## Customization

The text processing engine uses rules from `rules_definitions.json`. You can edit this file to change how text is cleaned. For example, you can add new character replacements or regex patterns to suit your needs.
