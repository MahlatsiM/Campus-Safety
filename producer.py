#!/usr/bin/env python3
"""
Kafka Producer for Campus Safety Dashboard.
Generates demo data (users and safety reports) and publishes to Kafka topics.
"""

import json
import random
import time
import argparse
import os
import secrets
from kafka import KafkaProducer
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================
# Configuration
# =========================
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:29092')

# Campus boundaries (from environment or defaults)
LAT_MIN = float(os.getenv('CAMPUS_LAT_MIN', -28.764947))
LAT_MAX = float(os.getenv('CAMPUS_LAT_MAX', -28.724177))
LON_MIN = float(os.getenv('CAMPUS_LON_MIN', 24.722326))
LON_MAX = float(os.getenv('CAMPUS_LON_MAX', 24.794486))

# =========================
# Kafka setup
# =========================
print(f"🔌 Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("✅ Kafka producer initialized successfully!")
except Exception as e:
    print(f"❌ Failed to connect to Kafka: {e}")
    print("💡 Make sure Kafka is running: docker-compose up -d")
    exit(1)

# =========================
# Constants
# =========================
REPORT_TYPES = [
    "Harassment", "Sexual Assault", "Assault",
    "Hazard", "Theft", "Suspicious Activity", 
    "Vandalism", "Other"
]

# Generate 30 demo users
USER_IDS = list(range(2, 32))

# =========================
# Data Generators
# =========================
def generate_user(user_id):
    """Generate a demo user with realistic data."""
    username = f"user{user_id}"
    email = f"{username}@campus.com"
    first_name = f"Student{user_id}"
    last_name = f"Demo{user_id}"
    password = secrets.token_urlsafe(8)
    hashed_password = pbkdf2_sha256.hash(password)

    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "hashed_password": hashed_password,
        "created_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat()
    }


def generate_random_report():
    """Generate a fake safety report with realistic coordinates."""
    return {
        "user_id": random.choice(USER_IDS),
        "report_type": random.choice(REPORT_TYPES),
        "description": f"Auto-generated {random.choice(REPORT_TYPES).lower()} report for demo purposes.",
        "latitude": round(random.uniform(LAT_MIN, LAT_MAX), 6),
        "longitude": round(random.uniform(LON_MIN, LON_MAX), 6),
        "created_at": datetime.now().isoformat()
    }

# =========================
# Main Producer Logic
# =========================
def main(args):
    """Run the producer with specified parameters."""
    
    print("\n" + "="*60)
    print("🚀 CAMPUS SAFETY DEMO DATA GENERATOR")
    print("="*60)
    
    # 1️⃣ Produce users first (once)
    if args.users:
        print("\n👥 Generating demo users...")
        for user_id in USER_IDS:
            user = generate_user(user_id)
            producer.send("users-topic", user)
            print(f"   ✅ User {user_id}: {user['username']} ({user['email']})")
            time.sleep(0.05)
        
        producer.flush()
        print(f"\n✅ All {len(USER_IDS)} users produced successfully!")
    
    # 2️⃣ Produce reports
    if args.count:
        print(f"\n📍 Generating {args.count} safety reports...")
        for i in range(args.count):
            report = generate_random_report()
            producer.send("safety-reports-topic", report)
            print(f"   {i+1}/{args.count}: {report['report_type']} at ({report['latitude']:.4f}, {report['longitude']:.4f})")
            time.sleep(args.delay)
        
        producer.flush()
        print(f"\n✅ All {args.count} reports produced successfully!")
    
    elif args.duration:
        print(f"\n📍 Generating reports for {args.duration} seconds...")
        print("   Press Ctrl+C to stop early\n")
        
        start_time = time.time()
        report_count = 0
        
        try:
            while (time.time() - start_time) < args.duration:
                report = generate_random_report()
                producer.send("safety-reports-topic", report)
                report_count += 1
                print(f"   Report #{report_count}: {report['report_type']} from user {report['user_id']}")
                producer.flush()
                time.sleep(args.delay)
        
        except KeyboardInterrupt:
            print("\n\n⏸️  Stopped by user")
        
        elapsed = time.time() - start_time
        print(f"\n✅ Generated {report_count} reports in {elapsed:.1f} seconds")
        print(f"   Average: {report_count/elapsed:.2f} reports/second")
    
    elif args.continuous:
        print("\n♾️  Continuous mode: Generating reports indefinitely...")
        print("   Press Ctrl+C to stop\n")
        
        report_count = 0
        
        try:
            while True:
                report = generate_random_report()
                producer.send("safety-reports-topic", report)
                report_count += 1
                print(f"   Report #{report_count}: {report['report_type']} from user {report['user_id']}")
                producer.flush()
                time.sleep(args.delay)
        
        except KeyboardInterrupt:
            print(f"\n\n⏸️  Stopped by user after {report_count} reports")
    
    print("\n" + "="*60)
    print("✅ Producer finished successfully!")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate demo data for Campus Safety Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 30 users and 100 reports
  python producer.py --users --count 100
  
  # Generate reports for 5 minutes
  python producer.py --duration 300
  
  # Generate reports continuously (for demos)
  python producer.py --continuous
  
  # Generate users only
  python producer.py --users
  
  # Generate 50 reports with 1 second delay
  python producer.py --count 50 --delay 1.0
        """
    )
    
    parser.add_argument(
        '--users',
        action='store_true',
        help='Generate demo users (30 users)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        help='Number of reports to generate (then stop)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        help='Run for N seconds (then stop)'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run indefinitely until stopped with Ctrl+C'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=0.3,
        help='Delay between reports in seconds (default: 0.3)'
    )
    
    args = parser.parse_args()
    
    # Validation
    if not (args.users or args.count or args.duration or args.continuous):
        parser.error("Must specify at least one of: --users, --count, --duration, or --continuous")
    
    if sum([bool(args.count), bool(args.duration), args.continuous]) > 1:
        parser.error("Can only specify one of: --count, --duration, or --continuous")
    
    try:
        main(args)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)