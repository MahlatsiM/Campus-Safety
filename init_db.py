#!/usr/bin/env python3
"""
Database initialization script for Campus Safety Dashboard.
Creates tables and populates with initial demo data.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'campus_safety'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}

def init_database():
    """Initialize database with schema and sample data."""
    
    print("🔌 Connecting to PostgreSQL...")
    
    # First connect to default postgres database to create our database if it doesn't exist
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        
        if not cursor.fetchone():
            print(f"📦 Creating database '{DB_CONFIG['database']}'...")
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Database '{DB_CONFIG['database']}' created successfully!")
        else:
            print(f"✅ Database '{DB_CONFIG['database']}' already exists.")
        
        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    # Now connect to our campus_safety database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n🏗️  Creating tables...")
        
        # Read and execute schema
        with open('schema.sql', 'r') as f:
            schema = f.read()
            cursor.execute(schema)
        
        print("✅ Tables created successfully!")
        
        # Insert sample safe routes
        print("\n🛣️  Adding sample safe routes...")
        routes = [
            # Main campus routes
            (-28.743554, 24.762580, -28.745000, 24.765000),  # Library to Admin
            (-28.745000, 24.765000, -28.750000, 24.770000),  # Admin to Sports Complex
            (-28.750000, 24.770000, -28.755000, 24.775000),  # Sports to Residence
            (-28.743554, 24.762580, -28.740000, 24.760000),  # Library to Cafeteria
            (-28.740000, 24.760000, -28.738000, 24.758000),  # Cafeteria to Parking
        ]
        
        for route in routes:
            cursor.execute(
                """
                INSERT INTO routes (start_lat, start_lon, end_lat, end_lon)
                VALUES (%s, %s, %s, %s)
                """,
                route
            )
        
        print(f"✅ Added {len(routes)} safe routes!")
        
        # Insert sample green/safe areas
        print("\n🟢 Adding sample safe areas...")
        green_areas = [
            ("Main Security Office", -28.743554, 24.762580, 150, "security"),
            ("Library Safe Zone", -28.744000, 24.763000, 100, "campus"),
            ("Sports Complex Security", -28.750000, 24.770000, 120, "security"),
            ("Student Center", -28.741000, 24.761000, 80, "campus"),
            ("Emergency Call Point - Parking", -28.738000, 24.758000, 50, "emergency"),
            ("Emergency Call Point - Residence", -28.755000, 24.775000, 50, "emergency"),
            ("Well-Lit Path - Main Quad", -28.746000, 24.764000, 200, "campus"),
        ]
        
        for area in green_areas:
            cursor.execute(
                """
                INSERT INTO green_areas (name, lat, lon, radius_meters, type)
                VALUES (%s, %s, %s, %s, %s)
                """,
                area
            )
        
        print(f"✅ Added {len(green_areas)} safe areas!")
        
        # Commit all changes
        conn.commit()
        
        # Display summary
        cursor.execute("SELECT COUNT(*) FROM routes")
        route_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM green_areas")
        area_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM safety_reports")
        report_count = cursor.fetchone()[0]
        
        print("\n" + "="*50)
        print("📊 DATABASE INITIALIZATION SUMMARY")
        print("="*50)
        print(f"Safe Routes:     {route_count}")
        print(f"Safe Areas:      {area_count}")
        print(f"Users:           {user_count}")
        print(f"Safety Reports:  {report_count}")
        print("="*50)
        print("\n✅ Database initialized successfully!")
        print("\n📝 Next steps:")
        print("   1. Start Docker services: docker-compose up -d")
        print("   2. Run consumer: python consumer.py")
        print("   3. Run producer: python producer.py")
        print("   4. Start app: streamlit run app.py")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        if conn:
            conn.rollback()
        return False

if __name__ == "__main__":
    if not os.getenv('DB_PASSWORD'):
        print("❌ ERROR: DB_PASSWORD not found in environment variables!")
        print("📝 Create a .env file based on .env.example")
        exit(1)
    
    success = init_database()
    exit(0 if success else 1)