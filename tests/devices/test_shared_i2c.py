"""Regression tests enforcing a single shared I2C bus across device drivers."""
import ast
import os

import pytest


_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DEVICES_DIR = os.path.join(_REPO_ROOT, "devices")

# Drivers that previously created their own I2C bus should now receive it.
ADAFRUIT_DRIVERS = [
    "bme688.py",
    "bmp3xx.py",
    "gps.py",
    "lps28.py",
    "pm25.py",
    "scd4x.py",
    "sen6x.py",
]

ALL_DRIVERS = [f for f in os.listdir(_DEVICES_DIR) if f.endswith(".py")]


def _source_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _contains_call(source, func):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == func:
                    return True
            elif isinstance(node.func, ast.Name):
                if node.func.id == func:
                    return True
    return False


def test_no_board_i2c_in_drivers():
    """No driver source should call board.I2C()."""
    for name in ALL_DRIVERS:
        source = _source_text(os.path.join(_DEVICES_DIR, name))
        assert not _contains_call(source, "I2C"), (
            f"{name} still contains an I2C() call; drivers should receive a shared bus"
        )


@pytest.mark.parametrize("filename", ADAFRUIT_DRIVERS)
def test_adafruit_driver_accepts_i2c_param(filename):
    """Each Adafruit/CircuitPython driver constructor should accept an 'i2c' parameter."""
    source = _source_text(os.path.join(_DEVICES_DIR, filename))
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    args = [a.arg for a in item.args.args] + [
                        a.arg for a in item.args.kwonlyargs
                    ]
                    assert "i2c" in args, (
                        f"{filename}.__init__ must accept an 'i2c' parameter"
                    )
                    return
    pytest.fail(f"No __init__ method found in {filename}")


def test_simpleaq_creates_shared_i2c():
    """simpleaq.py should create exactly one board.I2C() instance and pass it to drivers."""
    path = os.path.join(_REPO_ROOT, "simpleaq.py")
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    board_i2c_calls = sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "I2C"
    )
    assert board_i2c_calls >= 1, "simpleaq.py should create a shared board.I2C()"
    assert "i2c=shared_i2c" in source, "simpleaq.py should pass the shared bus to drivers"
