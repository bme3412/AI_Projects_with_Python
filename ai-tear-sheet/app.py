import locale
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from functools import lru_cache
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from openai import OpenAI
import time
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

# Set the locale to use commas as thousand separators
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def format_number(value):
    try:
        return "{:,.0f}".format(value)
    except (ValueError, TypeError):
        return value

def format_float(value, precision=2):
    """Format the float to a specified number of decimal places."""
    try:
        return f"{value:.{precision}f}"
    except (ValueError, TypeError):
        return value

def format_percentage(value):
    try:
        return f"{value:.2f}%"
    except (ValueError, TypeError):
        return 'N/A'

app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['format_float'] = format_float
app.jinja_env.filters['format_percentage'] = format_percentage

app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['format_float'] = format_float

API_BASE_URL_V3 = "https://financialmodelingprep.com/api/v3/"
API_BASE_URL_V4 = "https://financialmodelingprep.com/api/v4/"
API_KEY = os.getenv('FINANCIAL_MODEL_PREP_API_KEY') 

@lru_cache(maxsize=32)
def get_company_data(symbol):
    """Fetch company data from API with caching."""
    url = f"{API_BASE_URL_V3}profile/{symbol}?apikey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        profile_data = response.json()[0]

        # Fetch the "ask" value from the pre-post market API
        pre_post_market_url = f"{API_BASE_URL_V4}pre-post-market/{symbol}?apikey={API_KEY}"
        pre_post_market_response = requests.get(pre_post_market_url)
        pre_post_market_data = pre_post_market_response.json()

        if 'ask' in pre_post_market_data:
            profile_data['ask'] = pre_post_market_data['ask']
        else:
            profile_data['ask'] = 'N/A'

        # Fetch historical price data for the previous day's closing price
        historical_url = f"{API_BASE_URL_V3}historical-price-full/{symbol}?serietype=line&apikey={API_KEY}"
        historical_response = requests.get(historical_url)
        historical_data = historical_response.json().get('historical', [])

        if historical_data and len(historical_data) > 1:
            current_price = profile_data.get('price', None)
            previous_close = historical_data[1].get('close', None)

            if current_price and previous_close:
                changes_percentage = ((current_price - previous_close) / previous_close) * 100
                profile_data['changesPercentage'] = changes_percentage
            else:
                profile_data['changesPercentage'] = 'N/A'
        else:
            profile_data['changesPercentage'] = 'N/A'

        return profile_data
    except requests.RequestException as e:
        print(f"Failed to retrieve data for {symbol}: {e}")
        return {}



def get_annual_returns(symbol):
    """Fetch historical stock prices and calculate annual returns."""
    url = f"{API_BASE_URL_V3}historical-price-full/{symbol}?apikey={API_KEY}"
    response = requests.get(url)
    data = response.json().get('historical', [])

    # Calculate annual returns
    annual_returns = []
    prices_by_year = {}
    for entry in data:
        year = entry['date'][:4]
        if year not in prices_by_year:
            prices_by_year[year] = []
        prices_by_year[year].append((entry['date'], entry['close']))

    years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
    for year in years:
        if year in prices_by_year:
            year_prices = prices_by_year[year]
            start_date, start_price = min(year_prices)
            end_date, end_price = max(year_prices)
            # Check if start and end dates are in the same year
            if start_date[:4] == end_date[:4]:
                annual_return = ((end_price / start_price) - 1) * 100
                annual_returns.append((year, f"{annual_return:.2f}"))
            else:
                # Return "N/A" if the start and end dates are not in the same year
                annual_returns.append((year, "N/A"))
        else:
            # Return "N/A" if data is not available for a year
            annual_returns.append((year, "N/A"))

    # Calculate YTD return for 2024
    if '2023' in prices_by_year and '2024' in prices_by_year:
        # Get the price on December 31, 2023
        price_2023_12_31 = prices_by_year['2023'][-1][1]
        # Get the most recent price in 2024
        price_2024_latest = prices_by_year['2024'][-1][1]
        ytd_return = ((price_2024_latest / price_2023_12_31) - 1) * 100
        annual_returns.append(('2024 YTD', f"{ytd_return:.2f}"))
    else:
        annual_returns.append(('2024 YTD', "N/A"))

    return annual_returns


