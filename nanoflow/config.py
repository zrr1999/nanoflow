from __future__ import annotations

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

    def to_nodes(self) -> dict[str, list[str]]:
        nodes = {}
        for task_name, task_config in self.tasks.items():
            nodes[task_name] = task_config.deps

        return nodes
