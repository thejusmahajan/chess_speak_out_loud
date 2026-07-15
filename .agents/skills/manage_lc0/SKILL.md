---
name: manage_lc0
description: Skill for downloading, verifying, or updating the Leela Chess Zero (LC0) binary and network weights.
---

# Managing LC0

This project relies on the LC0 binary and neural network weights being present in the `engine/` directory.

## Current Setup
- **Directory**: `engine/`
- **Binary Name**: `lc0.exe`
- **Network Name**: Typically `192x15_network` (or similar depending on the version downloaded).

## How to Install or Update
If the user asks you to "update LC0" or "install the engine":

1. There is an existing script named `setup_engine.bat` in the `scratch/` folder.
2. DO NOT try to write your own `curl` or `wget` commands. 
3. Run the batch script: `.\scratch\setup_engine.bat` from the `C:\Users\Admin\Documents\chess_speak_out_loud` directory.
4. Verify the installation by checking if `engine/lc0.exe` exists.

## Troubleshooting
If the engine fails to start in Python (e.g., in `backend/engine_manager.py`), verify:
1. `lc0.exe` exists in `engine/`.
2. The network file exists in `engine/` or its subdirectories.
3. The paths are absolute when passed to Python `subprocess.Popen`.
