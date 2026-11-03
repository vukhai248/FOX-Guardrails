from typer.testing import CliRunner

import fox_guard
from fox_guard.cli import app


def test_package_imports():
    assert fox_guard.__version__ == "0.1.0"


def test_cli_help_and_version():
    runner = CliRunner()
    help_result = runner.invoke(app, ["--help"])
    assert help_result.exit_code == 0
    assert "FOX-Guard" in help_result.output
    version_result = runner.invoke(app, ["version"])
    assert version_result.exit_code == 0
    assert version_result.output.strip() == fox_guard.__version__
