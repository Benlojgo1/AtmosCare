# ☁️ AtmosCare: Infrastructure Resiliency Tracker

## Project Overview

**AtmosCare** is a database-driven application designed to monitor and visualize environmental data to provide actionable insights into **public health and well-being risks**. By integrating real-time and historical weather, air quality, and climate vulnerability data, the system aims to break the barrier of informational access by helping users and organizations proactively manage health and safety during adverse weather conditions.

### 🎯 Theme: Data for Breaking Health & Informational Barriers

The project specifically addresses how environmental data can be used to mitigate risks for vulnerable populations (e.g., those with asthma during poor air quality, or the elderly during extreme heat) by providing data-driven alerts and resource visibility.

## 🛠️ Technical Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Database Model** | Relational (PostgreSQL or SQLite) | Ensures data integrity and supports complex analytical queries. |
| **Database Language** | SQL | Used for all CRUD and analytical operations. |
| **API / Data Source** | **WeatherAPI.com** | Primary source for real-time weather, temperature, humidity, and air quality data. JSON/XML API |
| **Back-End / Integration** | Python (with a database connector like `psycopg2` or `sqlite3`) | Handles data ingestion, cleaning, and running the analytical queries. |
| **Front-End / UI** | React | Simple interface for running queries and demonstrating CRUD operations. |

## 📂 Database Schema (Relational Model)

Our relational design utilizes four tables to organize location, environment, and health risk data.

| Table Name | Description | Key Attributes (PK $\rightarrow$ **Bold**, FK $\rightarrow$ *Italics*) |
| :--- | :--- | :--- |
| **LOCATION** | Stores all monitored community/institutional locations. | **`ZipCode`**, `LocationName`, `Population`, `VulnerabilityIndex` |
| **WEATHER\_RECORD** | Stores historical and current environmental data. | **`RecordID`**, *`ZipCode`*, `TimeStamp`, `Temperature`, `Humidity`, `AirQualityIndex (AQI)` |
| **HEALTH\_RISK** | Stores known health risks associated with environmental factors. | **`RiskID`**, `RiskName` (e.g., 'Asthma', 'Heat Stroke'), `ThresholdType` |
| **RISK\_ALERT** | Links weather records to potential health risks. | **`AlertID`**, *`ZipCode`*, *`RecordID`*, *`RiskID`*, `IsUrgent` |

## ⚙️ Back-End Analytical Queries (5 Required)

These parameterized queries are the core of our barrier-breaking analysis, accessible via the front-end.

1.  **High-Risk Population Exposure:** Find all ZIP Codes where the `AirQualityIndex (AQI)` is above a user-defined threshold AND the `VulnerabilityIndex` (a measure of high-risk population) is high.
2.  **Historical Outlier Check:** List the top 5 `ZipCode`s with the highest number of historical days where the temperature exceeded the 95th percentile, identifying heat risk.
3.  **Proactive Health Alert:** Given a user-input `RiskName` (e.g., 'Asthma'), display all current `ZipCode`s that meet the environmental thresholds defined in the `HEALTH_RISK` table.
4.  **Resource Allocation Metric:** Calculate and display the percentage of monitored locations currently under an `IsUrgent` alert, grouped by `VulnerabilityIndex` (e.g., comparing highly vulnerable vs. less vulnerable areas).
5.  **Comparative Analysis:** Compare the average `Humidity` and `Temperature` readings between two user-entered `ZipCode`s over the last 7 days.

## 🚀 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone (https://github.com/Benlojgo1/AtmosCare)
    cd AtmosCare
    ```
2.  **Set up the database:**
    * Install **PostgreSQL** or ensure **SQLite** is available.
    * Execute the SQL schema file (e.g., `schema.sql`) to create the tables.
3.  **Configure API Key:**
    * Obtain an API key from **WeatherAPI.com**.
    * Create a `.env` file and store your key: `WEATHERAPI_KEY="your_key_here"`
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

***

# 👥 Team Responsibilities

| Area | Responsibility | Suggested Team Member(s) |
| :--- | :--- | :--- |
| **Data Modeling & SQL** | Finalize the relational schema, write the `CREATE TABLE` scripts, and implement all 5 analytical SQL queries. | Everyone |
| **API & Data Ingestion** | Manage the **WeatherAPI.com** integration, write the Python scripts to fetch data, and ensure data is cleaned and loaded into the database (the **C**reate operation). | Alvaro |
| **CRUD Operations** | Implement the full Create, Read, Update, and Delete (**CRUD**) logic in the Python back-end for the **LOCATION** and **WEATHER\_RECORD** entities. | Ben |
| **Front-End (UI)** | Design and build the Streamlit/HTML interface, connecting the user input forms to the analytical queries and displaying results clearly. | Eric |
| **Documentation & Presentation** | Lead the creation of the final report, prepare the slides, and manage the weekly video updates. | Everyone |
