# Quick Start Guide

## 🎯 Demo Workflow

### For Presentations/Demos

1. **Pre-Demo Setup** (5 minutes before):
   ```bash
   # Start Docker services
   docker-compose up -d
   
   # Initialize fresh database
   python3 init_db.py
   
   # Start consumer
   python3 consumer.py
   ```

2. **During Demo**:
   ```bash
   # Terminal 1: Generate demo data
   python3 producer.py --users --count 50 --delay 0.5
   
   # Terminal 2: Start Streamlit app
   streamlit run app.py
   ```

3. **Demo Script**:
   - Show login/registration
   - Submit a live report
   - View safety maps (reports, routes, areas)
   - Show analytics dashboard
   - Demonstrate filters

4. **After Demo**:
   ```bash
   # Stop producer (Ctrl+C)
   # Stop consumer (Ctrl+C)
   # Stop Streamlit (Ctrl+C)
   # Stop Docker
   docker-compose down
   ```

## 📊 Default Demo Credentials

After running `init_db.py` and `producer.py --users`, these test accounts are available:

- **Username**: `user2` to `user31`
- **Email**: `user2@campus.com` to `user31@campus.com`
- **Password**: Auto-generated (check producer output or create your own account)

**Recommended**: Create your own account via the registration form for demos.

## 🔐 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | No | `localhost` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `DB_NAME` | No | `campus_safety` | Database name |
| `DB_USER` | No | `postgres` | Database user |
| `DB_PASSWORD` | **Yes** | - | Database password |
| `GEOAPIFY_API_KEY` | **Yes** | - | Geoapify API key |
| `KAFKA_BOOTSTRAP_SERVERS` | No | `localhost:29092` | Kafka servers |
| `MAX_DAILY_REPORTS` | No | `3` | Reports per user per day |
| `CAMPUS_LAT_MIN` | No | `-28.764947` | Campus boundary |
| `CAMPUS_LAT_MAX` | No | `-28.724177` | Campus boundary |
| `CAMPUS_LON_MIN` | No | `24.722326` | Campus boundary |
| `CAMPUS_LON_MAX` | No | `24.794486` | Campus boundary |

## 🐛 Common Issues & Solutions

### Issue: "GEOAPIFY_API_KEY not configured"
**Solution**: 
1. Get free API key at https://www.geoapify.com/
2. Add to `.env` file: `GEOAPIFY_API_KEY=your_key_here`

### Issue: "Database password not found"
**Solution**: 
1. Edit `.env` file
2. Set `DB_PASSWORD=your_secure_password`
3. Match password in `docker-compose.yml` if needed

### Issue: Docker containers won't start
**Solution**:
```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: Deletes data)
docker-compose down -v

# Restart
docker-compose up -d
```

### Issue: Port already in use
**Solution**:
```bash
# Find process using port 5432 (PostgreSQL)
lsof -i :5432

# Kill the process
kill -9 <PID>

# Or change port in .env
DB_PORT=5433
```

### Issue: Maps not loading
**Solution**:
- Check internet connection (maps use OpenStreetMap)
- Verify coordinates are valid
- Check browser console for errors

### Issue: "No module named 'dotenv'"
**Solution**:
```bash
pip3 install python-dotenv
```

## 📈 Performance Tips

### For Large Datasets
```python
# Limit reports displayed on maps
SELECT * FROM safety_reports 
ORDER BY created_at DESC 
LIMIT 1000;
```

### For Faster Loading
- Reduce `MAX_DAILY_REPORTS` for testing
- Use `--delay` parameter with producer
- Limit map zoom levels

## 🔄 Reset Everything

Complete fresh start:
```bash
# Stop and remove all containers
docker-compose down -v

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Reinstall dependencies
pip3 install -r requirements.txt

# Restart setup
./setup.sh
```

## 📱 Browser Compatibility

✅ **Supported**:
- Chrome/Chromium (Recommended)
- Firefox
- Safari
- Edge

⚠️ **Not Recommended**:
- Internet Explorer (not supported)
- Very old browser versions

## 🎓 Learning Resources

### Understanding the Tech Stack

**Streamlit**:
- Docs: https://docs.streamlit.io/
- Tutorial: https://docs.streamlit.io/get-started/tutorials

**Kafka**:
- Quickstart: https://kafka.apache.org/quickstart
- Concepts: https://kafka.apache.org/documentation/#intro_concepts

