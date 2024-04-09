from flask import Flask
from urllib.request import urlopen
import certifi
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()
FINANCIAL_MODEL_PREP_API = os.getenv('FINANCIAL_MODEL_PREP_API')

app = Flask(__name__)

uri = "mongodb+srv://erhardbr:9mD9EXsdpviBbmKn@serverlessinstance0.6v1u89n.mongodb.net/?retryWrites=true&w=majority&appName=ServerlessInstance0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['tech_transcripts']
collection = db['tech']

# List of stock tickers
stock_tickers = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'FB']  # Replace with your list of stock tickers

def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

@app.route('/fetch_transcripts')
def fetch_transcripts():
    for ticker in stock_tickers:
        try:
            # Make API request to fetch earnings call transcript
            url = f'https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{ticker}?year=2020&apikey={FINANCIAL_MODEL_PREP_API}'
            data = get_jsonparsed_data(url)

            # Extract relevant fields from the API response
            if isinstance(data, list):
                for transcript in data:
                    symbol = transcript.get('symbol')
                    quarter = transcript.get('quarter')
                    year = transcript.get('year')
                    date = transcript.get('date')
                    content = transcript.get('content')

                    # Create a document for the transcript
                    document = {
                        '_id': ObjectId(),  # Generate a unique _id for each document
                        'symbol': symbol,
                        'quarter': quarter,
                        'year': year,
                        'date': date,
                        'content': content
                    }

                    # Insert the document into the MongoDB collection
                    insert_result = collection.insert_one(document)
                    if insert_result.acknowledged:
                        print(f'Transcripts for {ticker} stored successfully in MongoDB.')
                    else:
                        print(f'Failed to store transcripts for {ticker} in MongoDB.')
            else:
                print(f'Unexpected response format for {ticker}.')
        except Exception as e:
            print(f'Error fetching or storing transcripts for {ticker}: {str(e)}')

    return 'Transcripts stored successfully.'

if __name__ == '__main__':
    app.run()