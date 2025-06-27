## Dependencies for engine creation
import os

## Dependencies for token generation
import boto3
import psycopg2.extensions

## Dependencies for Model class
from sqlalchemy import Column, Date, String, create_engine, event, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import URL

## Dependencies for retry statement
from sqlalchemy.exc import SQLAlchemyError

## Dependencies for object creation (inserts)
from sqlalchemy.orm import DeclarativeBase, Session, relationship
from sqlalchemy.sql import text

ADMIN = "admin"
NON_ADMIN_SCHEMA = "myschema"


def create_dsql_engine():
    print("Starting to create DSQL Engine")
    cluster_user = os.environ.get("CLUSTER_USER", None)
    assert cluster_user is not None, "CLUSTER_USER environment variable is not set"

    cluster_endpoint = os.environ.get("CLUSTER_ENDPOINT", None)
    assert (
        cluster_endpoint is not None
    ), "CLUSTER_ENDPOINT environment variable is not set"

    region = os.environ.get("REGION", None)
    assert region is not None, "REGION environment variable is not set"

    client = boto3.client("dsql", region_name=region)

    # Create the URL, note that the password token is added when connections are created
    url = URL.create(
        "auroradsql+psycopg2",
        username=cluster_user,
        host=cluster_endpoint,
        database="postgres",
    )

    connect_args = {
        "sslmode": "verify-full",
        "sslrootcert": "./root.pem",
    }

    # Use the more efficient connection method if it's supported.
    if psycopg2.extensions.libpq_version() >= 170000:
        connect_args["sslnegotiation"] = "direct"

    # Create the engine
    engine = create_engine(url, connect_args=connect_args, pool_size=5, max_overflow=10)

    # Adds a listener that creates a new token every time a new connection is created
    # in the SQLAlchemy engine
    @event.listens_for(engine, "do_connect")
    def add_token_to_params(dialect, conn_rec, cargs, cparams):
        # Generate a fresh token for this connection
        fresh_token = generate_token(client, cluster_user, cluster_endpoint, region)
        # Update the password in connection parameters
        cparams["password"] = fresh_token

    # If we are using the non-admin user, we need to set the search path to use
    # 'myschema' instead of public whenever a connection is created.
    @event.listens_for(engine, "connect", insert=True)
    def set_search_path(dbapi_connection, connection_record):
        print("Successfully opened connection")
        if cluster_user == ADMIN:
            return
        existing_autocommit = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION search_path='%s'" % NON_ADMIN_SCHEMA)
        cursor.close()
        dbapi_connection.autocommit = existing_autocommit

    return engine


def generate_token(client, cluster_user, cluster_endpoint, region):
    if cluster_user == ADMIN:
        return client.generate_db_connect_admin_auth_token(cluster_endpoint, region)
    else:
        return client.generate_db_connect_auth_token(cluster_endpoint, region)


class Base(DeclarativeBase):
    pass


# Define a Owner table
class Owner(Base):
    __tablename__ = "owner"

    id = Column("id", UUID, primary_key=True, default=text("gen_random_uuid()"))
    name = Column("name", String(30), nullable=False)
    city = Column("city", String(80), nullable=False)
    telephone = Column("telephone", String(20), nullable=True, default=None)


# Define a Pet table
class Pet(Base):
    __tablename__ = "pet"

    id = Column("id", UUID, primary_key=True, default=text("gen_random_uuid()"))
    name = Column("name", String(30), nullable=False)
    birth_date = Column("birth_date", Date(), nullable=False)
    owner_id = Column("owner_id", UUID, nullable=True)
    # One to many
    owner = relationship(
        "Owner", foreign_keys=[owner_id], primaryjoin="Owner.id == Pet.owner_id"
    )


# Define an association table for Vet and Speacialty, this is an intermediate table
# that lets us define the may-to-many mapping
class VetSpecialties(Base):
    __tablename__ = "vetSpecialties"

    id = Column("id", UUID, primary_key=True, default=text("gen_random_uuid()"))
    vet_id = Column("vet_id", UUID, nullable=True)
    specialty_id = Column("specialty_id", String(80), nullable=True)


# Define a Specialty table
class Specialty(Base):
    __tablename__ = "specialty"
    id = Column("name", String(80), primary_key=True)


# Define a Vet table
class Vet(Base):
    __tablename__ = "vet"

    id = Column("id", UUID, primary_key=True, default=text("gen_random_uuid()"))
    name = Column("name", String(30), nullable=False)
    # Many-to-Many mapping
    specialties = relationship(
        "Specialty",
        secondary=VetSpecialties.__table__,
        primaryjoin="foreign(VetSpecialties.vet_id)==Vet.id",
        secondaryjoin="foreign(VetSpecialties.specialty_id)==Specialty.id",
    )


