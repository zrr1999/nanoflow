install:
    uv sync --all-extras --dev --index-url https://pypi.tuna.tsinghua.edu.cn/simple

ruff:
    ruff check . --fix --unsafe-fixes
    ruff format .

pyright:
    pyright .

cov:
    pytest --cov=nanoflow --xdoc
    coverage xml

check:
    just ruff
    just pyright

push:
    just cov
    git push
    git push --tags
