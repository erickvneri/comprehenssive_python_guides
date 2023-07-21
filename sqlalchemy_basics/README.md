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

1.  Read-Write SQL-ish Queries
