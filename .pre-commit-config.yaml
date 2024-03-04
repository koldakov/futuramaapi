fail_fast: true

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-yaml
      - id: check-toml
      - id: check-json
      - id: check-symlinks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.7
    hooks:
      - id: ruff
      - id: ruff-format
      - id: ruff
        args:
          - --no-fix
        stages:
          - manual
      - id: ruff-format
        args:
          - --check
        stages:
          - manual

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        pass_filenames: false
        args:
          - --install-types
          - --non-interactive
          - --check-untyped-defs
          - --python-version=3.12
