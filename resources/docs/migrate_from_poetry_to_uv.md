# Migrating from Poetry to uv

`uv` is an extremely fast Python package and project manager, written in Rust.

## How to migrate from Poetry to uv

First, you need to convert your poetry compatible pyproject.toml to be compatible with uv. You can actually do it quite easily with pdm.
```bash
uvx pdm import pyproject.toml
```

Next, remove all poetry sections in the pyproject (i.e. [tool.poetry...] sections)

Then, replace `[tool.pdm.dev-dependencies]` with `[dependency-groups]`.

You are done now!

## Exporting the requirements from uv to a requirements.txt file

```bash
uv export --no-hashes --format requirements-txt > requirements.txt
```
