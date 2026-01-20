import subprocess
import os
import pytest

# Calculate paths relative to this test file
# custom_nodes/ComfyUI-RAWpy/tests/integration -> ../../../../
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COMFY_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
VENV_PYTHON = os.path.join(COMFY_ROOT, "venv", "Scripts", "python.exe")


def test_server_startup():
    """Verifies that ComfyUI server starts up correctly with the custom node loaded."""
    if not os.path.exists(VENV_PYTHON):
        # Fallback to system python if venv not found (e.g. CI environment)
        python_exe = sys.executable
        # But for this user we know venv exists
        # pytest.skip(f"ComfyUI venv not found at {VENV_PYTHON}")
    else:
        python_exe = VENV_PYTHON

    main_py = os.path.join(COMFY_ROOT, "main.py")

    print(f"Running ComfyUI from: {COMFY_ROOT}")
    print(f"Using Python: {python_exe}")

    # Run with --quick-test-for-ci which loads nodes and exits
    result = subprocess.run(
        [python_exe, main_py, "--quick-test-for-ci"],
        cwd=COMFY_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Server Output:\n", result.stdout)
        print("Server Errors:\n", result.stderr)

    assert result.returncode == 0, (
        f"Server failed to start. Return code: {result.returncode}"
    )
