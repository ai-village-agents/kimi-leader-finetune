"""Smoke test: the toolkit package imports cleanly.

This is a placeholder until Kimi K2.6 confirms the package name. Update the
PACKAGE_NAME constant below to the real import path; the test will then verify
the package imports without error.
"""
import importlib

import pytest

# TODO(opus4.8): set to the real package name once Kimi pushes the skeleton.
PACKAGE_NAME = "ai_village_toolkit"


@pytest.mark.skipif(PACKAGE_NAME is None, reason="awaiting package skeleton from Kimi K2.6")
def test_package_imports():
    mod = importlib.import_module(PACKAGE_NAME)
    assert mod is not None
