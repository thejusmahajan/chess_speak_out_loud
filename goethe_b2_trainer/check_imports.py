import sys
import traceback

log_file = "c:/Users/Admin/Documents/chess_speak_out_loud/goethe_b2_trainer/startup_error.log"

try:
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Testing imports...\n")
        try:
            import uvicorn
            f.write("uvicorn OK\n")
        except Exception as e:
            f.write(f"uvicorn FAILED: {e}\n")
            
        try:
            import app
            f.write("app import OK\n")
        except Exception as e:
            f.write(f"app import FAILED:\n{traceback.format_exc()}\n")
except Exception as e:
    pass
