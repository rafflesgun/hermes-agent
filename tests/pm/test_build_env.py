"""The build_env CLI carries the caller's dependency-build timeout.

A cold sdist compile — and a cross-arch image build, which runs it under CPU
emulation — outlasts the interactive 1800s default. A caller that knows its
budget (the Docker image) must be able to raise it through the CLI.
"""

from __future__ import annotations


def _capture(monkeypatch, name, tmp_path):
    import pm

    seen: dict = {}
    monkeypatch.setattr(
        pm, name, lambda *args, **kwargs: seen.update(kwargs) or tmp_path / "venv/bin/python"
    )
    return seen


def test_timeout_reaches_a_project_build(monkeypatch, tmp_path):
    from pm import build_env

    seen = _capture(monkeypatch, "build_environment", tmp_path)
    assert build_env.main(["--source", str(tmp_path), "--out", str(tmp_path / "venv"),
                           "--timeout", "7200"]) == 0
    assert seen["timeout"] == 7200


def test_timeout_reaches_a_requirements_build(monkeypatch, tmp_path):
    from pm import build_env

    seen = _capture(monkeypatch, "build_requirements_environment", tmp_path)
    assert build_env.main(["--out", str(tmp_path / "venv"), "--requirement", "attrs==24.2.0",
                           "--timeout", "7200"]) == 0
    assert seen["timeout"] == 7200


def test_timeout_defaults_to_the_interactive_budget(monkeypatch, tmp_path):
    from pm import build_env

    seen = _capture(monkeypatch, "build_environment", tmp_path)
    assert build_env.main(["--source", str(tmp_path), "--out", str(tmp_path / "venv")]) == 0
    assert seen["timeout"] == 1800