def demo_pet_clinic_operations(engine):

    print("Starting demo pet clinic operations")
    print("Starting cleanup of existing tables")
    # Clean up any existing tables
    for table in Base.metadata.tables.values():
        table.drop(engine, checkfirst=True)
    print("Successfully cleaned up existing tables")
    print("Creating new tables")
    # Create all tables
    for table in Base.metadata.tables.values():
        table.create(engine, checkfirst=True)
    print("All tables created successfully")
    session = Session(engine)
    # Owner-Pet relationship is one to many.
    ## Insert owners
    john_doe = Owner(name="John Doe", city="Anytown")
    mary_major = Owner(name="Mary Major", telephone="555-555-0123", city="Anytown")

    ## Add two pets.
    pet_1 = Pet(name="Pet-1", birth_date="2006-10-25", owner=john_doe)
    pet_2 = Pet(name="Pet-2", birth_date="2021-7-23", owner=mary_major)

    session.add_all([john_doe, mary_major, pet_1, pet_2])
    print("Created owners: John Doe, Mary Major")
    print("Created pets: Pet-1, Pet-2")
    session.commit()
    print("Successfully committed Owner and Pet data")

    # Read back data for the pet.
    print("Fetching Pet-1 data")
    pet_query = select(Pet).where(Pet.name == "Pet-1")
    pet_1 = session.execute(pet_query).fetchone()[0]
    print("Successfully fetched Pet-1 data")

    # Get the corresponding owner
    print("Fetching Pet-1's owner data")
    owner_query = select(Owner).where(Owner.id == pet_1.owner_id)
    john_doe = session.execute(owner_query).fetchone()[0]
    print("Successfully fetched Pet-1's owner data")

    # Test: check read values
    assert pet_1.name == "Pet-1"
    assert str(pet_1.birth_date) == "2006-10-25"
    # Owner must be what we have inserted
    assert john_doe.name == "John Doe"
    assert john_doe.city == "Anytown"

    # Vet-Specialty relationship is many to many.
    dogs = Specialty(id="Dogs")
    cats = Specialty(id="Cats")

    ## Insert two vets with specialties, one vet without any specialty
    akua_mansa = Vet(name="Akua Mansa", specialties=[dogs])
    carlos_salazar = Vet(name="Carlos Salazar", specialties=[dogs, cats])

    session.add_all([dogs, cats, akua_mansa, carlos_salazar])
    print("Created vet specialties: Dogs, Cats")
    print("Created vets: Akua Mansa, Carlos Salazar")
    session.commit()
    print("Successfully committed vet specialty and vet data")

    # Read back data for the vets.
    print("Fetching vet data: Akua Mansa")
    vet_query = select(Vet).where(Vet.name == "Akua Mansa")
    akua_mansa = session.execute(vet_query).fetchone()[0]
    print("Successfully fetched vet data: Akua Mansa")

    print("Fetching vet data: Carlos Salazar")
    vet_query = select(Vet).where(Vet.name == "Carlos Salazar")
    carlos_salazar = session.execute(vet_query).fetchone()[0]
    print("Successfully fetched vet data: Carlos Salazar")

    # Test: check read value
    assert akua_mansa.name == "Akua Mansa"
    assert akua_mansa.specialties[0].id == "Dogs"

    assert carlos_salazar.name == "Carlos Salazar"
    assert carlos_salazar.specialties[0].id == "Cats"
    assert carlos_salazar.specialties[1].id == "Dogs"

    print("Finished demo pet clinic operations")


# Execute SQL Statement with retry
def execute_sql_statement_retry(engine, sql_statement, max_retries=None):
    with engine.connect() as connection:
        while max_retries is None or max_retries > 0:
            try:
                connection.execute(text(sql_statement))
                connection.commit()
                break
            except SQLAlchemyError as e:
                error = str(e.orig)
                if not ("OC001" in error or "OC000" in error):
                    raise e
                print(f"Error occurred when executing {sql_statement}, executing retry")
                if max_retries is not None:
                    max_retries -= 1


def demo_retry_mechanism(engine):

    print("Starting demo retry mechanism")
    # Create and drop the table, will retry until success is reached
    print("Creating test table abc")
    execute_sql_statement_retry(
        engine, "CREATE TABLE IF NOT EXISTS abc (id UUID NOT NULL);"
    )
    print("Created test table abc")
    print("Dropping test table abc")
    execute_sql_statement_retry(engine, "DROP TABLE IF EXISTS abc;")
    print("Dropped test table abc")

    # Run statement that will fail, it will not be retried as
    # the error is not OC001 or OC000
    try:
        print(
            "Dropping test table abc again which is expected to fail as it does not exist"
        )
        execute_sql_statement_retry(engine, "DROP TABLE abc;")
    except Exception as e:
        assert 'table "abc" does not exist' in str(e).lower()

    print("Creating test table abc with a maximum of 3 retries")
    # Create and drop the table, with maximum retries of 3
    execute_sql_statement_retry(
        engine, "CREATE TABLE IF NOT EXISTS abc (id UUID NOT NULL);", 3
    )
    print("Created test table abc")
    print("Dropping test table abc with a maximum of 3 retries")
    execute_sql_statement_retry(engine, "DROP TABLE IF EXISTS abc;", 3)
    print("Dropped test table abc")
    print("Finished demo retry mechanism")


if __name__ == "__main__":
    engine = create_dsql_engine()
    demo_pet_clinic_operations(engine)
    demo_retry_mechanism(engine)
