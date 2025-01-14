# 🐍 Final project for data analysis and visualization using python

## steps to use locally

### step 1. create virtual environment

`python -m venv venv`

### step 2. install requirements

`pip install -r requirements.txt`

### create a .env file with the following variables:

```
DB_PASSWORD=
DB_HOST=
DB_USER=
DB_NAME=
ENVIRONMENT=
```

DB values from neon.tech

environment being either "production" or "development"

# IN NEON.TECH SQL EDITOR RUN THE FOLLOWING:

```sql
CREATE TABLE weather_forecasts (
    id SERIAL PRIMARY KEY,
    period VARCHAR(50),
    short_desc VARCHAR(255),
    temperature VARCHAR(50),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

and this:

```sql
CREATE TABLE processed_weather_forecasts (
    id SERIAL PRIMARY KEY,
    forecast_period VARCHAR(50),
    temperature FLOAT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
