# caseMonster

## Project Overview
caseMonster is a desktop utility that automates common text case conversions. The tool provides a simple GUI for converting selected text to upper case, lower case, title case, or a sentence-style format that capitalizes the beginning of sentences and special cases like the standalone pronoun "I". Behind the scenes the application uses clipboard automation to capture the currently selected text from another window, transform it, and paste the result back for you.

## Prerequisites
- **Operating system:** Windows (the automation relies on Windows-specific window switching and the Help menu opens a Windows-only `start` command).
- **Python:** 3.9 or later.
- **Dependencies:** See the [`requirements.txt`](./requirements.txt) file for the exact package versions used during testing.

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/caseMonster.git
   cd caseMonster
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### Launching the GUI
Run the application from the repository root:
```bash
python window.py
```
This opens the **WarpTyme - CASEmonster** window containing buttons for each case conversion. The window now defaults to an "always on top" floating style so you can keep it handy above other applications. Use the gear-shaped **Settings** button to toggle this behaviour, hide the main window, or access the Windows Explorer integration helpers described below.

### Typical Workflow
1. Highlight the text you want to convert in another application.
2. Either click one of the buttons in the floating window *or* right-click the caseMonster tray icon to access the same conversions:
   - **Upper** – converts the text to upper case.
   - **Lower** – converts the text to lower case.
   - **Title** – converts the text to title case.
   - **Sentence** – applies the custom `funky` sentence-style capitalization.
3. The selected action triggers clipboard automation:
   - The app automatically `Alt+Tab`s to the previous window.
   - It copies the selected text (`Ctrl+C`), transforms it, and pastes the result (`Ctrl+V`).
   - A short delay is built in to keep the automation reliable.

### Tray icon quick actions
When the application launches it now also creates a system tray icon (Windows taskbar notification area). Right-click the icon to:

- Run any of the four conversions without opening the main window.
- Show or hide the floating window.
- Toggle the "Always on top" preference.
- Exit the application.

You can also left-click the icon to bring the window back to the foreground if you've hidden it.

### Keyboard Shortcuts & Automation
You do not need to press additional shortcuts beyond the button click. The application issues the following shortcuts on your behalf:
- `Alt+Tab` to return to the previously active window.
- `Ctrl+C` to copy the selection.
- `Ctrl+V` to paste the transformed text.

The Help → "How to use" menu item opens the bundled [`help.txt`](./help.txt) guide in your default browser for a quick refresher on the buttons and automation workflow. If the file is missing, the app now shows an in-window message that explains how to restore it.

### Command-line conversions
The automation helpers are also exposed via a small CLI in `main.py`. Examples:

```bash
# Copy text to your clipboard, then convert it to Title Case in place
python main.py --convert title

# Convert a file to sentence case and overwrite it in-place
python main.py --convert sentence --target path/to/file.txt --in-place

# Print a transformed version of a file to stdout
python main.py --convert upper --target path/to/file.txt
```

### Windows Explorer context menu entries
On Windows you can register right-click Explorer entries that call the CLI shown above. Launch the GUI and open **Settings → Register Windows Explorer context menu entries** to add the commands (or remove them later). The helper writes user-level registry keys, so no administrator privileges are required, but you may need to restart Windows Explorer for the menu entries to appear.

## Development Notes
- `main.py` contains the case-conversion logic and the clipboard automation routines shared by the GUI.
- `window.py` defines the wxPython GUI generated with wxFormBuilder and wires button events to the functions in `main.py`.
- The logo assets (`logo.png`, `logoico.ico`) are loaded directly by the GUI, so keep them in the project root or adjust the paths if you reorganize files.
- When extending the project, prefer adding new conversion routines in `main.py` and connecting them to new buttons in `window.py`.

