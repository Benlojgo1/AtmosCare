<<<<<<< HEAD
-- Insert Sample Locations (Static Data)
INSERT INTO LOCATION (zip_code, location_name, population, vulnerability_index) VALUES
('90210', 'Beverly Hills', 34000, 0.15),
('78520', 'Brownsville North', 55000, 0.78),
('10005', 'Financial District', 8000, 0.35),
('60620', 'Chicago South', 62000, 0.91);

-- Insert Sample Health Risks (Lookup Data for Analysis)
INSERT INTO HEALTH_RISK (risk_name, threshold_type, threshold_value) VALUES
('Asthma Attack Risk', 'AQI', 100.0),
('Heat Stroke Warning', 'Temperature', 35.0),
('Extreme Humidity Discomfort', 'Humidity', 75.0);

-- Insert Sample Weather Records (Dynamic data, but useful for initial testing)
-- You would replace this with actual data ingestion later!
INSERT INTO WEATHER_RECORD (zip_code, timestamp, temperature, humidity, air_quality_index) VALUES
('90210', NOW() - INTERVAL '1 day', 22.5, 55.0, 45),
('78520', NOW() - INTERVAL '1 day', 36.0, 78.0, 95), -- High risk event
('60620', NOW() - INTERVAL '1 day', 28.1, 65.0, 110), -- High AQI risk event
('78520', NOW(), 34.0, 70.0, 50);

-- Insert Sample Alerts (Based on the data above)
-- Alert 1: Heat Stroke Warning in 78520
INSERT INTO RISK_ALERT (zip_code, record_id, risk_id, is_urgent) VALUES
('78520', 2, 2, TRUE); -- Assuming record_id 2 corresponds to the 36.0 temp

-- Alert 2: Asthma Risk in 60620
INSERT INTO RISK_ALERT (zip_code, record_id, risk_id, is_urgent) VALUES
('60620', 3, 1, TRUE); -- Assuming record_id 3 corresponds to the 110 AQI
=======
--Optional sample data
>>>>>>> f43217294404db2beb60366dd78400e793075df8
