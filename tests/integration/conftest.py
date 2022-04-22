import pytest
from minumtium_postgres import MinumtiumPostgresAdapterConfig


@pytest.fixture
def adapter_config() -> MinumtiumPostgresAdapterConfig:
    return MinumtiumPostgresAdapterConfig(
        username='minumtium',
        password='samplepassword',
        host='127.0.0.1',
        port=5432,
        dbname='minumtium',
        schema_name='minumtium')


@pytest.fixture()
def schema_setup() -> str:
    return """
        DROP SCHEMA IF EXISTS minumtium CASCADE;
        CREATE SCHEMA minumtium;
        GRANT ALL ON SCHEMA minumtium TO postgres;
        GRANT ALL ON SCHEMA minumtium TO public;
        GRANT ALL ON SCHEMA minumtium TO minumtium;
        SET search_path = minumtium;
    """
