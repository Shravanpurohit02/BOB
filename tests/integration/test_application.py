"""Integration tests for application."""

import pytest
from builder.bootstrap import bootstrap
from builder.cli.app import app
from typer.testing import CliRunner

runner = CliRunner()


@pytest.mark.integration
def test_application_startup():
    """Test that application can start up."""
    try:
        bootstrap()
    except Exception as e:
        pytest.fail(f"Application startup failed: {e}")


@pytest.mark.integration
def test_cli_help():
    """Test that CLI help works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Vidhi Builder" in result.stdout
