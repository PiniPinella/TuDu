# === TuDu_App CONFIG MIT USER EINGABE ================================================================

# db_config.py

db_config = {
    'host': 'localhost',
    'port': 5433,
    'dbname': 'TuDu',
    'user': 'postgres',
    'password': 'postgres'
}

def get_connection():
    import psycopg2
    return psycopg2.connect(**db_config)