def get_price_target(symbol):
    url = f"{API_BASE_URL_V4}price-target-consensus?symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error for HTTP codes 400 or 500
        data = response.json()
        if data:
            return data[0]
        else:
            print(f"No data returned for {symbol}")
            return {}
    except requests.RequestException as e:
        print(f"Request failed for {symbol}: {e}")
        return {}


def get_consensus_data(symbol):
    """Fetch consensus data from API."""
    url = f"{API_BASE_URL_V4}upgrades-downgrades-consensus?symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]  # Return the first element of the list if it exists
        else:
            return {}  # Return an empty dictionary if the response data is empty
    except requests.RequestException as e:
        print(f"Failed to retrieve consensus data for {symbol}: {e}")
        return {}  # Return an empty dictionary or some default value


@app.route('/price-data/<symbol>')
def get_price_data(symbol):
    now = datetime.now().date()
    periods = {
        '1d': (now - timedelta(days=1), now, '1min'),
        '5d': (now - timedelta(days=5), now, '5min'),
        '1mo': (now - timedelta(days=30), now, '1hour'),
        '3mo': (now - timedelta(days=90), now, '1day'),
        '6mo': (now - timedelta(days=180), now, '1day'),
        '1y': (now - timedelta(days=365), now, '1day'),
        '3y': (now - timedelta(days=365*3), now, '1week'),
        '5y': (now - timedelta(days=365*5), now, '1month'),
        '10y': (now - timedelta(days=365*10), now, '1month'),
        # Adjust the number of years as needed
        'max': (now - timedelta(days=365*50), now, '1month')
    }

    def fetch_data(period, from_date, to_date, interval):
        url = f'https://financialmodelingprep.com/api/v3/historical-chart/{interval}/{symbol}?from={from_date}&to={to_date}&apikey={API_KEY}'
        response = requests.get(url)
        data = response.json()

        if data:
            timestamps = [entry['date'] for entry in data]
            prices = [entry['close'] for entry in data]

            # Filter out non-business days
            df = pd.DataFrame({'timestamp': timestamps, 'price': prices})
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            df = df[df.index.dayofweek < 5]  # Keep only business days

            timestamps = df.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
            prices = df['price'].tolist()

            return period, {'timestamps': timestamps, 'prices': prices}
        else:
            return period, {'timestamps': [], 'prices': []}

    price_data = {}
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_data, period, from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'), interval)
                   for period, (from_date, to_date, interval) in periods.items()]
        for future in as_completed(futures):
            period, data = future.result()
            price_data[period] = data

    return jsonify(price_data)


def filter_business_days(data):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'].dt.dayofweek < 5]  # Keep only Monday to Friday
    return df.to_dict(orient='list')


@app.route('/', methods=['GET'])
def home():
    symbol = request.args.get('symbol', 'AAPL')
    company_data = get_company_data(symbol)
    annual_returns = get_annual_returns(symbol)
    price_target_data = get_price_target(symbol)
    consensus_data = get_consensus_data(symbol)

    return render_template('index.html', company=company_data, returns=annual_returns,
                           price_target=price_target_data, consensus=consensus_data,
                           error=company_data.get('error'))


def number_format(value):
    """Format a number with grouped thousands using commas."""
    try:
        return locale.format_string("%d", value, grouping=True)
    except:
        return value  # If value is not a number, return it unmodified


# Register the filter with Jinja2
app.jinja_env.filters['number_format'] = number_format


def get_fiscal_year_end(symbol):
    """Fetch the fiscal year end date for a given symbol."""
    url = f"{API_BASE_URL_V4}company-core-information?symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and 'fiscalYearEnd' in data[0]:
            return data[0]['fiscalYearEnd']
    return None


