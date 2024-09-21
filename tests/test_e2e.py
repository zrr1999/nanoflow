from __future__ import annotations

import tempfile

from typer.testing import CliRunner

from nanoflow.__main__ import app

runner = CliRunner()


def test_app():
    with tempfile.NamedTemporaryFile(suffix=".toml", mode="w+t") as temp_config:
        temp_config.write("""
name = "test"

[tasks.a]
command = "echo 'a'"

[tasks.b]
command = "echo 'b'"

[tasks.c]
command = "echo 'c'"
deps = ["a", "b"]
""")
        temp_config.flush()
        result = runner.invoke(app, [temp_config.name])
        assert result.exit_code == 0
