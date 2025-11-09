export type Location = {
  ZipCode: string;
  LocationName: string;
  Population: number;
  VulnerabilityIndex: number;
};

export type WeatherRecord = {
  RecordID: number;
  ZipCode: string;
  TimeStamp: string;
  Temperature: number;
  Humidity: number;
  AirQualityIndex: number;
};
