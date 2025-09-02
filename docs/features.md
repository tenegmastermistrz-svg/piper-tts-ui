# Application Features

This document provides a comprehensive overview of the features of the CompactApp multi-tool runner.

## Core Functionality

The application is a versatile utility that provides a graphical user interface for various command-line tools. It is built with PyQt5 and features a modern, themeable UI.

## Execution Modes

The application can be switched between several modes using a slider in the main window.

### 1. Piper TTS Mode

This is the primary mode of the application. It provides a user-friendly interface for the [Piper text-to-speech engine](https://github.com/rhasspy/piper).

- **Text Input**: Users can type text directly into an input field or use the "Speak Selection" hotkey to read selected text from other applications.
- **Voice Model Selection**: The application can scan a directory for available Piper voice models (`.onnx` files) and allows the user to choose one from a dropdown menu.
- **Multi-speaker Models**: If a model supports multiple speakers (detected from its `.json` config file), a second dropdown is enabled to select a specific speaker.
- **Voice Preview**: A "Play Sample" button allows users to hear a preview of the selected voice.
- **Advanced Voice Tuning**: Users can fine-tune the voice output with sliders and spinboxes for:
    - Sentence Silence
    - Length Scale
    - Noise Scale
    - Noise W
- **Volume Control**: A dedicated slider controls the output volume of the TTS engine.

### 2. Custom Command Mode

This mode provides a simple input field where the user can enter any shell command to be executed. This allows for great flexibility in running scripts or other command-line tools.

### 3. Ping Mode

A simple diagnostic mode that runs `ping -c 4 127.0.0.1` to test local network connectivity.

### 4. Echo Mode

A basic test mode that runs `echo 'Hello from QProcess!'` to verify that the process execution engine is working correctly.

## Text Processing Engine

Before being spoken by the TTS engine, the input text is passed through a `TextProcessorEngine`. This engine cleans and normalizes the text based on a set of rules loaded from a JSON file.

- **Rule-Based Processing**: The engine applies several types of rules in a specific order:
    1. **Block Replacements**: Removes or replaces entire blocks of text between specified delimiters.
    2. **Regex Pattern Replacements**: Applies regular expression substitutions.
    3. **Newline Normalization**: Converts different newline formats into a consistent style and replaces single newlines with spaces to join lines.
    4. **String Replacements**: Performs simple string-for-string replacements.
    5. **Character Replacements**: Replaces individual characters.
- **Customizable Rule Sets**: The application comes with two predefined rule sets:
    - `rules_definitions.json`: Optimized for cleaning up text from e-books.
    - `chatbot_rules_definitions.json`: Designed to remove markdown, special characters, and other artifacts from chatbot responses.
    - *Note: The application currently only loads `rules_definitions.json` by default.*

## User Interface and Experience

- **Modern UI**: The application features a custom dark theme with a clean and intuitive layout.
- **Always on Top**: A checkbox allows the main window to stay on top of all other windows.
- **Opacity Control**: When "Always on Top" is enabled, an opacity slider appears, allowing the window to become transparent when it's not in focus.
- **System Tray Integration**:
    - The application can be minimized to the system tray.
    - A context menu on the tray icon allows showing/hiding the window and exiting the application.
    - Desktop notifications are used to provide feedback on process status (started, stopped, finished, error).
- **Process Control**:
    - **Execute**: Starts the command for the currently selected mode.
    - **Stop**: Terminates the running process.
    - **Pause/Resume**: Can pause and resume the running process (not available on Windows).
- **Log Viewer**: A text area at the bottom of the window displays timestamped logs of application events and command output.
- **Persistent Settings**: The application saves all user settings (selected mode, voice, tuning parameters, window geometry, etc.) to a JSON file and restores them on the next launch.

## Hotkeys

The application supports global hotkeys for quick actions (requires the `pynput` library).

- **Toggle Hotkeys**: Double-press the **Left Shift** key to enable or disable all hotkeys.
- **Speak Selection**: Press **Right Shift** to automatically copy the currently selected text, switch to Piper TTS mode, and speak the text (Linux only, uses `xsel`).
- **Stop Process**: Press **Escape** once to stop the currently running process.
- **Quit Application**: Double-press the **Escape** key to quit the application.
