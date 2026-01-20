"""
Pytest configuration for ComfyUI-RAWpy tests.

This file provides fixtures for both unit and integration tests.
Integration tests use LAZY IMPORTS to ensure unit tests can run
even without all dependencies installed.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# MARKER REGISTRATION
# =============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no server required)")
    config.addinivalue_line(
        "markers", "integration: Integration tests (requires ComfyUI server)"
    )


# =============================================================================
# UNIT TEST FIXTURES
# =============================================================================


@pytest.fixture
def mock_rawpy():
    """Mock rawpy.imread and postprocess for unit testing."""
    import numpy as np
    from unittest.mock import MagicMock, patch

    with patch("rawpy.imread") as mock_imread:
        mock_raw = MagicMock()
        # Create fake 100x100 RGB image
        mock_raw.postprocess.return_value = np.random.randint(
            0, 255, (100, 100, 3), dtype=np.uint8
        )
        mock_imread.return_value.__enter__ = MagicMock(return_value=mock_raw)
        mock_imread.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_raw


# =============================================================================
# INTEGRATION TEST FIXTURES
# =============================================================================


class ComfyUIApiClient:
    """Simple API client for ComfyUI server health checks and node queries."""

    def __init__(self, host="127.0.0.1", port=8188):
        self.base_url = f"http://{host}:{port}"
        # Lazy import requests only when client is used
        import requests

        self._requests = requests

    def is_healthy(self):
        """Check if the server is responding."""
        try:
            resp = self._requests.get(f"{self.base_url}/system_stats", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def get_object_info(self):
        """Get all registered nodes from the server."""
        resp = self._requests.get(f"{self.base_url}/object_info", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def node_exists(self, node_name):
        """Check if a specific node is registered."""
        try:
            info = self.get_object_info()
            return node_name in info
        except Exception:
            return False


@pytest.fixture(scope="session")
def api_client():
    """
    Provides a ComfyUI API client for integration tests.

    LAZY IMPORT: The 'requests' library is imported inside this fixture,
    so unit tests don't fail if 'requests' is not installed.
    """
    client = ComfyUIApiClient()
    if not client.is_healthy():
        pytest.skip("ComfyUI server is not running on port 8188")
    return client
