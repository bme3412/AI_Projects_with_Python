from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from flask_caching import Cache
from openai import OpenAI

client = OpenAI(api_key='#')


app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# Function to get summary from OpenAI
def get_summary(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Your task is to succinctly summarize the text for an astute financial analyst."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=64,
            top_p=1
        )
        # The alchemy to extract the essence of our quest:
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Summary not available"



def parse_transcript(json_data):
    transcript = json_data[0]['content']
    parts = transcript.split("\n")
    transcript_data = []
    current_speaker = None

    for part in parts:
        if ":" in part:
            speaker, speech = part.split(":", 1)
            current_speaker = speaker.strip()
            summary = get_summary(speech.strip())  # Get summary for each speech
            transcript_data.append({'Speaker': current_speaker, 'Speech': speech.strip(), 'Summary': summary})
        elif current_speaker:
            # Append to the last speech if the current line is a continuation
            transcript_data[-1]['Speech'] += " " + part.strip()
            # Update the summary for the continued speech
            transcript_data[-1]['Summary'] = get_summary(transcript_data[-1]['Speech'])

    return pd.DataFrame(transcript_data)

public_years = {
    'AAPL': 1980,
    'MSFT': 1986,
    'AMZN': 1997,
    'BABA':2014,
    'META': 2012,
    'GOOGL': 2004
}


def get_available_years_for_tickers(ticker):
    base_url = "https://financialmodelingprep.com/api/v4/batch_earning_call_transcript"
    api_key = ''
    start_year = public_years.get(ticker, 2000)
    current_year = pd.Timestamp.now().year
    years_range = range(start_year, current_year + 1)
    years_with_data = []

    for year in years_range:
        url = f"{base_url}/{ticker}?year={year}&apikey={api_key}"
        response = requests.get(url)
        if response and response.json():
            years_with_data.append(year)

    print(f"Years with data for {ticker}: {years_with_data}")  # Debug statement
    return sorted(years_with_data)



@app.route('/', methods=['GET', 'POST'])
def index():
    available_years = []
    selected_ticker = None

    if request.method == 'POST':
        ticker = request.form['ticker']
        year = request.form['year']
        quarter = request.form['quarter']
        selected_ticker = ticker

        # Fetch available years for the selected ticker
        available_years = get_available_years_for_tickers(ticker)

        api_key = '#'
        url = f'https://financialmodelingprep.com/api/v3/earning_call_transcript/{ticker}?year={year}&quarter={quarter}&apikey={api_key}'
        
        response = requests.get(url)
        data = response.json()

        transcript_df = parse_transcript(data)
        transcript_html = transcript_df.to_html(index=False)
        return render_template('index.html', table=transcript_html, years=available_years, selected_ticker=selected_ticker)

    return render_template('index.html', table=None, years=available_years, selected_ticker=selected_ticker)

@app.route('/years/<ticker>')
def get_years(ticker):
    available_years = get_available_years_for_tickers(ticker)
    return jsonify({'years': available_years})




if __name__ == '__main__':
    app.run(debug=True)
