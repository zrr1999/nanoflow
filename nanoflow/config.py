from __future__ import annotations

from pydantic import BaseModel


class TaskConfig(BaseModel):
    command: str
    deps: list[str] = []


class WorkflowConfig(BaseModel):
    name: str
    tasks: dict[str, TaskConfig]

    def to_nodes(self) -> dict[str, list[str]]:
        nodes = {}
        for task_name, task_config in self.tasks.items():
            nodes[task_name] = task_config.deps

        return nodes
