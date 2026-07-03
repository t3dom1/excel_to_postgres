import psycopg2
from contextlib import contextmanager
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)

@contextmanager
def pg_conn(params):
    conn = psycopg2.connect(
        host=params['host'],
        port=params['port'],
        database=params['database'],
        user=params['user'],
        password=params['password']
    )
    try:
        yield conn
    finally:
        conn.close()

def create_table_with_columns(conn, table_name, columns):
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        
        columns_def = []
        for col in columns:
            if col == 'summa' or col == 'Сумма':
                columns_def.append(f"{col} NUMERIC(15,2)")
            elif col == 'chel' or col == 'Чел':
                columns_def.append(f"{col} INTEGER")
            else:
                columns_def.append(f"{col} VARCHAR(255)")
        
        create_sql = f"CREATE TABLE {table_name} ({', '.join(columns_def)})"
        cur.execute(create_sql)
        conn.commit()
        logger.info(f"Created table {table_name} with columns: {columns}")

def load_to_postgres(df_transformed, params, table_name):
    with pg_conn(params) as conn:
        create_table_with_columns(conn, table_name, df_transformed.columns.tolist())
        with conn.cursor() as cur:
            for _, row in df_transformed.iterrows():
                placeholders = ', '.join(['%s'] * len(row))
                cur.execute(f"INSERT INTO {table_name} ({', '.join(df_transformed.columns)}) VALUES ({placeholders})", tuple(row))
            conn.commit()

def log_to_db(status, stage, run_id, log_table, params, records=0, error=None, total_sum=0, message=None):
    try:
        with pg_conn(params) as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {log_table}
                    (run_id, status, stage, records_processed, total_sum, duration_seconds, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    run_id,
                    status,
                    stage,
                    records,
                    total_sum,
                    0,
                    error if error else message
                ))
                conn.commit()
    except Exception as e:
        logger.warning(f"Log failed: {e}")

def log_message_to_db(message, run_id, log_table, params, status='INFO'):
    try:
        with pg_conn(params) as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {log_table}
                    (run_id, status, stage, error_message)
                    VALUES (%s, %s, %s, %s)
                """, (
                    run_id,
                    status,
                    'SYSTEM',
                    message
                ))
                conn.commit()
    except Exception as e:
        logger.warning(f"Log to DB failed: {e}")