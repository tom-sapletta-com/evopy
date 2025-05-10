import subprocess
import sys
import pytest

def test_venv_active():
    # Sprawdź, czy uruchomione jest środowisko wirtualne
    assert (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    ), "Python nie działa w środowisku wirtualnym (.venv)!"

def test_flask_installed():
    try:
        import flask
    except ImportError:
        pytest.fail("Flask NIE jest zainstalowany w aktywnym środowisku!")

def test_matplotlib_installed():
    try:
        import matplotlib
    except ImportError:
        pytest.fail("matplotlib NIE jest zainstalowany w aktywnym środowisku!")

def test_openpyxl_installed():
    try:
        import openpyxl
    except ImportError:
        pytest.fail("openpyxl NIE jest zainstalowany w aktywnym środowisku!")

def test_requests_installed():
    try:
        import requests
    except ImportError:
        pytest.fail("requests NIE jest zainstalowany w aktywnym środowisku!")
