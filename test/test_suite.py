from sqlalchemy.testing.suite.test_dialect import *
import pytest
  
DifficultParametersTest = pytest.mark.skip(reason="Not compatible with aurora_dsql - serial identifier, mixed dml and ddl are not supported")(DifficultParametersTest)
