import requests
import os
import json
from datetime import datetime

def download_and_save_transcript(api_key, symbol, year, base_directory):
    # Define the URL for the batch earning call transcript
    url = f"https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{symbol}?year={year}&apikey={api_key}"

    # Send a request to the API
    response = requests.get(url)
    if response.status_code == 200:
        transcript_data = response.json()
        if transcript_data:
            # Create a subdirectory for the stock symbol if it doesn't exist
            symbol_directory = os.path.join(base_directory, symbol)
            os.makedirs(symbol_directory, exist_ok=True)

            # Save each transcript to a separate file in the symbol's subdirectory
            for item in transcript_data:
                quarter = item['quarter']
                date = datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S")
                date_formatted = date.strftime("%Y-%m-%d")
                file_path = os.path.join(symbol_directory, f"{symbol}_transcript_CY{year}_Q{quarter}_{date_formatted}.json")
                with open(file_path, 'w') as f:
                    json.dump(item, f)
                print(f"Saved transcript for {symbol} for {year} Q{quarter}")
            return True
    return False

# List of stock symbols
tmt_stocks = [
    "AAPL", "CPAY", "HUBS", "NETE", "SQ", "ACN", "CRM", "IBM", "NOK", "STM",
    "ADBE", "CRWD", "IIVI", "NOW", "TEAM", "ADI", "CSCO", "INFY", "NTAP", "TEL",
    "ADSK", "CTSH", "INTC", "NTES", "AMAT", "DDOG", "INTU", "NVDA", "TSM",
    "AMD", "DELL", "IOT", "NXPI", "TTD", "ANET", "EA", "IT", "ON", "TTWO",
    "ANSS", "ENTG", "KEYS", "ORCL", "TXN", "APH", "FI", "KLAC", "PANW", "TYL",
    "APP", "FICO", "KSPI", "PLTR", "UBER", "ARM", "FIS", "LRCX", "PTC", "UMC",
    "ASML", "FLT", "MCHP", "QCOM", "VMW", "ASX", "FTNT", "MDB", "RBLX", "WDAY",
    "ATVI", "FTV", "MPWR", "SAP", "WDC", "AVGO", "GFS", "MRVL", "SHOP", "WIT",
    "BR", "GIB", "MSFT", "SMCI", "ZS", "CAJ", "GLW", "MSI", "SNOW", "CDNS",
    "GRMN", "MSTR", "SNPS", "CDW", "HPE", "MU", "SONY", "COIN", "HPQ", "NET", "SPLK"
]

# Example usage
api_key = "c4ad87b03bec1878bc0be6156d4472b0"  # Replace with your actual API key
# List of years to download transcripts for
years = [2020, 2021, 2022, 2023, 2024]  # Add more years as needed

# Base directory to save transcripts
base_directory = "transcripts"

# API key for Financial Modeling Prep
api_key = "c4ad87b03bec1878bc0be6156d4472b0"  # Replace with your actual API key

# Loop through each stock symbol and year
for symbol in tmt_stocks:
    for year in years:
        download_and_save_transcript(api_key, symbol, year, base_directory)