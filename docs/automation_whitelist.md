# 🛡️ PC Automation Whitelist & Safety Architecture

Megan automates desktop actions while maintaining strict security boundaries to prevent accidental or malicious system damage.

---

## 📜 Whitelist Principles

1. **Explicit Whitelist Only**: No command is executed unless its action name exists in `configs/automation_whitelist.yaml`.
2. **No Raw Shell Execution**: Megan does not pass user strings directly to `cmd.exe`, `powershell.exe`, or `bash`.
3. **Structured Parameter Extraction**: The intent classifier extracts strict structured arguments (e.g., `{ "action": "create_folder", "name": "Project", "path": "..." }`).

---

## 📋 Action Registry

### 📁 File Management
- `create_file`: Creates empty or pre-filled file.
- `create_folder`: Creates directory.
- `delete_file`: Moves file to Recycle Bin. **[Requires Confirmation]**
- `delete_folder`: Moves directory to Recycle Bin. **[Requires Confirmation]**
- `rename_file`: Renames file. **[Requires Confirmation]**
- `rename_folder`: Renames directory. **[Requires Confirmation]**
- `copy_file` / `move_file`: Safe copy or relocation.

### 🚀 Application Control
- `open_application`: Launches registered applications (VS Code, Chrome, Notepad, Calculator, etc.).
- `open_url_in_browser`: Opens URL in system default browser.

### 🔍 Search
- `search_files_by_name`: Finds files matching glob patterns.
- `search_files_by_extension`: Lists files of specific types (`.py`, `.pdf`, etc.).
- `search_files_by_content`: Searches for text snippets in files.

### 🎵 Media
- `play_audio_file`: Plays an audio file using system media player.
- `open_media_player`: Launches default audio player.

### 💻 Code Generation
- `write_code_to_file`: Writes generated source code directly to a file.
- `open_in_vscode`: Launches VS Code targeting a specific file or directory.

---

## ⚠️ Destructive Action Confirmation Flow

```
User Command: "Delete old_backup folder"
         │
    [Intent Classifier] -> "delete_folder"
         │
    [Whitelist Check] -> Action is allowed
         │
    [Destructive Check] -> Matches destructive list!
         │
    [Confirmation Gate]
         ├─► React UI: Pop up ConfirmationModal
         └─► CLI: [y/N] prompt
         │
    User approves?
         ├── YES ──► send2trash(path) -> "Folder deleted safely."
         └── NO  ──► Action aborted -> "Operation cancelled."
```
