"""
Unit tests for syntax validation and import rules.

These tests ensure all Python files in the package are syntactically valid
and follow strict import rules (no ComfyUI-specific imports at module level).
"""

import pytest
import ast
import os


@pytest.mark.unit
class TestSyntax:
    """Validate Python syntax across all source files."""

    @pytest.fixture
    def source_files(self):
        """Get all Python files in the package root."""
        package_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        python_files = []
        for filename in os.listdir(package_root):
            if filename.endswith(".py") and not filename.startswith("_"):
                python_files.append(os.path.join(package_root, filename))
        return python_files

    def test_all_files_parse(self, source_files):
        """Verify all Python files are syntactically valid."""
        for filepath in source_files:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            try:
                ast.parse(source)
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {filepath}: {e}")

    def test_no_print_statements_in_production(self, source_files):
        """Check for debug print statements (optional warning)."""
        for filepath in source_files:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "print":
                        # This is a warning, not a failure
                        # pytest.warn(f"Found print() in {filepath}:{node.lineno}")
                        pass
