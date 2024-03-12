#!/usr/bin/env python

from urllib.request import urlopen
import certifi
import json
from dotenv import load_dotenv
import os
import re  # Import the regex module

# Load environment variables from .env file
load_dotenv()
api_key = os.environ.get("FINANCIAL_MODELING_PREP_API")


def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

def ensure_directories_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_transcript_content(content):
    # Split the content by speaker using a regex pattern
    pattern = re.compile(r'\n([A-Za-z ]+): ')
    parts = pattern.split(content)
    
    # Reorganize parts into a list of dicts with speaker and text
    speakers = parts[1::2]  # Every second element starting from 1
    speeches = parts[2::2]  # Every second element starting from 2
    transcript_data = [{'speaker': speaker, 'text': text} for speaker, text in zip(speakers, speeches)]
    
    return transcript_data

def download_transcript(ticker, year, quarters=[1, 2, 3, 4], api_key=api_key):
    for quarter in quarters:
        directory_path = f"transcripts/{ticker}/{year}"
        ensure_directories_exist(directory_path)
        
        filename = f"{directory_path}/{ticker}_Q{quarter}_{year}.json"
        
        if os.path.exists(filename):
            print(f"Transcript for {ticker} for Q{quarter}, {year} already downloaded.")
            continue

        url = f"https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{ticker}?year={year}&quarter={quarter}&apikey={api_key}"
        
        try:
            data = get_jsonparsed_data(url)
            if data:
                # Process the content to differentiate by speaker
                for item in data:
                    item['content'] = process_transcript_content(item['content'])
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Transcript for {ticker} for Q{quarter}, {year} has been saved to {filename}.")
            else:
                print(f"No data found for {ticker} for Q{quarter}, {year}.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    ticker_input = input("Enter ticker symbol: ")
    year_input = input("Enter year: ")
    download_transcript(ticker_input, year_input)
