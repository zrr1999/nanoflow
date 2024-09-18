from __future__ import annotations

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


def init_logger(log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]):
    handler = RichHandler(highlighter=NullHighlighter(), markup=True)
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)


@app.command()
def run(config_path: Path):
    init_logger("DEBUG")
    workflow_config = WorkflowConfig.model_validate(toml.load(config_path))
    execute_parallel_tasks.run(workflow_config)


if __name__ == "__main__":
    app()
