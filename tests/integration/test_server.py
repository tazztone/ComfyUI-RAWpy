"""
Integration tests for ComfyUI-RAWpy.

These tests require a running ComfyUI server on port 8188.
The run_tests.py script will auto-start the server if needed.
"""

import pytest


@pytest.mark.integration
class TestServerHealth:
    """Verify ComfyUI server is healthy and accessible."""

    def test_server_is_running(self, api_client):
        """Verify the server responds to health checks."""
        assert api_client.is_healthy(), "ComfyUI server should be reachable"


@pytest.mark.integration
class TestNodeRegistration:
    """Verify all RAWpy nodes are correctly registered with ComfyUI."""

    EXPECTED_NODES = [
        "Load Raw Image",
        "Load Raw Image Advanced",
    ]

    def test_all_nodes_registered(self, api_client):
        """Check that all expected nodes are available in the server."""
        for node_name in self.EXPECTED_NODES:
            assert api_client.node_exists(node_name), (
                f"Node '{node_name}' should be registered"
            )

    def test_node_count(self, api_client):
        """Verify the correct number of nodes are registered."""
        info = api_client.get_object_info()
        registered = [name for name in self.EXPECTED_NODES if name in info]
        assert len(registered) == len(self.EXPECTED_NODES), (
            f"Expected {len(self.EXPECTED_NODES)} nodes, found {len(registered)}"
        )


@pytest.mark.integration
class TestNodeInputsOutputs:
    """Verify node schemas are correctly defined."""

    def test_load_raw_image_has_image_input(self, api_client):
        """Verify LoadRawImage has the required 'image' input."""
        info = api_client.get_object_info()
        node_info = info.get("Load Raw Image", {})
        inputs = node_info.get("input", {}).get("required", {})
        assert "image" in inputs, "LoadRawImage should have 'image' input"

    def test_load_raw_image_has_image_output(self, api_client):
        """Verify LoadRawImage outputs an IMAGE type."""
        info = api_client.get_object_info()
        node_info = info.get("Load Raw Image", {})
        outputs = node_info.get("output", [])
        assert "IMAGE" in outputs, "LoadRawImage should output IMAGE type"
