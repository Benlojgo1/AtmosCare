from pydantic import BaseModel
from typing import List, Optional
import datetime

# ====================================================================
# A. LOCATION CRUD MODELS (Define structure for the LOCATION table)
# ====================================================================

class LocationBase(BaseModel):
    """Base model for shared location fields."""
    zip_code: str
    location_name: str
    population: int
    vulnerability_index: float

class LocationCreate(LocationBase):
    """Schema for data incoming when creating a new location (POST request)."""
    pass

class LocationRow(LocationBase):
    """Schema for data being returned from the database (GET response)."""
    class Config:
        # Allows Pydantic to map database column names (snake_case) to
        # model field names (snake_case or CamelCase if defined)
        from_attributes = True


# ====================================================================
# B. WEATHER_RECORD MODELS (Define structure for the WEATHER_RECORD table)
# ====================================================================

class WeatherRecordBase(BaseModel):
    """Schema for weather records."""
    timestamp: datetime.datetime
    temperature: float
    humidity: float
    air_quality_index: int

class WeatherRecordCreate(WeatherRecordBase):
    """Schema for data incoming when inserting new API data (needs FK)."""
    zip_code: str # Foreign Key needed for insertion

class WeatherRecordRow(WeatherRecordCreate):
    record_id: int
    
    class Config:
        from_attributes = True


# ====================================================================
# C. ANALYTICAL QUERY RESPONSE MODELS (Define the output structure for your 5 queries)
# ====================================================================

### 1. Query 1: High-Risk Population Exposure
class HighRiskRow(BaseModel):
    """
    Output for finding locations with high AQI AND high vulnerability.
    (Used by high_risk_query)
    """
    ZipCode: str
    LocationName: str
    VulnerabilityIndex: float
    AQI: float

    class Config:
        from_attributes = True


### 2. Query 5: Comparative Analysis (Compare Zips)
class CompareZipRow(BaseModel):
    """
    Output for comparing average temperature and humidity between two ZIP codes.
    (Used by compare_zips endpoint)
    """
    ZipCode: str
    AvgTemp: float
    AvgHumidity: float

    class Config:
        from_attributes = True


### 3. Query 4: Resource Allocation
class AllocationRow(BaseModel):
    """
    Output for calculating the percentage of urgent alerts by vulnerability bucket.
    (Used by resource_allocation endpoint)
    """
    VulnerabilityBucket: str
    PercentUrgent: float
    
    class Config:
        from_attributes = True

# You would add response models for the other analytical queries here as needed.