export type Location = {
  zip_code: string;
  location_name: string;
  population: number;
  vulnerability_index: number;
};

export type WeatherRecord = {
  record_id: number;
  zip_code: string;
  timestamp: string;         // ISO string from FastAPI
  temperature: number;
  humidity: number;
  air_quality_index: number;
};

