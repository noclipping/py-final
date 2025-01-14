from flask import Flask, send_file, jsonify
import matplotlib.pyplot as plt
import io
import pandas as pd
import weather_module as wm  # Import the modularized functions
import os
app = Flask(__name__)
plt.switch_backend('Agg')

@app.route('/scrape_and_store', methods=['GET'])
def scrape_and_store():
    try:
        # Scrape the data
        url = "https://forecast.weather.gov/MapClick.php?lat=37.7772&lon=-122.4168"
        page_content = wm.fetch_weather_page(url)
        weather_data = wm.parse_weather_data(page_content)

        # Insert raw data into weather_forecasts
        db_connection = wm.get_db_connection()
        wm.insert_weather_data(db_connection, weather_data)

        # Fetch raw data as DataFrame
        df = wm.fetch_data_to_dataframe(db_connection)

        # Clean and transform the data
        df_cleaned = wm.clean_and_transform(df)

        # Aggregate the data
        df_aggregated = wm.aggregate_data(df_cleaned)

        # Save processed data to the processed_weather_forecasts table
        wm.save_processed_data(db_connection, df_aggregated)

        db_connection.close()

        return jsonify({"message": "Data scraped, processed, and stored successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/temperature_trends', methods=['GET'])
def temperature_trends():
    try:
        # Fetch processed data from the processed_weather_forecasts table
        db_connection = wm.get_db_connection()
        query = "SELECT * FROM processed_weather_forecasts;"
        df = pd.read_sql_query(query, db_connection)
        db_connection.close()

        # Generate the plot
        fig, ax = plt.subplots()
        ax.plot(df['forecast_period'], df['temperature'], marker='o')
        ax.set(title='Temperature Trends', xlabel='Forecast Period', ylabel='Temperature')
        plt.xticks(rotation=45)
        plt.tight_layout()
        ax.grid(True)

        # Save plot to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)

        return send_file(buf, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    env = os.getenv('ENVIRONMENT', 'development')  # Default to 'development' if not set

    if env == 'development':
        app.run()  # dev
    elif env == 'production':
        app.run(host='0.0.0.0', port=10000, debug=True)  # prod
    else:
        raise ValueError(f"Invalid FLASK_ENV value: {env}. Must be 'development' or 'production'.")