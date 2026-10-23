"""Unit tests must never write into the user's project/review database."""

import pytest


@pytest.fixture(autouse=True)
def isolated_workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("COVER_DATABASE", str(tmp_path / "workspace.sqlite3"))
