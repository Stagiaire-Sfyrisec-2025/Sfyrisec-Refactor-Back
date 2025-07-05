import subprocess
import os
from utils.tool_runner import run_tool

def codeigniter_refactor(file_path: str, version: str) -> tuple[str, str]:
    try:
        config_file = f"/tools/rector/codeigniter.php"
        command = ["vendor/bin/rector", "process", file_path, "--config", config_file]
        stdout, stderr = run_tool(command, file_path)
        if stderr:
            raise Exception(f"Rector error: {stderr}")
        with open(file_path, "r") as f:
            refactored_code = f.read()
        return refactored_code, stdout
    finally:
        if os.path.exists(file_path):
            os.unlink(file_path)