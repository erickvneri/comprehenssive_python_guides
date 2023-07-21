# Comprehenssive Psycopg2 Guide

[Psycopg2](https://www.psycopg.org/docs/) is a PostgreSQL adapter for Python released in 2010
and its whole feature set is compliant with the [PEP 249 - Python Database API Specification
2.0](https://peps.python.org/pep-0249/)\*.

\*documentation intended to encourage following up a set of guidelines for the development and
release of Python-based software with the goal of database access.

---

## Preface

Before getting hands on with the following snippets, make sure you've read the [Runtime
requirements](https://www.psycopg.org/docs/install.html#runtime-requirements) section.

Additionally, consider that previous SQL knowledge MAY BE required to take the most out of this
library, its benefits and optimize it over time.

## Features

1.  Connection and minimal configuration

        import psycopg2

        connection = psycopg2.connect(
            host="...",
            port="...",
            dbname="...",
            user="...",
            password="...",
        )

        # This configuration will allow minimizing
        # embedded SQL into the Python Database Access
        # Objects by commiting SQL queries as they're
        # being executed.
        connection.autocommit = True

1.  Cursor / Pool _([reference](https://www.psycopg.org/docs/cursor.html#cursor.executemany))_

    A connection cursor, also known as Pool is useful to save time between execution of several
    queries by reusing the connection session.

        pool = connection.cursor()

1.  Query Execution

        sql_query = """
        SELECT
            application_name,
            username,
            datname,
            client_addr,
            backend_start
        FROM pg_stat_activity;
        """
        pool.execute(sql_query)
        result = pool.fetch_all()

1.  Parametrization

        sql_query = """
        SELECT
            application_name,
            user,
            datname,
            client_addr,
            backend_start
        FROM pg_stat_activity
        WHERE datname = %(database)s;
        """
        params = dict(database='...')

        pool.execute(sql_query, params)
        result: list[tuple] = pool.fetch_all()

1.  Remapping psycopg results

        # By taking the same snippet from below...
        result: list[tuple] = pool.fetch_all()

        def remap_result(row: tuple):
            (
                application_name,
                user,
                database,
                client_ip_addr,
                connected_at
            ) = row

            return dict(
                application_name=application_name,
                user=user,
                database=database,
                client_ip_addr=client_ip_addr,
                connected_at=connected_at
            )

        result: list[dict] = list(map(remap_result, result))

    _**Note**: It may result resource expensive to remap large data collections from tuples to
    dictionaries, however, since at some point in our API flow data will be formatted into JSON
    therefore, short-cutting the output data processing may result handy._

1.  Extensions

    Extensions are commonly installed via migrations, however, it is possible to use them
    across queries sent by psycopg, for example [pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html) provide cryptographic APIs to increase the security of data stored and build HIPAA-compliant
    applications.

    Consider the following schema deployed in a migration:

        CREATE EXTENSION IF NOT EXISTS "pgcrypto";

        CREATE TABLE user_medications (
            uuid UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_uuid UUID NOT NULL,
            medication VARCHAR,
            dose BIGINT,
            unit VARCHAR,
            periodicity BIGINT,
            periodicity_unit VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );

    Insert new data via psycopg

        from connection import pool
        from config import env

        pgp_sym_key = env.PGP_SYM_KEY

        def insert_medication(medication_data: dict) -> list[tuple]:
            sql_query = """
                INSERT INTO user_medications (
                    user_uuid,
                    medication,
                    dose,
                    unit,
                    periodicity,
                    periodicity_unit,
                    created_at,
                    updated_at
                ) SELECT
                    gen_random_uuid(),
                    pgp_sym_encrypt(%(medication)s, %(pgp_sym_key)s),
                    %(dose)s,
                    pgp_sym_encrypt(%(unit)s, %(pgp_sym_key)s),
                    %(periodicity)s,
                    pgp_sym_encrypt(%(periodicity_unit)s, %(pgp_sym_key)s),
                    NOW(),
                    NOW()
                RETURNING *;
                """

                pool.execute(sql_query, medication_data)
                return pool.fetchall()

1.  Testing

        import pytest
        from connection import pool

        seed_up_sql = """
            CREATE EXTENSION "pgcrypto";
            CREATE TABLE users (
                uuid UUID,
                username VARCHAR,
                email VARCHAR,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                deleted_at TIMESTAMP
            );
            INSERT INTO users (uuid, username, email, created_at, updated_at)
            VALUES
            (gen_random_uuid(), '...', '...', NOW(), NOW()),
            (gen_random_uuid(), '...', '...', NOW(), NOW()),
            (gen_random_uuid(), '...', '...', NOW(), NOW()),
            (gen_random_uuid(), '...', '...', NOW(), NOW());
        """
        seed_down_sql = """
            DROP EXTENSION "pgcrypto";
            DROP TABLE users;
        """


        @pytest.fixture
        def seed():
            pool.execute(seed_up_sql)
            yield
            pool.execute(seed_down_sql)


        def test_counting_users(seed):
            sql = """
                SELECT COUNT(*) FROM users;
            """
            pool.execute(sql)
            result = pool.fetchall()

            assert result
            assert type(result) is list
            assert result[0][0] == 4
