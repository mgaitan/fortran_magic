"""Test pyproject.toml"""

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - py3.10 fallback
    import tomli as tomllib


def test_pyproject_version_config() -> None:
    """Check pyproject.toml version configuration"""

    import fortranmagic

    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert "version" in data["project"]["dynamic"]
    assert data["tool"]["hatch"]["version"]["path"] == "fortranmagic.py"
    assert fortranmagic.__version__
