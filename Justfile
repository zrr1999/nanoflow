install:
    uv sync --all-extras --dev --index-url https://pypi.tuna.tsinghua.edu.cn/simple

ruff:
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .

pyright:
    uv run pyright .

cov:
    uv run pytest --cov=nanoflow --xdoc
    uv run coverage xml

check:
    just ruff
    just pyright

push:
    just cov
    git push
    git push --tags
