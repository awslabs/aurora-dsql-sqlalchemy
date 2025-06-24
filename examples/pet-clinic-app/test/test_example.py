import pytest

from ..src.example import example, run_retry


# Smoke tests that our example works fine
def test_example():
    try:
        example()
        run_retry()
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
