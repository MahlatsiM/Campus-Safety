#!/usr/bin/env python3
"""
Kafka Consumer for Campus Safety Dashboard.
Consumes user and safety report events from Kafka topics and writes to PostgreSQL.
"""

import json
import psycopg2
import os
from kafka import KafkaConsumer
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================
# Configuration
# =========================
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:29092')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP', 'campus-safety-consumer')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'campus_safety'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}

# =========================
# Kafka setup
# =========================
print(f"🔌 Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")

consumer = KafkaConsumer(
    'users-topic',
    'safety-reports-topic',
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=KAFKA_CONSUMER_GROUP
)

print("✅ Kafka consumer initialized successfully!")

# =========================
# PostgreSQL connection
# =========================
print(f"🔌 Connecting to PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}...")

if not DB_CONFIG['password']:
    print("❌ ERROR: DB_PASSWORD not found in environment variables!")
    print("📝 Create a .env file based on .env.example")
    exit(1)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ PostgreSQL connection established!")
except Exception as e:
    print(f"❌ Failed to connect to PostgreSQL: {e}")
    exit(1)

# =========================
# Helper functions
# =========================
def insert_user(user):
    """Insert a user into the users table, ignoring duplicates."""
    query = """
    INSERT INTO users (
        user_id, username, email, first_name, last_name,
        hashed_password, created_at, last_seen
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (user_id) DO NOTHING;
    """
    try:
        cursor.execute(query, (
            user['user_id'],
            user['username'],
            user['email'],
            user['first_name'],
            user['last_name'],
            user['hashed_password'],
            user['created_at'],
            user['last_seen']
        ))
        conn.commit()
        print(f"🧑‍🎓 Inserted user: {user['username']} (ID: {user['user_id']})")
    except Exception as e:
        print(f"❌ Failed to insert user {user.get('username')}: {e}")
        conn.rollback()

def insert_report(report):
    """Insert a report into the safety_reports table."""
    query = """
    INSERT INTO safety_reports (
        user_id, report_type, description, latitude, longitude, created_at
    ) VALUES (%s, %s, %s, %s, %s, %s);
    """
    try:
        # Ensure user_id is integer to match the user table
        user_id = int(report['user_id'])
        cursor.execute(query, (
            user_id,
            report['report_type'],
            report['description'],
            report['latitude'],
            report['longitude'],
            report['created_at']
        ))
        conn.commit()
        print(f"📍 Inserted report: {report['report_type']} from user {user_id}")
    except Exception as e:
        print(f"❌ Failed to insert report from user {report.get('user_id')}: {e}")
        conn.rollback()

# =========================
# Main consumption loop
# =========================
try:
    print("\n" + "="*60)
    print("🚀 Consumer started. Listening to Kafka topics...")
    print("   - users-topic")
    print("   - safety-reports-topic")
    print("="*60)
    print("\nPress Ctrl+C to stop.\n")
    
    message_count = 0
    
    for message in consumer:
        topic = message.topic
        data = message.value
        message_count += 1

        if topic == 'users-topic':
            insert_user(data)
        elif topic == 'safety-reports-topic':
            insert_report(data)
        
        # Print progress every 10 messages
        if message_count % 10 == 0:
            print(f"📊 Processed {message_count} messages so far...")

except KeyboardInterrupt:
    print("\n\n🛑 Consumer stopped by user.")
    print(f"📊 Total messages processed: {message_count}")

except Exception as e:
    print(f"\n❌ Consumer error: {e}")

finally:
    print("\n🔒 Closing connections...")
    cursor.close()
    conn.close()
    consumer.close()
    print("✅ All connections closed.")