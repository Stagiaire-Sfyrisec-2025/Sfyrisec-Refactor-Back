import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_tool(command: list[str], file_path: str) -> tuple[str, str]:
    try:
        logger.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        logger.error(f"Tool execution failed: {e.stderr}")
        raise Exception(f"Tool execution failed: {e.stderr}")