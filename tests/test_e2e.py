from __future__ import annotations

import pytest


@pytest.mark.benchmark
def test_cli():
    from typer.testing import CliRunner

    from nanoflow.__main__ import app

    runner = CliRunner()
    result = runner.invoke(app, ["./examples/simple.toml"])
    assert result.exit_code == 0, f"Exit code was {result.exit_code}, expected 0. Error: {result.exc_info}"


@pytest.mark.asyncio
async def test_tui():
    import toml

    from nanoflow.config import WorkflowConfig
    from nanoflow.tui import Nanoflow

    workflow_config = WorkflowConfig.model_validate(toml.load("./examples/simple.toml"))
    app = Nanoflow(workflow_config)
    async with app.run_test() as pilot:
        assert app.is_running is True
        await pilot.press("q")
        assert app.is_running is False
