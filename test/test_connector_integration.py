# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from botocore.credentials import CredentialProvider, Credentials
from botocore.session import get_session
from sqlalchemy import text
from sqlalchemy.testing import fixtures

from aurora_dsql_sqlalchemy import create_dsql_engine

from .conftest import CLUSTER_ENDPOINT, CLUSTER_ID, CLUSTER_USER, REGION

DRIVERS = ["psycopg", "psycopg2"]


class TrackingCredentialsProvider(CredentialProvider):
    METHOD = "custom-tracking"

    def __init__(self):
        super().__init__()
        self.load_called = False

    def load(self):
        self.load_called = True
        session = get_session()
        creds = session.get_credentials()
        return Credentials(creds.access_key, creds.secret_key, creds.token)


def _verify_connection(engine):
    """Verify the engine can connect and execute a simple query."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


class TestConnectorIntegration(fixtures.TestBase):
    """Integration tests verifying connector parameters work correctly."""

    @pytest.mark.parametrize("driver", DRIVERS)
    def test_profile_used_for_connection(self, driver):
        """Verify that profile parameter is used when connecting."""
        engine = create_dsql_engine(
            host=CLUSTER_ENDPOINT,
            user=CLUSTER_USER,
            driver=driver,
            connect_args={"profile": "default"},
        )
        _verify_connection(engine)

    @pytest.mark.parametrize("driver", DRIVERS)
    def test_cluster_id_with_region(self, driver):
        """Verify that cluster ID with region parameter works."""
        engine = create_dsql_engine(
            host=CLUSTER_ID,
            user=CLUSTER_USER,
            driver=driver,
            connect_args={"region": REGION},
        )
        _verify_connection(engine)

    @pytest.mark.parametrize("driver", DRIVERS)
    def test_token_duration_secs(self, driver):
        """Verify that token_duration_secs parameter works."""
        engine = create_dsql_engine(
            host=CLUSTER_ENDPOINT,
            user=CLUSTER_USER,
            driver=driver,
            connect_args={"token_duration_secs": 900},
        )
        _verify_connection(engine)

    @pytest.mark.parametrize("driver", DRIVERS)
    def test_custom_credentials_provider(self, driver):
        """Verify that custom_credentials_provider parameter works."""
        provider = TrackingCredentialsProvider()
        engine = create_dsql_engine(
            host=CLUSTER_ENDPOINT,
            user=CLUSTER_USER,
            driver=driver,
            connect_args={"custom_credentials_provider": provider},
        )
        _verify_connection(engine)
        assert provider.load_called