@app.route('/income-statement')
def income_statement():
    ticker = request.args.get('ticker', 'AAPL')
    period = request.args.get('period', 'annual')
    limit = 12 if period == 'quarter' else 5
    fiscal_year_end = get_fiscal_year_end(ticker)
    if not fiscal_year_end:
        return "Error fetching fiscal year end date."
    url = f"{API_BASE_URL_V3}income-statement/{ticker}?period={period}&apikey={API_KEY}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            keys_of_interest = [
                'date', 'revenue', 'costOfRevenue', 'grossProfit', 'grossProfitRatio',
                'researchAndDevelopmentExpenses', 'sellingGeneralAndAdministrativeExpenses', 'otherExpenses',
                'operatingExpenses', 'operatingIncome', 'operatingIncomeRatio', 'interestIncome',
                'interestExpense', 'incomeBeforeTax', 'incomeTaxExpense', 'netIncome',
                'eps', 'epsdiluted', 'weightedAverageShsOut', 'weightedAverageShsOutDil'
            ]
            income_statements = [{key: item[key]
                                  for key in keys_of_interest} for item in data]
            for statement in income_statements:
                statement['formatted_date'] = datetime.strptime(
                    statement['date'], '%Y-%m-%d').strftime('%b %Y')
            if period == 'quarter':
                income_statements.sort(key=lambda x: x['date'], reverse=True)
                income_statements = income_statements[::-1]
            else:
                income_statements.sort(key=lambda x: x['date'])
            return render_template('income_statement.html', income_statements=income_statements, ticker=ticker, period=period)
        else:
            return "No income statement data available."
    else:
        return f"Error retrieving data: {response.status_code}"


@app.route('/balance-sheet')
def balance_sheet():
    ticker = request.args.get('ticker', 'AAPL')
    period = request.args.get('period', 'annual')
    limit = 12 if period == 'quarter' else 5
    fiscal_year_end = get_fiscal_year_end(ticker)
    if not fiscal_year_end:
        return "Error fetching fiscal year end date."
    url = f"{API_BASE_URL_V3}balance-sheet-statement/{ticker}?period={period}&apikey={API_KEY}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            keys_of_interest = [
                'date', 'cashAndCashEquivalents', 'shortTermInvestments', 'cashAndShortTermInvestments',
                'netReceivables', 'inventory', 'otherCurrentAssets', 'totalCurrentAssets',
                'propertyPlantEquipmentNet', 'goodwill', 'intangibleAssets', 'goodwillAndIntangibleAssets',
                'longTermInvestments', 'taxAssets', 'otherNonCurrentAssets', 'totalNonCurrentAssets',
                'totalAssets', 'accountPayables', 'shortTermDebt', 'taxPayables', 'deferredRevenue',
                'otherCurrentLiabilities', 'totalCurrentLiabilities', 'longTermDebt',
                'deferredRevenueNonCurrent', 'deferredTaxLiabilitiesNonCurrent', 'otherNonCurrentLiabilities',
                'totalNonCurrentLiabilities', 'totalLiabilities', 'preferredStock', 'commonStock',
                'retainedEarnings', 'accumulatedOtherComprehensiveIncomeLoss', 'totalStockholdersEquity',
                'totalEquity', 'totalLiabilitiesAndStockholdersEquity', 'minorityInterest'
            ]
            balance_sheets = [{key: item[key]
                               for key in keys_of_interest} for item in data]
            for statement in balance_sheets:
                statement['formatted_date'] = datetime.strptime(
                    statement['date'], '%Y-%m-%d').strftime('%b %Y')
            if period == 'quarter':
                balance_sheets.sort(key=lambda x: x['date'], reverse=True)
                balance_sheets = balance_sheets[::-1]
            else:
                balance_sheets.sort(key=lambda x: x['date'])
            return render_template('balance_sheet.html', balance_sheets=balance_sheets, ticker=ticker, period=period)
        else:
            return "No balance sheet data available."
    else:
        return f"Error retrieving data: {response.status_code}"


