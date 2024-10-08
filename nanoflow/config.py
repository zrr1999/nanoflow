from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class TaskConfig(BaseModel):
    command: str
    deps: list[str] = []


class WorkflowConfig(BaseModel):
    """
    Workflow config file.

    Example:
    >>> config = WorkflowConfig(
    >>>     name="test",
    >>>     resources="gpus",
    >>>     tasks={
    >>>         "task1": TaskConfig(command="echo 'task1'"),
    >>>         "task2": TaskConfig(command="echo 'task2'", deps=["task1"]),
    >>>         "task3": TaskConfig(command="echo 'task3'", deps=["task2"]),
    >>>     }
    >>> )
    >>> config.to_nodes()
    {'task1': [], 'task2': ['task1'], 'task3': ['task2']}
    """

    name: str
    tasks: dict[str, TaskConfig]
    resources: Literal["gpus"] | list[str] | None = None

    def to_nodes(self) -> dict[str, list[str]]:
        nodes = {}
        for task_name, task_config in self.tasks.items():
            nodes[task_name] = task_config.deps

        return nodes
