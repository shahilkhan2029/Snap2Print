"""
Snap2Print - Desktop Application Launcher
Starts local FastAPI server, binds to 127.0.0.1, and launches browser.
"""
import sys
import os
import socket
import threading
import time
import webbrowser
import logging
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.config import APP_DIR, IS_FROZEN, FRONTEND_DIR, MODELS_DIR

# Set up logging directory in APP_DIR/logs
log_dir = APP_DIR / "logs"
try:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "snap2print.log"
except Exception:
    log_file = None

handlers = [logging.StreamHandler(sys.stdout)]
if log_file:
    handlers.append(logging.FileHandler(str(log_file), encoding="utf-8"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=handlers
)
logger = logging.getLogger("Snap2PrintLauncher")


def show_error_dialog(title: str, message: str):
    """Shows a native Windows error dialog box if possible, and logs the error."""
    logger.error(f"{title}: {message}")
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)  # 0x10 = MB_ICONERROR
    except Exception:
        pass


def find_available_port(host: str = "127.0.0.1", start_port: int = 8000, max_attempts: int = 50) -> int:
    """Finds an available local port on host."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    raise RuntimeError(
        f"Unable to find an available local port on {host} (checked ports {start_port} to {start_port + max_attempts})."
    )


def open_browser_delayed(url: str, host: str, port: int, timeout: float = 20.0):
    """Waits for local server to be responsive, then launches user's default browser."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                time.sleep(0.4)  # Small stabilization delay
                logger.info(f"Local server is ready. Launching browser: {url}")
                webbrowser.open(url)
                return
        except (OSError, ConnectionRefusedError):
            time.sleep(0.25)
    logger.warning(f"Server readiness check timed out. Attempting to open browser anyway: {url}")
    webbrowser.open(url)


def main():
    try:
        # Multiprocessing support for PyInstaller on Windows
        import multiprocessing
        multiprocessing.freeze_support()

        host = "127.0.0.1"
        try:
            port = find_available_port(host=host, start_port=8000)
        except Exception as e:
            show_error_dialog("Snap2Print Startup Error", f"Failed to allocate a local port:\n{e}")
            sys.exit(1)

        url = f"http://{host}:{port}"

        print("=" * 64)
        print("          Snap2Print Studio — Standalone Desktop Mode")
        print("=" * 64)
        print(f"  * Mode:       {'Packaged Executable' if IS_FROZEN else 'Development'}")
        print(f"  * Local Host: {host}")
        print(f"  * Local Port: {port}")
        print(f"  * Web URL:    {url}")
        print(f"  * Location:   {APP_DIR}")
        print("=" * 64)
        print(" Starting local server and opening your browser...")
        print(" (Keep this window open while using Snap2Print. Close to exit.)\n")

        # Import FastAPI application
        from backend.main import app
        import uvicorn

        # Start browser in background thread
        browser_thread = threading.Thread(
            target=open_browser_delayed,
            args=(url, host, port),
            daemon=True
        )
        browser_thread.start()

        # Run uvicorn server directly on localhost
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            access_log=False,
            loop="asyncio"
        )
        server = uvicorn.Server(config)
        server.run()

    except KeyboardInterrupt:
        print("\nSnap2Print shut down gracefully.")
    except Exception as e:
        import traceback
        err_msg = f"An unexpected error occurred during application startup:\n\n{e}\n\n{traceback.format_exc()}"
        show_error_dialog("Snap2Print Fatal Error", err_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
