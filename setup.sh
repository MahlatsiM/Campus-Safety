#!/bin/bash

# Campus Safety Dashboard - Setup Script
# This script automates the initial setup and verification

set -e  # Exit on error

echo "========================================"
echo "🚨 Campus Safety Dashboard Setup"
echo "========================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo ""
    echo "Creating .env from .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your:${NC}"
        echo "   1. Database password (DB_PASSWORD)"
        echo "   2. Geoapify API key (GEOAPIFY_API_KEY)"
        echo ""
        echo "Get a free Geoapify key at: https://www.geoapify.com/"
        echo ""
        read -p "Press Enter after you've configured .env..."
    else
        echo -e "${RED}❌ .env.example not found!${NC}"
        exit 1
    fi
fi

# Check if required variables are set
echo "🔍 Checking environment variables..."
source .env

if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "your_secure_password_here" ]; then
    echo -e "${RED}❌ DB_PASSWORD not configured in .env${NC}"
    exit 1
fi

if [ -z "$GEOAPIFY_API_KEY" ] || [ "$GEOAPIFY_API_KEY" = "your_geoapify_api_key_here" ]; then
    echo -e "${RED}❌ GEOAPIFY_API_KEY not configured in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables configured${NC}"
echo ""

# Check if Docker is running
echo "🐳 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "Please start Docker and run this script again."
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Check if Python is installed
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found!${NC}"
    exit 1
fi
echo ""

# Start Docker services
echo "🚀 Starting Docker services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Docker services started${NC}"
else
    echo -e "${RED}❌ Failed to start Docker services${NC}"
    docker-compose logs
    exit 1
fi
echo ""

# Initialize database
echo "🗃️  Initializing database..."
if python3 init_db.py; then
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    echo -e "${RED}❌ Database initialization failed${NC}"
    exit 1
fi
echo ""

# Summary
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "📋 Next steps:"
echo ""
echo "1️⃣  Start the Kafka consumer (Terminal 1):"
echo "   python3 consumer.py"
echo ""
echo "2️⃣  Start the data producer (Terminal 2):"
echo "   python3 producer.py --users --count 50"
echo ""
echo "3️⃣  Start the Streamlit app (Terminal 3):"
echo "   streamlit run app.py"
echo ""
echo "4️⃣  Open your browser:"
echo "   http://localhost:8501"
echo ""
echo "🛠️  Useful commands:"
echo "   - View Docker logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Reset database: python3 init_db.py"
echo ""
echo "📖 For more info, see README.md"
echo "========================================"