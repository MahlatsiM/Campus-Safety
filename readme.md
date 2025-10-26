# Campus Safety Dashboard 🚨

A real-time campus safety reporting platform built with Streamlit, Apache Kafka, and PostgreSQL. Students can report incidents, view interactive maps of safety reports, and track campus safety trends through an analytics dashboard.

## Features

- **🔐 Secure Authentication** - User registration, login, password reset with encrypted credentials
- **📍 Real-Time Incident Reporting** - Report safety concerns with precise geolocation
- **🗺️ Interactive Maps** - Visualize safety reports, safe routes, and secure areas
- **📊 Analytics Dashboard** - Track safety trends and statistics
- **⚡ Kafka Event Streaming** - Real-time data processing pipeline
- **🔒 Rate Limiting** - Prevents spam with daily report limits

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python, PostgreSQL
- **Streaming**: Apache Kafka + Zookeeper
- **Authentication**: Passlib (pbkdf2_sha256)
- **Geolocation**: Geoapify API
- **Visualization**: Plotly, Pandas
- **Infrastructure**: Docker Compose

## Architecture

```
User → Streamlit App → PostgreSQL
                    ↓
Producer → Kafka → Consumer → PostgreSQL
```

The system uses a dual-write pattern where:
1. User interactions write directly to PostgreSQL for immediate feedback
2. Kafka streams simulated data for testing and demo purposes

## Prerequisites

- Python 3.8+
- Docker & Docker Compose
- PostgreSQL 15
- Apache Kafka (via Docker)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/campus-safety-dashboard.git
cd campus-safety-dashboard
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campus_safety
DB_USER=postgres
DB_PASSWORD=your_secure_password_here

# Geoapify API
GEOAPIFY_API_KEY=your_api_key_here

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_CONSUMER_GROUP=campus-safety-consumer

# Application Settings
MAX_DAILY_REPORTS=3
```

**⚠️ IMPORTANT**: Never commit the `.env` file. It's already in `.gitignore`.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Docker Services

```bash
docker-compose up -d
```

This starts:
- Zookeeper (port 2181)
- Kafka (ports 9092, 29092)
- PostgreSQL (port 5432)

Verify services are running:
```bash
docker-compose ps
```

### 5. Initialize Database

```bash
python init_db.py
```

This creates:
- Tables (users, safety_reports, routes, green_areas)
- Sample safe routes
- Sample secure areas
- Initial data for testing

### 6. Run the Application

**Terminal 1 - Start Consumer** (processes Kafka messages):
```bash
python consumer.py
```

**Terminal 2 - Start Producer** (generates demo data):
```bash
python producer.py
```

**Terminal 3 - Start Streamlit App**:
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Project Structure

```
campus-safety-dashboard/
├── app.py                      # Main Streamlit application
├── auth/
│   └── auth_handlers.py        # Authentication logic
├── consumer.py                 # Kafka consumer
├── producer.py                 # Kafka producer (demo data)
├── init_db.py                  # Database initialization
├── schema.sql                  # Database schema
├── docker-compose.yml          # Docker services
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── .env.example                # Template for .env
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Usage

### First Time Setup

1. Navigate to the app at `http://localhost:8501`
2. Click "Create Account" in the sidebar
3. Register with your details
4. Login with your credentials

### Reporting an Incident

1. Login to the dashboard
2. Scroll to "Submit a New Safety Report"
3. Search for a location using the autocomplete
4. Select and confirm the location
5. Fill in report type and description
6. Submit the report

### Viewing Data

- **Safety Reports Map**: View all reported incidents
- **Safe Routes**: See recommended safe paths
- **Safe Areas**: View secure zones on campus
- **Analytics**: Track trends by report type

## Demo Mode

For presentations, the producer generates realistic fake data:

```bash
# Run producer for 5 minutes of demo data
python producer.py --duration 300
```

This creates:
- 30 simulated users
- Random safety reports every 3 seconds
- Realistic coordinates within campus bounds

