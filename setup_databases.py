"""
Database Setup Script for BSU Kiosk System
Automates database creation and initial setup
"""

import psycopg2
import pymysql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_postgresql_databases():
    """Setup PostgreSQL databases for LostLink and Grievance"""
    print("="*60)
    print("Setting up PostgreSQL databases...")
    print("="*60)
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password=input("Enter PostgreSQL password: ")
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create LostLink database
        print("\n[1/2] Creating LostLink database...")
        try:
            cursor.execute("CREATE DATABASE \"LostLink\"")
            print("✓ LostLink database created")
        except psycopg2.errors.DuplicateDatabase:
            print("! LostLink database already exists")
        
        # Create Grievance database
        print("[2/2] Creating Grievance database...")
        try:
            cursor.execute("CREATE DATABASE grievance_system")
            print("✓ Grievance database created")
        except psycopg2.errors.DuplicateDatabase:
            print("! Grievance database already exists")
        
        cursor.close()
        conn.close()
        print("\n✓ PostgreSQL setup completed!")
        return True
        
    except Exception as e:
        print(f"\n✗ PostgreSQL setup failed: {e}")
        return False

def setup_mysql_database():
    """Setup MySQL database for RGO"""
    print("\n" + "="*60)
    print("Setting up MySQL database...")
    print("="*60)
    
    try:
        # Connect to MySQL
        password = input("Enter MySQL root password (press Enter if none): ")
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password=password
        )
        cursor = conn.cursor()
        
        # Create RGO database
        print("\n[1/1] Creating RGO database...")
        try:
            cursor.execute("CREATE DATABASE rgo_system")
            print("✓ RGO database created")
        except pymysql.err.DatabaseError:
            print("! RGO database already exists")
        
        cursor.close()
        conn.close()
        print("\n✓ MySQL setup completed!")
        return True
        
    except Exception as e:
        print(f"\n✗ MySQL setup failed: {e}")
        return False

def create_lostlink_tables():
    """Create tables for LostLink database"""
    print("\n" + "="*60)
    print("Creating LostLink tables...")
    print("="*60)
    
    try:
        password = input("Enter PostgreSQL password: ")
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password=password,
            database="LostLink"
        )
        cursor = conn.cursor()
        
        # Users table
        print("\n[1/3] Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                sr_code VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                surname VARCHAR(255) NOT NULL,
                age INTEGER NOT NULL,
                email VARCHAR(255) NOT NULL,
                contact VARCHAR(20) NOT NULL,
                gender VARCHAR(20) NOT NULL,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(255) NOT NULL
            )
        """)
        print("✓ Users table created")
        
        # Reports table
        print("[2/3] Creating reports table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                item VARCHAR(255) NOT NULL,
                place VARCHAR(255) NOT NULL,
                photo VARCHAR(255) NOT NULL,
                description VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW(),
                report_by VARCHAR(255) REFERENCES users(sr_code)
            )
        """)
        print("✓ Reports table created")
        
        # Returns table
        print("[3/3] Creating returns table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                id SERIAL PRIMARY KEY,
                item_id INTEGER REFERENCES reports(id) ON DELETE CASCADE,
                item_name VARCHAR(255) NOT NULL,
                place_found VARCHAR(255) NOT NULL,
                photo VARCHAR(255) NOT NULL,
                description VARCHAR(255) NOT NULL,
                claimed_by VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                contact VARCHAR(50) NOT NULL,
                timestamp_claimed TIMESTAMP DEFAULT NOW()
            )
        """)
        print("✓ Returns table created")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("\n✓ LostLink tables created successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ LostLink table creation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("BSU KIOSK SYSTEM - DATABASE SETUP WIZARD")
    print("="*60)
    print("\nThis script will help you set up all databases for the system.")
    print("Make sure PostgreSQL and MySQL servers are running!\n")
    
    input("Press Enter to continue...")
    
    # Setup PostgreSQL
    if setup_postgresql_databases():
        create_lostlink_tables()
    
    # Setup MySQL
    setup_mysql_database()
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update .env file with your database credentials")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: python app.py")
    print("\nFor detailed instructions, see README.md")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
