from flask import Flask, render_template, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Format date function
def format_date(value, format_string='%Y-%m-%d %H:%M'):
    try:
        timestamp = int(value) / 1000
        return datetime.utcfromtimestamp(timestamp).strftime(format_string)
    except (ValueError, TypeError):
        return "Invalid Date"

app.jinja_env.filters['format_date'] = format_date

@app.route('/', methods=['GET', 'POST'])
def home():
    events_data = []
    city_name = ""

   
    # Direct path to the merged schedule data
    merged_schedule_file_path = '/Users/brendan/Desktop - Brendan’s MacBook Air/sportsInfo/sportsInfo/data/schedules/merged_data.json'  

    try:
        with open(merged_schedule_file_path, 'r') as file:
            combined_schedule_data = json.load(file)

        # Sort the combined schedule data by date
        sorted_events_data = sorted(combined_schedule_data, key=lambda x: x['Date'])

        if request.method == 'POST':
            city_name = request.form.get('city_name', '').strip().lower()

        for event in sorted_events_data:
            if not city_name or city_name == event.get('Location', '').split(',')[0].strip().lower():
                events_data.append(event)

        city_name = city_name.capitalize() if city_name else "All Cities"

    except Exception as e:
        print(f"Error reading the merged schedule file: {e}")
        return render_template('schedule.html', error="Could not load the schedule data", city_name=city_name)

    return render_template('schedule.html', events_data=events_data, city_name=city_name)


if __name__ == '__main__':
    app.run(debug=True)