## Configuration

### Rate Limiting

Modify `MAX_DAILY_REPORTS` in `.env` to change how many reports a user can submit per day (default: 3).

### Campus Boundaries

Edit coordinates in `producer.py`:

```python
LAT_MIN, LAT_MAX = -28.764947, -28.724177  # Your campus latitude range
LON_MIN, LON_MAX = 24.722326, 24.794486    # Your campus longitude range
```

### Safe Areas & Routes

Modify `init_db.py` to add your campus-specific locations:

```python
green_areas = [
    ("Security Office", -28.743554, 24.762580, 100, "security"),
    # Add your locations here
]
```

## API Keys

### Geoapify API

1. Sign up at [Geoapify](https://www.geoapify.com/)
2. Create a free API key
3. Add to `.env` file

Free tier includes:
- 3,000 requests/day
- Geocoding & autocomplete
- No credit card required

## Security Considerations

- ✅ Passwords hashed with pbkdf2_sha256
- ✅ SQL injection protection via parameterized queries
- ✅ Rate limiting on reports
- ✅ Environment variables for secrets
- ✅ Session state management
- ⚠️ **Production deployment requires HTTPS**
- ⚠️ **Use a proper secrets manager for production**
- ⚠️ **Enable database SSL in production**

## Troubleshooting

### "Connection refused" errors

```bash
# Check if Docker services are running
docker-compose ps

# Restart services
docker-compose restart
```

### "Table does not exist" errors

```bash
# Reinitialize database
python init_db.py
```

### Kafka consumer not receiving messages

```bash
# Check Kafka is running
docker-compose logs kafka

# Verify topics exist
docker exec -it campus-safety-dashboard-kafka-1 kafka-topics --list --bootstrap-server localhost:9092
```

### Producer hangs

The producer runs indefinitely by default. Stop with `Ctrl+C` or use:

```bash
python producer.py --count 100  # Generate 100 reports then stop
```

## Database Schema

### Users Table
- user_id (SERIAL PRIMARY KEY)
- username (UNIQUE)
- email (UNIQUE)
- hashed_password
- first_name, last_name
- created_at, last_seen

### Safety Reports Table
- report_id (SERIAL PRIMARY KEY)
- user_id (FK to users)
- report_type
- description
- latitude, longitude
- created_at

### Routes Table
- route_id (SERIAL PRIMARY KEY)
- start_lat, start_lon
- end_lat, end_lon

### Green Areas Table
- id (SERIAL PRIMARY KEY)
- name, type
- lat, lon, radius_meters

## Known Limitations

- Geolocation limited to Geoapify API free tier (3k requests/day)
- No mobile app (web responsive only)
- No real-time notifications (planned feature)
- Demo data is randomly generated (not real incidents)
- Single-node Kafka setup (not production-grade)

## Future Enhancements

- [ ] Push notifications for nearby incidents
- [ ] Mobile app (React Native)
- [ ] ML-based risk prediction
- [ ] Integration with campus security systems
- [ ] Multi-campus support
- [ ] Anonymous reporting option
- [ ] Admin dashboard for security personnel

## Contributing

This is an academic project. Contributions welcome for educational purposes.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Geoapify for geolocation services
- Streamlit for the rapid prototyping framework
- Apache Kafka for event streaming

## Support & Contact

For issues, questions, or demo requests:
- Open an issue on GitHub
- Email: mahlatsimm1510@gmail.com

## Deployment Notes

**DO NOT deploy to production without:**
1. Proper SSL/TLS certificates
2. Secrets management (AWS Secrets Manager, HashiCorp Vault)
3. Database backup strategy
4. Load balancer for Streamlit
5. Multi-broker Kafka cluster
6. Monitoring & alerting (Prometheus, Grafana)
7. Rate limiting at application gateway level
8. GDPR/privacy compliance review

This is a demo application. Treat it as such.

---

**Remember**: Your database password and API keys should NEVER be in your code or committed to version control. Always use environment variables.
