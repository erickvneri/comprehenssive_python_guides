# Comprehenssive alembic Guide

The [alembic](https://alembic.sqlalchemy.org/en/latest/index.html) tool is a powerful database change
manager that operates on top of [psycopg2](https://www.psycopg.org/docs/) and [SQLAlchemy](https://www.sqlalchemy.org/)
to maintain migration scripts history.

> DISCLAIMER
>
> Even when database migration tools offer the oportunity to jump between migrations or going up and
> down, it is advised to preserve a unidirectional migrations history to guarantee visibility of
> changes over time.

## Features

1.  Initialize

    Create alembic configuration files

        alembic init migrations

        # Migrations file system generated:
        .
        ├── alembic.ini
        └── migrations
           ├── env.py
           ├── README
           ├── script.py.mako
           └── versions

1.  Configurations:

    The `alembic.ini` file describes how Python will behave while developers or automated scripts
    interact with the `alembic` command line tool.

    -   Database Connection

            sqlalchemy.url = driver://user:pass@localhost/dbname

    -   Loggers

1.  Create new migration:

        alembic revision -m "first_migration"

        # output
        Generating /home/ubuntu/alembic_basics/migrations/versions/42e
        936388b35_first_migration.py ...  done

    -   Migration script boilerplate

            """first_migration

            Revision ID: 42e936388b35
            Revises:
            Create Date: 2023-07-21 12:49:35.457288

            """
            from alembic import op
            import sqlalchemy as sa


            # revision identifiers, used by Alembic.
            revision = '42e936388b35'
            down_revision = None
            branch_labels = None
            depends_on = None


            def upgrade() -> None:
                pass


            def downgrade() -> None:
                pass

1.  Upgrade and Downgrade commands:

    -   Upgrade/Downgrade only one migration

             # up
              alembic upgrade +1

              # down
              alembic downgrade -1

    -   Upgrade whole migrations sequence

              # up
              alembic upgrade head

              # down
              alembic downgrade base

    -   Upgrade to specific migration

            # up
            alembic upgrade <revision_id>

            # down
            alembic downgrade <revision_id>

1.  Migration Syntax

    -   SQL migrations

            def upgrade() -> None:
                sql = """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR NOT NULL,
                        password VARCHAR NOT NULL,
                        email VARCHAR NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        deleted_at TIMESTAMP DEFAULT NULL
                    );

                """
                op.execute(sql)

    -   SQLAlchemy migrations

            def upgrade() -> None:
                op.create_table(
                    "users_sqlalchemy_syntax",
                    sa.Column("id", sa.Integer, primary_key=True, autoincrement="auto"),
                    sa.Column("username", sa.String, nullable=False),
                    sa.Column("password", sa.String, nullable=False),
                    sa.Column("email", sa.String, nullable=False),
                    sa.Column("created_at", sa.TIMESTAMP, default=datetime.now),
                    sa.Column("updated_at", sa.TIMESTAMP, default=datetime.now),
                    sa.Column("deleted_at", sa.TIMESTAMP, default=None),
                )

1.  Deprecating migrations:

    This process may be confusing at first because alembic doesn't provide a built-in procedure to
    deprecate or remove migrations from the versions tree.

    Therefore, revision Ids must be updated, for example, consider the following migrations sequence
    where migration **B** must be removed from the tree.

        ## Migration A
        Revision ID: 42e936388b35
        Revises:
        Create Date: 2023-07-21 12:49:35.457288


        ## Migration B
        Revision ID: c014b8338738
        Revises: 42e936388b35
        Create Date: 2023-07-21 13:07:30.603231


        ## Migration C
        Revision ID: c92adffd2e6c
        Revises: c014b8338738
        Create Date: 2023-07-21 13:11:22.936899

    In this case, **Migration C**'s `Revises` parameter must be updated with **Migration A**'s
    revision Id and then **Migration B** will be free to leave the stack.