@app.route('/cash-flow')
def cash_flow():
    ticker = request.args.get('ticker', 'AAPL')
    period = request.args.get('period', 'annual')
    # Adjust limit for quarters to get trailing 12 quarters
    limit = 12 if period == 'quarter' else 5
    fiscal_year_end = get_fiscal_year_end(ticker)
    if not fiscal_year_end:
        return "Error fetching fiscal year end date."
    url = f"{API_BASE_URL_V3}cash-flow-statement/{ticker}?period={period}&apikey={API_KEY}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            keys_of_interest = [
                'date', 'netIncome', 'depreciationAndAmortization', 'deferredIncomeTax', 'stockBasedCompensation',
                'changeInWorkingCapital', 'accountsReceivables', 'inventory', 'accountsPayables',
                'otherWorkingCapital', 'otherNonCashItems', 'netCashProvidedByOperatingActivities',
                'investmentsInPropertyPlantAndEquipment', 'acquisitionsNet', 'purchasesOfInvestments',
                'salesMaturitiesOfInvestments', 'otherInvestingActivites', 'netCashUsedForInvestingActivites',
                'debtRepayment', 'commonStockIssued', 'commonStockRepurchased', 'dividendsPaid',
                'otherFinancingActivites', 'netCashUsedProvidedByFinancingActivities', 'effectOfForexChangesOnCash',
                'netChangeInCash', 'cashAtEndOfPeriod', 'cashAtBeginningOfPeriod', 'operatingCashFlow',
                'capitalExpenditure', 'freeCashFlow'
            ]
            cash_flows = [{key: item[key]
                           for key in keys_of_interest} for item in data]
            # Format dates for better readability
            for statement in cash_flows:
                statement['formatted_date'] = datetime.strptime(
                    statement['date'], '%Y-%m-%d').strftime('%b %Y')
            if period == 'quarter':
                # Sort by date in descending order
                cash_flows.sort(key=lambda x: x['date'], reverse=True)
                # Reverse the order of the cash flows
                cash_flows = cash_flows[::-1]
            else:
                # Sort by date in ascending order
                cash_flows.sort(key=lambda x: x['date'])
            return render_template('cash_flow.html', cash_flows=cash_flows, ticker=ticker, period=period)
        else:
            return "No cash flow data available."
    else:
        return f"Error retrieving data: {response.status_code}"


# Variables for transcripts
API_BASE_URL = 'https://financialmodelingprep.com/api/v3/earning_call_transcript/'
YEARS = [2020, 2021, 2022, 2023, 2024]
QUARTERS = [1, 2, 3, 4]


def fetch_transcripts(symbol):
    transcripts = []
    for year in YEARS:
        for quarter in QUARTERS:
            url = f"{API_BASE_URL}{symbol}?year={year}&quarter={quarter}&apikey={API_KEY}"
            response = requests.get(url).json()
            transcripts.extend(response)

    transcripts.sort(key=lambda x: x['date'], reverse=True)
    return transcripts[:12]

def create_prompt(transcripts):
    prompt = (
        "You are a financial analyst. Use only info provided in the transcripts. "
        "Accuracy is important. If there is no information for a topic, it is ok to skip and not provide any info. "
        "Do not invent any answers. Do instructions below in a stepwise fashion.\n"
        "1) Review the data of the earnings transcripts for each company. Identify the most recent 12 quarters, starting with the one closest to today's date.\n"
        "2) Within the CEO and CFO sections, for each of those quarters identify and record, identify management outlook for the company and management specific guidance for each of the following: sales, GM %, operating expenses, operating margin, share count, EPS, and FCF.\n"
        "3) Analyze how management outlook and guidance have changed chronologically quarter over quarter over the last 12 quarters. Develop a score ranging from -5 to +5 as a measure of how much more positive or negative the outlook and guidance have changed quarter to quarter. In the scoring, -5 = very negative, 0 = no change, +5 = very positive.\n"
        "4) Create a table with visible borders. The column headings are: Quarter, Management Outlook, What Changed & Management Explanation, Score, Rationale for Score.\n"
        "5) Fill in the table with relevant info.\n\n"
    )

    for transcript in transcripts:
        prompt += f"Date: {transcript['date']}\n"
        prompt += f"Quarter: Q{transcript['quarter']} {transcript['year']}\n"
        prompt += f"Content:\n{transcript['content']}\n\n"

    return prompt

@app.route('/transcripts/<symbol>', methods=['GET', 'POST'])
def transcripts(symbol):
    if request.method == 'POST':
        transcripts = fetch_transcripts(symbol)
        prompt = create_prompt(transcripts)
        return render_template('transcript.html', prompt=prompt, symbol=symbol)
    return render_template('transcript.html', symbol=symbol)

@app.route('/generate_prompt', methods=['POST'])
def generate_prompt():
    symbol = request.form['symbol']
    return redirect(url_for('transcripts', symbol=symbol))

@app.route('/llm', methods=['POST'])
def llm():
    data = request.json
    transcript_content = data.get('transcript_content')
    prompt = data.get('prompt')

    if not transcript_content or not prompt:
        return jsonify({"error": "No transcript content or prompt provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": transcript_content
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            n=1,
            stop=None
        )

        # Accessing the response correctly using dot notation
        generated_text = response.choices[0].message.content.strip()
        return jsonify({"generated_text": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
