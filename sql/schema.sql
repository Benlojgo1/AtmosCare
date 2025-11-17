<<<<<<< HEAD
-- Disable referential integrity checks temporarily during setup
SET session_replication_role = replica;

-- LOCATION Table (Parent table, holds static info about monitored communities)
CREATE TABLE IF NOT EXISTS LOCATION (
    zip_code VARCHAR(10) PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    population INTEGER,
    vulnerability_index DECIMAL(3, 2) -- e.g., 0.00 to 1.00 score based on socio-economic factors
);

-- HEALTH_RISK Table (Lookup table for types of health conditions/risks)
CREATE TABLE IF NOT EXISTS HEALTH_RISK (
    risk_id SERIAL PRIMARY KEY,
    risk_name VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'Asthma', 'Extreme Heat Risk'
    threshold_type VARCHAR(50),             -- e.g., 'AQI', 'Temperature'
    threshold_value DECIMAL(5, 2)           -- e.g., AQI > 150, Temp > 35.0 C
);

-- WEATHER_RECORD Table (Stores the high-volume, time-series data from the API)
CREATE TABLE IF NOT EXISTS WEATHER_RECORD (
    record_id SERIAL PRIMARY KEY,
    zip_code VARCHAR(10) REFERENCES LOCATION(zip_code) ON DELETE CASCADE, -- FK to LOCATION
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature DECIMAL(4, 1),
    humidity DECIMAL(4, 1),
    air_quality_index INTEGER
);

-- RISK_ALERT Table (Fact table, links a specific weather event to a potential health risk)
CREATE TABLE IF NOT EXISTS RISK_ALERT (
    alert_id SERIAL PRIMARY KEY,
    zip_code VARCHAR(10) NOT NULL REFERENCES LOCATION(zip_code) ON DELETE CASCADE,
    record_id INTEGER REFERENCES WEATHER_RECORD(record_id) ON DELETE CASCADE,
    risk_id INTEGER REFERENCES HEALTH_RISK(risk_id) ON DELETE RESTRICT,
    is_urgent BOOLEAN DEFAULT FALSE,

    -- Ensures we don't duplicate the exact same alert for the same record and risk
    UNIQUE (record_id, risk_id) 
);

-- Re-enable referential integrity checks
SET session_replication_role = DEFAULT;
=======
--CREATE TABLE statements (LOCATION, WEATHER_RECORD...)
>>>>>>> f43217294404db2beb60366dd78400e793075df8
