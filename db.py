import os
from psycopg import connect
from psycopg.rows import dict_row

def get_conn():
    """
    Crea y devuelve una conexión a PostgreSQL usando variables de entorno.
    """
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "postgres")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")

    return connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        row_factory=dict_row,  # si luego queremos rows como dict
    )
