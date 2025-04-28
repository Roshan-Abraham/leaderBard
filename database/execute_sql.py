"""
Execute SQL script for database initialization.
This script reads the SQL file and executes it using Python's database connection.
"""
import os
import sys
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_db_connection():
    """Get database connection based on environment variables."""
    db_type = os.environ.get('DB_TYPE', 'sqlite').lower()
    
    if db_type == 'postgres':
        # PostgreSQL connection
        pg_host = os.environ.get('POSTGRES_HOST', 'db')
        pg_port = os.environ.get('POSTGRES_PORT', '5432')
        pg_user = os.environ.get('POSTGRES_USER', 'dashboard_user')
        pg_password = os.environ.get('POSTGRES_PASSWORD', 'dashboard_password')
        pg_database = os.environ.get('POSTGRES_DB', 'dashboard')
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            password=pg_password,
            database=pg_database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn, 'postgres'
    else:
        # SQLite connection
        db_path = os.environ.get('DB_PATH', 'data/dashboard.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return sqlite3.connect(db_path), 'sqlite'

def execute_sql_file(sql_file_path):
    """Read and execute SQL file.
    
    Args:
        sql_file_path: Path to the SQL file
    """
    # Get database connection
    conn, db_type = get_db_connection()
    
    # Read SQL file
    with open(sql_file_path, 'r') as sql_file:
        sql_script = sql_file.read()
    
    # Split script into statements for PostgreSQL
    if db_type == 'postgres':
        # Filter out commented lines and handle Postgres-specific syntax
        statements = []
        current_statement = []
        for line in sql_script.split('\n'):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue
            # Remove SQLite-specific AUTOINCREMENT keyword for PostgreSQL
            if 'AUTOINCREMENT' in line:
                line = line.replace('AUTOINCREMENT', '')
            
            current_statement.append(line)
            if line.endswith(';'):
                statements.append(' '.join(current_statement))
                current_statement = []
        
        # Execute each statement
        cursor = conn.cursor()
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"Error executing statement: {statement}")
                    print(f"Error message: {e}")
                    # Continue execution despite errors
    else:
        # For SQLite, we can execute the entire script at once
        conn.executescript(sql_script)
    
    conn.commit()
    conn.close()
    
    print(f"SQL script at {sql_file_path} executed successfully.")

if __name__ == "__main__":
    # Get SQL file path
    sql_file_path = os.path.join(os.path.dirname(__file__), 'init_db.sql')
    
    if not os.path.exists(sql_file_path):
        print(f"Error: SQL file not found at {sql_file_path}")
        sys.exit(1)
    
    print(f"Executing SQL script: {sql_file_path}")
    execute_sql_file(sql_file_path)
    print("Database initialization complete.")
