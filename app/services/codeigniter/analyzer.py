import subprocess
import os
import json
from utils.tool_runner import run_tool

def codeigniter_analyze(file_path: str, version: str) -> dict:
    try:
        config_file = f"/tools/phpstan/codeigniter.neon"
        command = ["vendor/bin/phpstan", "analyse", file_path, "--configuration", config_file, "--error-format=json"]
        stdout, stderr = run_tool(command, file_path)
        if stderr:
            raise Exception(f"PHPStan error: {stderr}")
        return json.loads(stdout)
    finally:
        if os.path.exists(file_path):
            os.unlink(file_path)