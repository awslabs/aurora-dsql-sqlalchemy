import pytest

from src.example import (
    demo_pet_clinic_operations,
    demo_retry_mechanism,
    create_dsql_engine,
)


# Smoke tests that our example works fine
def test_example():
    try:
        engine = create_dsql_engine()
        demo_pet_clinic_operations(engine)
        demo_retry_mechanism(engine)
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
