import json
import psycopg2
from kafka import KafkaConsumer
from datetime import datetime

# =========================
# Kafka setup
# =========================
consumer = KafkaConsumer(
    'users-topic',
    'safety-reports-topic',
    bootstrap_servers='localhost:29092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='campus-safety-consumer'
)

# =========================
# PostgreSQL connection
# =========================
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='campus_safety',
    user='postgres',
    password='Mahlatsi#0310'
)
cursor = conn.cursor()

# =========================
# Helper functions
# =========================
def insert_user(user):
    """Insert a user into the users table, ignoring duplicates."""
    query = """
    INSERT INTO users (
        user_id, username, email, first_name, last_name,
        hashed_password, is_admin, created_at, last_seen
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            user['is_admin'],
            user['created_at'],
            user['last_seen']
        ))
        conn.commit()
        print(f"🧑‍🎓 Inserted user: {user['username']}")
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
        # Ensure user_id is string to match the user table
        user_id_str = str(report['user_id'])
        cursor.execute(query, (
            user_id_str,
            report['report_type'],
            report['description'],
            report['latitude'],
            report['longitude'],
            report['created_at']
        ))
        conn.commit()
        print(f"📍 Inserted report from user {user_id_str}")
    except Exception as e:
        print(f"❌ Failed to insert report from user {report.get('user_id')}: {e}")
        conn.rollback()

# =========================
# Main consumption loop
# =========================
try:
    print("🚀 Consumer started. Listening to Kafka topics...")
    for message in consumer:
        topic = message.topic
        data = message.value

        if topic == 'users-topic':
            insert_user(data)
        elif topic == 'safety-reports-topic':
            insert_report(data)

except KeyboardInterrupt:
    print("\n🛑 Consumer stopped by user.")

finally:
    cursor.close()
    conn.close()
    print("✅ PostgreSQL connection closed.")
