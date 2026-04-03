-- ===============================
-- USERS TABLE
-- ===============================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    hashed_password TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_until TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);

-- ===============================
-- SAFETY REPORTS
-- ===============================
CREATE TABLE safety_reports (
    report_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,
    description TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending'
);

-- ===============================
-- SAFE ROUTES
-- ===============================
CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    start_lat DOUBLE PRECISION NOT NULL,
    start_lon DOUBLE PRECISION NOT NULL,
    end_lat DOUBLE PRECISION NOT NULL,
    end_lon DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- SAFE AREAS (GREEN ZONES)
-- ===============================
CREATE TABLE green_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    radius_meters INTEGER NOT NULL,
    type VARCHAR(50) DEFAULT 'safe',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===============================
-- REPORT LOGS (for temporal blocking)
-- ===============================
CREATE TABLE report_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    report_id INTEGER REFERENCES safety_reports(report_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);
