"""
Root conftest.py for shared fixtures across all test files.
"""

import pytest


@pytest.fixture(autouse=True)
def _setup_test_environment():
    """Auto-use fixture that runs before every test.
    Add global setup/teardown here.
    """
    yield
    # Teardown happens here
