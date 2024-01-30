from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)  
# Global API key
api_key = '#'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search-tickers', methods=['GET'])
def search_tickers():
    query = request.args.get('query')
    api_url = f"https://financialmodelingprep.com/api/v3/search?query={query}&limit=10&apikey={api_key}"
    
    response = requests.get(api_url)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "API request failed"}), response.status_code

@app.route('/get-10k-filings', methods=['GET'])
def get_10k_filings():
    ticker = request.args.get('ticker')
    response = requests.get(f"https://financialmodelingprep.com/api/v3/sec_filings/{ticker}?type=10-k&page=0&apikey={api_key}")
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "API request failed"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
