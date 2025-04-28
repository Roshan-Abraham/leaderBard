"""
Database adapter for supporting both SQLite and PostgreSQL databases.
"""
import os
import sqlite3
import json
import psycopg2
from psycopg2.extras import DictCursor
from typing import Dict, List, Any, Optional, Union, Tuple


class DatabaseAdapter:
    """Database adapter for different database backends."""
    
    def __init__(self):
        """Initialize the database adapter based on environment variables."""
        # Check for PostgreSQL connection info
        self.pg_host = os.environ.get('POSTGRES_HOST', 'db')
        self.pg_port = os.environ.get('POSTGRES_PORT', '5432')
        self.pg_user = os.environ.get('POSTGRES_USER', 'dashboard_user')
        self.pg_password = os.environ.get('POSTGRES_PASSWORD', 'dashboard_password')
        self.pg_database = os.environ.get('POSTGRES_DB', 'dashboard')
        
        # SQLite path
        self.sqlite_path = os.environ.get('DB_PATH', 'data/dashboard.db')
        
        # Determine database type
        self.db_type = os.environ.get('DB_TYPE', 'sqlite').lower()
        
        # Initialize connection
        self.connection = None
    
    def get_connection(self):
        """Get a database connection based on the configured type."""
        if self.db_type == 'postgres':
            if self.connection is None or self.connection.closed:
                self.connection = psycopg2.connect(
                    host=self.pg_host,
                    port=self.pg_port,
                    user=self.pg_user,
                    password=self.pg_password,
                    database=self.pg_database
                )
            return self.connection
        else:  # Default to SQLite
            return sqlite3.connect(self.sqlite_path)
    
    def execute_query(self, query: str, params: Tuple = None, fetch_type: str = 'all'):
        """Execute a query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_type: Type of fetch ('all', 'one', 'none')
            
        Returns:
            Query results based on fetch_type
        """
        if self.db_type == 'postgres':
            # PostgreSQL
            conn = self.get_connection()
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params if params else ())
                
                if fetch_type == 'all':
                    results = cursor.fetchall()
                    # Convert to list of dicts
                    return [dict(row) for row in results] if results else []
                elif fetch_type == 'one':
                    result = cursor.fetchone()
                    return dict(result) if result else None
                else:  # 'none'
                    conn.commit()
                    return cursor.rowcount if cursor.rowcount > 0 else None
        else:
            # SQLite
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params if params else ())
            
            if fetch_type == 'all':
                results = cursor.fetchall()
                # Convert to list of dicts
                return [dict(row) for row in results] if results else []
            elif fetch_type == 'one':
                result = cursor.fetchone()
                return dict(result) if result else None
            else:  # 'none'
                conn.commit()
                rowcount = cursor.rowcount
                cursor.close()
                return rowcount if rowcount > 0 else None
    
    def execute_script(self, script: str):
        """Execute a SQL script.
        
        Args:
            script: SQL script string
        """
        if self.db_type == 'postgres':
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(script)
                conn.commit()
        else:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
            cursor.close()
    
    def get_last_insert_id(self, table_name: str = None):
        """Get the ID of the last inserted row.
        
        Args:
            table_name: Table name (required for PostgreSQL)
            
        Returns:
            Last insert ID
        """
        if self.db_type == 'postgres' and table_name:
            query = f"SELECT currval(pg_get_serial_sequence('{table_name}', 'id'))"
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else None
        elif self.db_type != 'postgres':
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT last_insert_rowid()")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        return None
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
