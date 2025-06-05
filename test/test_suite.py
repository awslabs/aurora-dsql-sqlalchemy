import pytest
from sqlalchemy.testing.suite.test_dialect import *  # noqa: F403

DifficultParametersTest = pytest.mark.skip(
    reason="""Not compatible with auroradsql - 
        serial identifier, 
        mixed dml and ddl are not supported"""
)(
    DifficultParametersTest  # noqa: F405
)
