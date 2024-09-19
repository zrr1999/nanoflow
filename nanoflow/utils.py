from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import Callable

import networkx as nx
from loguru import logger

from .config import WorkflowConfig
from .resource_pool import ResourcePool
from .task import Task, task
from .workflow import workflow


@task
def group_parallel_nodes(nodes: dict[str, list[str]]) -> list[list[str]]:
    graph = nx.DiGraph()

    for node, dependencies in nodes.items():
        for dependency in dependencies:
            graph.add_edge(dependency, node)

    level = {}
    for node in nx.topological_sort(graph):
        level[node] = max((level[pred] + 1 for pred in graph.predecessors(node)), default=0)

    max_level = max(level.values(), default=-1)
    parallel_nodes = [[] for _ in range(max_level + 1)]
    for node, lvl in level.items():
        parallel_nodes[lvl].append(node)

    return parallel_nodes


@task
def get_available_gpus(threshold=0.05) -> list[int]:
    gpu_info = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,nounits,noheader"]
    ).decode("utf-8")
    gpus = [tuple(map(int, line.split(","))) for line in gpu_info.strip().split("\n")]

    free_gpus = []
    for i, (used, total) in enumerate(gpus):
        usage_ratio = used / total
        if usage_ratio <= threshold:
            free_gpus.append(i)

    return free_gpus


@workflow
async def execute_parallel_tasks(config: WorkflowConfig):
    def create_gpu_task(command: str) -> Task:
        environ = os.environ.copy()

        def set_visible_gpu(fn: Callable[[], bytes], resource: int) -> Callable[[], bytes]:
            environ["CUDA_VISIBLE_DEVICES"] = str(resource)

            def inner_fn() -> bytes:
                res = subprocess.run(command, shell=True, env=environ)
                if res.returncode != 0:
                    logger.error(f"Command failed with return code {res.returncode}")
                    return res.stderr
                return res.stdout

            return inner_fn

        @task(resource_pool=gpu_pool, resource_modifier=set_visible_gpu)
        def dummy_fn() -> bytes: ...

        return dummy_fn

    logger.info("Submitting tasks to get available GPUs and group parallel nodes")
    available_gpus = get_available_gpus.submit()
    parallel_nodes = group_parallel_nodes.submit(config.to_nodes())

    logger.info("Creating GPU resource pool and parallel tasks")
    gpu_pool = ResourcePool(await available_gpus)
    parallel_tasks = [[create_gpu_task(config.tasks[node].command) for node in nodes] for nodes in await parallel_nodes]

    for tasks in parallel_tasks:
        start_time = asyncio.get_event_loop().time()
        logger.info(f"Starting execution of {len(tasks)} tasks")
        await asyncio.gather(*[task.submit() for task in tasks])
        end_time = asyncio.get_event_loop().time()
        logger.info(f"Execution completed, actual time taken: {end_time - start_time:.2f} seconds")
