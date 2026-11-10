import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import LGTV


def test_setdefault_requires_tv_name(monkeypatch, tmp_path, capsys):
    """`lgtv setDefault` with no TV name must print usage and exit 1."""
    monkeypatch.setattr(
        LGTV, "find_config", lambda: str(tmp_path / "config.json")
    )
    monkeypatch.setattr(sys, "argv", ["lgtv", "setDefault"])
    with pytest.raises(SystemExit) as exc_info:
        LGTV.main()
    assert exc_info.value.code == 1
    assert "lgtv setDefault <tv_name>" in capsys.readouterr().out
