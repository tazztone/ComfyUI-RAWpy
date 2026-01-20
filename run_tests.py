#!/usr/bin/env python
"""
Test runner for ComfyUI-RAWpy.

This script handles the working directory setup to avoid relative import issues
with ComfyUI custom nodes. It also auto-starts ComfyUI for integration tests.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -m unit      # Run only unit tests (fast, no server)
    python run_tests.py -m integration  # Run integration tests (auto-starts server)
"""

import os
import sys
import subprocess
import time
import signal
import atexit

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(SCRIPT_DIR, "tests")
COMFYUI_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
COMFYUI_MAIN = os.path.join(COMFYUI_ROOT, "main.py")
PYTHON_EXE = os.path.join(COMFYUI_ROOT, "venv", "Scripts", "python.exe")

# Server process handle
_server_process = None


def is_server_running(host="127.0.0.1", port=8188):
    """Check if ComfyUI server is already running."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False


def start_comfyui_server():
    """Start ComfyUI server in background and wait for it to be ready."""
    global _server_process

    if is_server_running():
        print("✓ ComfyUI server already running on port 8188")
        return None

    print("🚀 Starting ComfyUI server...")

    # Start server with subprocess
    _server_process = subprocess.Popen(
        [PYTHON_EXE, COMFYUI_MAIN, "--listen", "127.0.0.1", "--port", "8188"],
        cwd=COMFYUI_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        if sys.platform == "win32"
        else 0,
    )

    # Register cleanup
    atexit.register(stop_comfyui_server)

    # Wait for server to be ready (max 60 seconds)
    print("   Waiting for server to be ready...", end="", flush=True)
    for i in range(60):
        if is_server_running():
            print(f" ready! ({i + 1}s)")
            return _server_process
        time.sleep(1)
        print(".", end="", flush=True)

    print("\n✗ Server failed to start within 60 seconds")
    stop_comfyui_server()
    sys.exit(1)


def stop_comfyui_server():
    """Stop the ComfyUI server if we started it."""
    global _server_process
    if _server_process is not None:
        print("\n🛑 Stopping ComfyUI server...")
        if sys.platform == "win32":
            _server_process.terminate()
        else:
            os.killpg(os.getpgid(_server_process.pid), signal.SIGTERM)
        _server_process.wait(timeout=10)
        _server_process = None


def main():
    # Parse arguments to check if integration tests are requested
    args = sys.argv[1:]
    running_integration = "-m" not in args or "integration" in args
    running_unit_only = "-m" in args and "unit" in args and "integration" not in args

    # Start server if integration tests are needed
    if running_integration and not running_unit_only:
        start_comfyui_server()

    # Change to tests directory (critical for relative import handling)
    os.chdir(TESTS_DIR)

    # Build pytest command
    pytest_args = [PYTHON_EXE, "-m", "pytest", "."] + args

    print(f"\n📋 Running: {' '.join(pytest_args)}")
    print(f"   Working directory: {os.getcwd()}\n")

    # Run pytest
    try:
        result = subprocess.run(pytest_args)
        return result.returncode
    finally:
        stop_comfyui_server()


if __name__ == "__main__":
    sys.exit(main())
