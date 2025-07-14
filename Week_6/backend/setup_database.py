#!/usr/bin/env python3
"""
Database setup script for Spotify Clone backend.
This script helps create the database and test the connection.
"""

import psycopg2
import sys
import os

def test_connection(connection_string):
    """Test database connection with given connection string."""
    try:
        conn = psycopg2.connect(connection_string)
        print(f"✅ Successfully connected with: {connection_string}")
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"❌ Failed to connect with: {connection_string}")
        print(f"   Error: {e}")
        return False

def create_database(connection_string, db_name):
    """Create the database if it doesn't exist."""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print(f"✅ Database '{db_name}' already exists")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def main():
    print("🔧 Spotify Clone Database Setup")
    print("=" * 40)
    
    # Common connection strings to try
    connection_strings = [
        "postgresql://postgres@localhost:5464/postgres",
        "postgresql://postgres:postgres@localhost:5464/postgres",
        "postgresql://postgres:admin@localhost:5464/postgres",
        "postgresql://postgres:password@localhost:5464/postgres",
        "postgresql://postgres:123456@localhost:5464/postgres",
    ]
    
    print("Testing database connections...")
    working_connection = None
    
    for conn_str in connection_strings:
        if test_connection(conn_str):
            working_connection = conn_str
            break
    
    if not working_connection:
        print("\n❌ Could not connect to PostgreSQL with any of the common passwords.")
        print("Please provide your PostgreSQL password:")
        password = input("Password: ").strip()
        if password:
            working_connection = f"postgresql://postgres:{password}@localhost:5464/postgres"
            if not test_connection(working_connection):
                print("❌ Still cannot connect. Please check your PostgreSQL setup.")
                return
        else:
            print("❌ No password provided. Exiting.")
            return
    
    print(f"\n✅ Using connection: {working_connection}")
    
    # Create the spotify_clone database
    print("\nCreating spotify_clone database...")
    if create_database(working_connection, "spotify_clone"):
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Update your alembic.ini and session.py with the working connection string")
        print("2. Run: venv/Scripts/python -m alembic revision --autogenerate -m 'Initial schema'")
        print("3. Run: venv/Scripts/python -m alembic upgrade head")
    else:
        print("\n❌ Failed to create database.")

if __name__ == "__main__":
    main() 