**PostgreSQL**:
- Tutorial: https://www.postgresql.org/docs/current/tutorial.html
- Commands: https://www.postgresql.org/docs/current/sql-commands.html

**Plotly**:
- Maps: https://plotly.com/python/maps/
- Dash: https://plotly.com/python/plotly-express/

## 🚀 Next Steps

After getting it running:

1. **Customize for your campus**:
   - Update coordinates in `.env`
   - Edit safe routes in `init_db.py`
   - Modify report types in `producer.py`

2. **Extend functionality**:
   - Add admin dashboard
   - Implement email notifications
   - Create mobile app
   - Add ML predictions

3. **Deploy to production**:
   - Set up HTTPS
   - Use managed PostgreSQL
   - Configure proper authentication
   - Set up monitoring

4. **Improve security**:
   - Enable SSL for database
   - Add rate limiting at gateway
   - Implement CAPTCHA
   - Add audit logging

## 💡 Pro Tips

- Use `tmux` or `screen` to manage multiple terminals
- Set up bash aliases for common commands
- Keep a separate `.env.dev` for development
- Document any changes you make
- Test with real campus coordinates for accuracy
- Back up database before major changes

## 📞 Getting Help

1. Check this guide first
2. Review README.md
3. Check GitHub issues
4. Read error messages carefully
5. Check Docker/Kafka logs
6. Verify environment variables

## 🎬 Recording a Demo

```bash
# Install screen recording tool
# macOS: Use QuickTime or ScreenFlow
# Linux: sudo apt-get install kazam
# Windows: Use OBS Studio

# Before recording:
1. Clear database (python3 init_db.py)
2. Generate fresh data (python3 producer.py --users --count 50)
3. Close unnecessary windows
4. Zoom browser to 125% for visibility
5. Prepare demo script

# During recording:
- Speak clearly
- Show each feature
- Demonstrate error handling
- Show the data flow (producer → consumer → app)
```

---

**Remember**: This is a demo/educational project. For production use, additional security hardening, testing, and infrastructure setup is required.🚀 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/campus-safety-dashboard.git
cd campus-safety-dashboard

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your credentials
nano .env  # or use your preferred editor

# 4. Run setup script
chmod +x setup.sh
./setup.sh

# 5. Start services (in 3 separate terminals)
# Terminal 1:
python3 consumer.py

# Terminal 2:
python3 producer.py --users --count 100

# Terminal 3:
streamlit run app.py
```

## 📋 Essential Commands

### Docker Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart postgres
```

### Database Operations
```bash
# Initialize/reset database
python3 init_db.py

# Connect to PostgreSQL
docker exec -it campus-safety-dashboard-postgres-1 psql -U postgres -d campus_safety

# Backup database
docker exec campus-safety-dashboard-postgres-1 pg_dump -U postgres campus_safety > backup.sql
```

### Kafka Operations
```bash
# List topics
docker exec campus-safety-dashboard-kafka-1 kafka-topics --list --bootstrap-server localhost:9092

# View messages in a topic
docker exec campus-safety-dashboard-kafka-1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic safety-reports-topic \
  --from-beginning
```

### Data Generation
```bash
# Generate 30 users
python3 producer.py --users

# Generate 100 reports
python3 producer.py --count 100

# Run for 5 minutes
python3 producer.py --duration 300

# Run continuously (Ctrl+C to stop)
python3 producer.py --continuous

# Custom delay between reports
python3 producer.py --count 50 --delay 1.0
```

## 🔧 Troubleshooting

### "Connection refused" Error
```bash
# Check if Docker services are running
docker-compose ps

# Restart services
docker-compose restart

# Check service logs
docker-compose logs postgres
docker-compose logs kafka
```

### "Module not found" Error
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall
```

### "Table does not exist" Error
```bash
# Reinitialize database
python3 init_db.py
```

### Producer/Consumer Not Working
```bash
# Check Kafka is running
docker-compose ps | grep kafka

# Verify topics exist
docker exec campus-safety-dashboard-kafka-1 kafka-topics --list --bootstrap-server localhost:9092

# Restart Kafka
docker-compose restart kafka zookeeper
```

### Streamlit Won't Start
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Clear Streamlit cache
rm -rf ~/.streamlit/

# Restart
streamlit run app.py
```

##