import json
import os
from flask import Flask, render_template, request, abort
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)
CORS(app)

# Custom Jinja filter for date formatting
def format_date(value, format_string='%Y/%m/%d %H:%M'):
    if isinstance(value, int):
        # Convert milliseconds to seconds
        timestamp = value / 1000
    else:
        timestamp = int(value) / 1000
    return datetime.utcfromtimestamp(timestamp).strftime(format_string)

app.jinja_env.filters['format_date'] = format_date


@app.route('/', methods=['GET', 'POST'])
def home():
    events_data = []
    city_name = ""

    # Default start_date to today's date, formatted as 'YYYY-MM-DD'
    start_date = datetime.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        city_name = request.form.get('city_name', '').strip().lower()
        # Update start_date based on form input, if provided
        form_start_date = request.form.get('start_date')
        if form_start_date:
            start_date = form_start_date

    # Convert start_date string back to a datetime object for comparison
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')

    # Update file path to the merged schedule data
    merged_schedule_file_path = os.path.join('data', 'schedules', 'merged_data.json')

    try:
        with open(merged_schedule_file_path, 'r') as file:
            combined_schedule_data = json.load(file)

        for event in combined_schedule_data:
            # Correctly handle timestamp conversion based on its format (int or str)
            if isinstance(event['Date'], int):
                # Convert milliseconds to seconds if necessary
                event_date_obj = datetime.utcfromtimestamp(event['Date'] / 1000)
            else:
                event_date_obj = datetime.strptime(event['Date'], '%Y-%m-%d')

            if event_date_obj >= start_date_obj:
                if not city_name or (event.get('Location') and city_name.lower() in event.get('Location', '').lower()):
                    events_data.append(event)

        # Sort events_data by date, from earliest to latest
        events_data.sort(key=lambda event: datetime.utcfromtimestamp(event['Date'] / 1000) if isinstance(event['Date'], int) else datetime.strptime(event['Date'], '%Y/%m/%d'))

        city_name = city_name.capitalize() if city_name else "All Cities"

    except Exception as e:
        print(f"Error reading the merged schedule file: {e}")
        return render_template('schedule.html', error="Could not load the schedule data", city_name=city_name, start_date=start_date)

    return render_template('schedule.html', events_data=events_data, city_name=city_name, start_date=start_date)



if __name__ == '__main__':
    app.run(debug=True)
