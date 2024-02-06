from flask import Flask, render_template, request, jsonify
import requests
from openai import OpenAI
client = OpenAI()
import pandas as pd

app = Flask(__name__)



## converts speech to dataframe
def parse_transcript(json_data):
    transcript = json_data[0]['content']
    parts = transcript.split("\n")
    transcript_data = []
    current_speaker = None

    for part in parts:
        if ":" in part:
            speaker, speech = part.split(":", 1)
            speaker = speaker.strip()

            # Skip entries where the speaker is 'Operator'
            if speaker == 'Operator':
                continue

            speech = speech.strip()

            if speaker != current_speaker:
                if current_speaker is not None:
                    transcript_data.append({'Speaker': '---', 'Speech': 'Speaker Change'})

                current_speaker = speaker
                transcript_data.append({'Speaker': current_speaker, 'Speech': speech})
            else:
                # Append to the last speech if the current line is a continuation
                transcript_data[-1]['Speech'] += " " + speech
                
    transcript_df = pd.DataFrame(transcript_data)
    return transcript_df


# gets years transcript is available for each ticker
def get_available_years_for_tickers(ticker):
    base_url = "https://financialmodelingprep.com/api/v4/batch_earning_call_transcript"
    api_key = ''
    start_year = 2000
    current_year = pd.Timestamp.now().year
    years_range = range(start_year, current_year + 1)
    years_with_data = []

    for year in years_range:
        url = f"{base_url}/{ticker}?year={year}&apikey={api_key}"
        response = requests.get(url)
        if response and response.json():
            years_with_data.append(year)

    #print(f"Years with data for {ticker}: {years_with_data}")  # Debug statement
    return sorted(years_with_data)

## generates summaries
def generate_speaker_summaries(transcript_df):
    summaries = {}
    for speaker, group in transcript_df.groupby('Speaker'):
        if speaker != 'Operator':  # Exclude 'Operator' from summaries
            combined_speech = ' '.join(group['Speech'])
            summary = generate_summary_with_openai(combined_speech)
            summaries[speaker] = summary
    return summaries

def generate_summary_with_openai(text):
    try:
        # Adding instructions to format the summary with bullet points
        prompt = f"Summarize this text using bullet points:\n{text}"
        response = client.chat.completions.create(
            model="gpt-4",  # Confirm this is the correct model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.5
        )
        if response.choices and len(response.choices) > 0:
            # Format the summary to include bullet points if not already formatted
            summary_lines = response.choices[0].message.content.strip().split('\n')
            bullet_point_summary = '\n'.join([f"* {line}" for line in summary_lines if line.strip() != ''])
            return bullet_point_summary if bullet_point_summary else None
    except Exception as e:
        print(f"Error in generating summary: {e}")
    return None



def add_summaries_to_df(transcript_df):
    # Ensure 'Speech' is a string to avoid errors in summary generation
    transcript_df['Speech'] = transcript_df['Speech'].astype(str)
    
    # Generate summaries and add to a new 'Summary' column
    transcript_df['Summary'] = transcript_df['Speech'].apply(generate_summary_with_openai)
    return transcript_df





# route that shows years, ticker, summaries
@app.route('/', methods=['GET', 'POST'])
def index():
    available_years = []
    selected_ticker = None
    summaries = {}  # Initialize summaries to an empty dictionary

    if request.method == 'POST':
        ticker = request.form['ticker']
        year = request.form['year']
        quarter = request.form['quarter']
        selected_ticker = ticker

        # Fetch available years for the selected ticker
        available_years = get_available_years_for_tickers(ticker)

        api_key = ''
        url = f'https://financialmodelingprep.com/api/v3/earning_call_transcript/{ticker}?year={year}&quarter={quarter}&apikey={api_key}'
        
        response = requests.get(url)
        data = response.json()

        transcript_df = parse_transcript(data)
        # Update the DataFrame to include summaries for each speech
        transcript_df = add_summaries_to_df(transcript_df)  # This line replaces generate_speaker_summaries

        # Convert the updated DataFrame to HTML, including the new 'Summary' column
        transcript_html = transcript_df.to_html(index=False, escape=False)
        return render_template('index.html', table=transcript_html, summaries=summaries, years=available_years, selected_ticker=selected_ticker)

    # For GET request, pass the initialized empty 'summaries'
    return render_template('index.html', table=None, summaries=summaries, years=available_years, selected_ticker=selected_ticker)


@app.route('/years/<ticker>')
def get_years(ticker):
    available_years = get_available_years_for_tickers(ticker)
    return jsonify({'years': available_years})


if __name__ == '__main__':
    app.run(debug=True)
