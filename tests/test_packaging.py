from pathlib import Path
import tomllib


def _pyproject() -> dict:
    return tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_includes_redis_extra_and_vendor_data():
    data = _pyproject()
    extras = data["project"]["optional-dependencies"]
    assert extras["redis"] == ["redis>=5.0"]

    pkgdata = data["tool"]["setuptools"]["package-data"]["adiuvare"]
    assert "vendor/*.dll" in pkgdata
    assert "vendor/libinjection_src/*" in pkgdata


def test_manifest_carries_build_scripts_and_vendor_tree():
    text = Path("MANIFEST.in").read_text(encoding="utf-8")
    assert "scripts/build_libinjection.py" in text
    assert "scripts/build_libinjection.sh" in text
    assert "recursive-include adiuvare/vendor/libinjection_src *" in text


def test_public_version_is_exported():
    from adiuvare import __version__

    assert __version__ == "0.1.0"
