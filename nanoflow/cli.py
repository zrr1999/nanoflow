from __future__ import annotations

import asyncio
from logging import Handler
from pathlib import Path
from typing import Literal

import toml
import typer
from loguru import logger
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler

from nanoflow import WorkflowConfig
from nanoflow.utils import execute_parallel_tasks

app = typer.Typer()


def init_logger(log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], handler: Handler):
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)


@app.command()
def run(config_path: Path, use_tui: bool = False):
    handler = RichHandler(highlighter=NullHighlighter(), markup=True)
    init_logger("DEBUG", handler)
    workflow_config = WorkflowConfig.model_validate(toml.load(config_path))
    if use_tui:  # pragma: no cover
        from nanoflow.tui import Nanoflow

        app = Nanoflow(workflow_config)

        async def start():
            await asyncio.gather(execute_parallel_tasks(workflow_config, update_hook=app.update_log), app.run_async())

        asyncio.run(start())
    else:
        execute_parallel_tasks.run(workflow_config)
