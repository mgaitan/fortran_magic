.PHONY: install test qa build

export UV_MALWARE_CHECK := 1

install:
	uv sync
	uv run --group dev prek install

test:
	JUPYTER_PLATFORM_DIRS=1 uv run --group dev pytest

qa:
	uv run --group dev prek run --all-files

build:
	uv build
