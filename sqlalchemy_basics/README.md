# Comprehenssive SQLAlchemy Guide

[SQLAlchemy](https://www.sqlalchemy.org/) is one of the most popular ORMs build for Python and relies on
[psycopg2](https://www.psycopg.org/docs/) as its driver to communicate SQL queries with PostgrSQL databases.

As an ORM allows to build SQL tables in a Pythonistic syntax and it also works as a query builder to
perform read-write operations.

## Features

1.  Configuration

1.  Initialize connection

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(env.DB_URL)
        session = scoped_session(sessionmaker(engine))

1.  Declaring Base Entity Model

        Model = declarative_base(name=__name__)

1.  Declare Entity Models

        class User(Model):
            __tablename__ = "users"

            id = Column(Integer, primary_key=True, autoincrement=True)
            username = Column(String, nullable=False)
            email = Column(String, nullable=False)
            password = Column(String, nullable=False)
            created_at = Column(DateTime, default=datetime.now)
            updated_at = Column(DateTime, default=datetime.now)
            deleted_at = Column(DateTime, default=None)

1.  Database management capabilities

    The `Model.metadata` interface provides a series of DB / App admin functionalities that
    can help to stablish the integration behavior based on a specific environment or
    to simplify our development processes.

    -   Describe tables `tables`

    -   Create tables `create_all`

    -   Drop tables `clear`

    -   Reflect tables `reflect`

1.  Queries

    -   ORM's Syntax

        -   Writing

                def insert_user(conn: Session, user_data: dict) -> tuple[User]:
                    result = User(**user_data)
                    conn.add(result)
                    conn.commit()
                    return result

        -   Reading

                def get_users(conn: Session) -> list[User]:
                    result = conn.query(User).all()
                    return result

    -   Query Building capabilities

        -   Writing

                def insert_user(conn: Session, user_data: dict) -> tuple[User]:
                    query = (
                        insert(User)
                        .values(**user_data)
                        .returning(User)
                    )
                    result = conn.execute(query)
                    conn.commit()
                    return result.one()

        -   Reading

                def get_users(conn: Session) -> list[User]:
                    query = select(User)
                    result = conn.execute(query)
                    return result

1.  Non-indexed tables

    With the help of `Model.metadata.reflect` we can collect the necessary metadata to
    still use ORM syntax across non-declared models, e.g.

    1.  First, we run the following into our DB Client:

            # Executed directly at the PostgreSQL engine:
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

            CREATE TABLE IF NOT EXISTS profiles (
                uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                user_uuid UUID NOT NULL
            );

            ALTER TABLE profiles
            ADD CONSTRAINT fk_users_profiles
            FOREIGN KEY (user_uuid)
            REFERENCES users (uuid);

            INSERT INTO profiles (user_uuid)
            SELECT uuid FROM users;

    2.  Then we read `profiles` via Python:

        -   ORM Syntax

                def get_user_profile(conn: Session, user_uuid: UUID):
                    profiles = Model.metadata.tables["profiles"]
                    result = conn.query(profiles).where(User.uuid == user_uuid).all()
                    return result

        -   Query Builder Syntax

                def get_user_profile(conn: Session, user_uuid: UUID):
                    profiles = Model.metadata.tables["profiles"]
                    query = select(profiles).where(User.uuid == user_uuid)
                    result = conn.execute(query)
                    return result.fetchall()

1.  JOIN clause

    Following the schema generated so far, we can use JOIN statements as follows:

    -   ORM Syntax

            def get_user_profile(conn: Session, user_uuid: UUID):
                profiles = Model.metadata.tables["profiles"]
                result = conn.query(User, profiles).join(User).all()
                return result

    -   Query Builder Syntax

            from sqlalchemy.orm import aliased

            def get_user_profile(conn: Session, user_uuid: UUID):
                profiles = Model.metadata.tables["profiles"]
                user_alias = aliased(User)
                profile_alias = aliased(profiles)
                query = (
                    select(user_alias, profile_alias).join(user_alias).where(User.uuid == user_uuid)
                )
                result = conn.execute(query)
                return result.fetchall()
