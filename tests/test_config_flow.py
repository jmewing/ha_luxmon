"""Tests for the lux-mon config flow, including add-on defaults passthrough."""
import json
from pathlib import Path

import pytest

from luxmon import config_flow


def test_load_addon_defaults_returns_empty_when_missing(monkeypatch, tmp_path):
    """No add-on defaults file -> empty dict."""
    monkeypatch.setattr(config_flow, "_ADDON_DEFAULTS_FILE", tmp_path / "nope.json")
    assert config_flow._load_addon_defaults() == {}


def test_load_addon_defaults_reads_file(monkeypatch, tmp_path):
    """Add-on defaults file is parsed into a dict."""
    p = tmp_path / ".addon-defaults.json"
    p.write_text(json.dumps({"host": "192.168.12.8", "port": 80, "api_token": "tok"}))
    monkeypatch.setattr(config_flow, "_ADDON_DEFAULTS_FILE", p)
    assert config_flow._load_addon_defaults() == {
        "host": "192.168.12.8",
        "port": 80,
        "api_token": "tok",
    }


def test_load_addon_defaults_handles_bad_json(monkeypatch, tmp_path):
    """Malformed JSON -> empty dict (no crash)."""
    p = tmp_path / ".addon-defaults.json"
    p.write_text("{not valid json")
    monkeypatch.setattr(config_flow, "_ADDON_DEFAULTS_FILE", p)
    assert config_flow._load_addon_defaults() == {}
