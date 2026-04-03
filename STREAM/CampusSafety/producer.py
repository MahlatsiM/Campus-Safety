import json
import random
import time
import uuid
import string
import hashlib
from kafka import KafkaProducer
from datetime import datetime
import secrets
from passlib.hash import pbkdf2_sha256

# =========================
# Kafka setup
# =========================
producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# =========================
# Constants
# =========================
LAT_MIN, LAT_MAX = -28.764947, -28.724177
LON_MIN, LON_MAX = 24.722326, 24.794486

REPORT_TYPES = [
    "Harassment", "Sexual Assault", "Assault",
    "Hazard", "Theft", "Suspicious Activity", "Other"
]

# Generate 30 users
USER_IDS = list(range(2, 31))

# =========================
# Utility Functions
# =========================
def generate_random_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def hash_password(password):
    # Simple SHA256 hashing (for simulated data only)
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# Data Generators
# =========================
def generate_user(user_id):
    user_id_str = str(user_id)  # ensure string
    username = f"user{user_id_str}"
    email = f"{username}@campus.com"
    first_name = f"First{user_id_str[-2:]}"
    last_name = f"Last{user_id_str[-2:]}"
    password = secrets.token_urlsafe(8)
    hashed_password = pbkdf2_sha256.hash(password)

    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "hashed_password": hashed_password,
        "is_admin": False,
        "created_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat()
    }


def generate_random_report():
    """Generate a fake safety report."""
    used_numbers = set()

    def generate_unique_number():
        while True:
            num = random.randint(100000, 999999)
            if num not in used_numbers:
                used_numbers.add(num)
                return num
    return {
        "report_id": generate_unique_number(),
        "user_id": random.choice(USER_IDS),
        "report_type": random.choice(REPORT_TYPES),
        "description": "Auto-generated report for simulation purposes.",
        "latitude": round(random.uniform(LAT_MIN, LAT_MAX), 6),
        "longitude": round(random.uniform(LON_MIN, LON_MAX), 6),
        "created_at": datetime.now().isoformat()
    }

# =========================
# Main Producer Logic
# =========================
if __name__ == "__main__":
    # 1️⃣ Produce users first (once)
    for user_id in USER_IDS:
        user = generate_user(user_id)
        producer.send("users-topic", user)
        print(f"🧑‍🎓 Produced user: {user['username']} ({user['email']})")
        time.sleep(0.1)

    producer.flush()
    print("✅ All users produced successfully.")
    print("🚀 Starting continuous report generation...")

    # 2️⃣ Then continuously produce reports
    while True:
        report = generate_random_report()
        producer.send("safety-reports-topic", report)
        producer.flush()
        print(f"📍 Produced report: {report}")
        time.sleep(0.3)
