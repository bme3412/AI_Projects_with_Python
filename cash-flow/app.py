import pandas as pd
import random

# Define the tickers, company names, and regions
tickers = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'FB', 'JNJ', 'V', 'PG', 'JPM', 'UNH',
           'NESN.SW', 'ROG.SW', 'NOVN.SW', 'LIN.DE', 'ALV.DE',
           '7203.T', '9984.T', '6861.T', '9433.T', '4063.T',
           '005930.KS', '000660.KS', '035420.KS', '035720.KS', '051910.KS',
           '0700.HK', '1299.HK', '0941.HK', '2318.HK', '1398.HK']

company_names = ['Apple Inc.', 'Alphabet Inc.', 'Amazon.com, Inc.', 'Microsoft Corporation', 'Facebook, Inc.',
                 'Johnson & Johnson', 'Visa Inc.', 'Procter & Gamble Co', 'JPMorgan Chase & Co', 'UnitedHealth Group Inc.',
                 'Nestlé SA', 'Roche Holding AG', 'Novartis AG', 'Linde plc', 'Allianz SE',
                 'Toyota Motor Corp.', 'SoftBank Group Corp.', 'Keyence Corporation', 'KDDI Corporation', 'Shin-Etsu Chemical Co., Ltd.',
                 'Samsung Electronics Co., Ltd.', 'SK Hynix Inc.', 'NAVER Corporation', 'Kakao Corporation', 'LG Chem Ltd.',
                 'Tencent Holdings Limited', 'AIA Group Limited', 'China Mobile Limited', 'Ping An Insurance (Group) Company of China, Ltd.', 'Industrial and Commercial Bank of China Limited']

regions = ['US'] * 10 + ['Europe'] * 5 + ['Japan'] * 5 + ['Korea'] * 5 + ['Hong Kong'] * 5

# Create a dictionary to store the portfolio data
portfolio_data = {
    'Ticker': [],
    'Company Name': [],
    'Region': [],
    'Market Value': [],
    '% of Portfolio': [],
    'Total Shares': [],
    'Price in Local Currency': []
}

# Generate random data for the portfolio
total_market_value = 75000000  # Total market value of the portfolio
selected_tickers = random.sample(list(zip(tickers, company_names, regions)), 25)

for ticker, company_name, region in selected_tickers:
    market_value = random.uniform(0.01, 0.1) * total_market_value
    portfolio_percentage = market_value / total_market_value
    
    if region == 'Japan':
        total_shares = random.randint(1, 100) * 100  # Round Japanese shares to the nearest 100
        market_value_formatted = f"¥{market_value:,.0f}"
        price_formatted = f"¥{round(random.uniform(1000, 10000))}"
    elif region == 'Europe':
        total_shares = random.randint(100, 10000)
        market_value_formatted = f"€{market_value:,.0f}"
        price_formatted = f"€{round(random.uniform(10, 1000))}"
    elif region == 'Korea':
        total_shares = random.randint(100, 10000)
        market_value_formatted = f"₩{market_value:,.0f}"
        price_formatted = f"₩{round(random.uniform(10000, 100000))}"
    elif region == 'Hong Kong':
        total_shares = random.randint(100, 10000)
        market_value_formatted = f"HK${market_value:,.0f}"
        price_formatted = f"HK${round(random.uniform(10, 1000))}"
    else:
        total_shares = random.randint(100, 10000)
        market_value_formatted = f"${market_value:,.0f}"
        price_formatted = f"${round(random.uniform(10, 1000))}"
    
    portfolio_data['Ticker'].append(ticker)
    portfolio_data['Company Name'].append(company_name)
    portfolio_data['Region'].append(region)
    portfolio_data['Market Value'].append(market_value_formatted)  # Assign only the formatted market value
    portfolio_data['% of Portfolio'].append(f"{portfolio_percentage:.2%}")
    portfolio_data['Total Shares'].append(total_shares)
    portfolio_data['Price in Local Currency'].append(price_formatted)

# Create the portfolio dataframe
portfolio_df = pd.DataFrame(portfolio_data)

# Sort the dataframe by "% of Portfolio" in descending order
portfolio_df = portfolio_df.sort_values(by='% of Portfolio', ascending=False)

# Reset the index after sorting
portfolio_df = portfolio_df.reset_index(drop=True)

def sell_portfolio(portfolio_df, sell_percentage):
    # Create a copy of the original dataframe to avoid modifying the original data
    portfolio_df_copy = portfolio_df.copy()

    # Remove currency symbols and commas from the 'Market Value' column for calculations
    portfolio_df_copy['Market Value'] = portfolio_df_copy['Market Value'].replace(r'[^\d.]', '', regex=True).astype(float)

    # Calculate the total market value of the portfolio
    total_market_value = portfolio_df_copy['Market Value'].sum()

    # Calculate the amount to sell
    sell_amount = total_market_value * sell_percentage

    # Calculate the sell ratio for each stock
    portfolio_df_copy['Sell Ratio'] = portfolio_df_copy['Market Value'] / total_market_value

    # Calculate the amount to sell for each stock
    portfolio_df_copy['Sell Amount'] = sell_amount * portfolio_df_copy['Sell Ratio']

    # Update the market value for each stock after selling
    portfolio_df_copy['Market Value'] -= portfolio_df_copy['Sell Amount']

    # Update price information to perform share calculations
    portfolio_df_copy['Price in Local Currency'] = portfolio_df_copy['Price in Local Currency'].replace(r'[^\d.]', '', regex=True).astype(float)

    # Update the total shares for each stock after selling
    for i in portfolio_df_copy.index:
        if portfolio_df_copy.loc[i, 'Region'] == 'Japan':
            # Round to the nearest 100 shares for Japanese stocks
            shares = (portfolio_df_copy.loc[i, 'Market Value'] / portfolio_df_copy.loc[i, 'Price in Local Currency'])
            rounded_shares = round(shares / 100) * 100
            portfolio_df_copy.loc[i, 'Total Shares'] = rounded_shares
        else:
            # Normal rounding for other regions
            shares = (portfolio_df_copy.loc[i, 'Market Value'] / portfolio_df_copy.loc[i, 'Price in Local Currency']).round()
            portfolio_df_copy.loc[i, 'Total Shares'] = shares

    # Update the percentage of the portfolio for each stock after selling
    new_total_market_value = portfolio_df_copy['Market Value'].sum()
    portfolio_df_copy['% of Portfolio'] = (portfolio_df_copy['Market Value'] / new_total_market_value).apply(lambda x: f"{x:.2%}")

    # Reformat values to include currency symbols and commas
    for region in portfolio_df_copy['Region'].unique():
        if region == 'Japan':
            currency_symbol = '¥'
        elif region == 'Europe':
            currency_symbol = '€'
        elif region == 'Korea':
            currency_symbol = '₩'
        elif region == 'Hong Kong':
            currency_symbol = 'HK$'
        else:
            currency_symbol = '$'
        
        region_mask = portfolio_df_copy['Region'] == region
        portfolio_df_copy.loc[region_mask, 'Market Value'] = currency_symbol + portfolio_df_copy.loc[region_mask, 'Market Value'].apply(lambda x: f"{x:,.0f}")
        portfolio_df_copy.loc[region_mask, 'Price in Local Currency'] = currency_symbol + portfolio_df_copy.loc[region_mask, 'Price in Local Currency'].apply(lambda x: f"{x:,.0f}")

    # Drop the temporary columns
    portfolio_df_copy.drop(['Sell Ratio', 'Sell Amount'], axis=1, inplace=True)

    return portfolio_df_copy

# Example usage
sold_portfolio_df = sell_portfolio(portfolio_df, 0.12)

def summarize_trade(portfolio_df):
    # Example conversion rates; replace these with dynamic retrieval or accurate static values
    conversion_rates = {
        'USD': 1.0,
        'JPY': 0.0073,
        'EUR': 1.1,
        'KRW': 0.00074,
        'HKD': 0.13
    }

    # Removing currency symbols and converting market values to floats for calculations
    portfolio_df['Market Value Numeric'] = portfolio_df['Market Value'].replace(r'[^\d.]', '', regex=True).astype(float)

    # Summarize securities by region
    total_usd_value = 0
    summary_messages = []
    for region in portfolio_df['Region'].unique():
        region_securities = portfolio_df[portfolio_df['Region'] == region]
        shares = region_securities['Total Shares'].sum()
        market_value = region_securities['Market Value Numeric'].sum()

        # Get the currency symbol from the original market value string
        currency_symbol = region_securities.iloc[0]['Market Value'][0]

        # Determine the currency from the region
        if region == 'Japan':
            currency = 'JPY'
        elif region == 'Europe':
            currency = 'EUR'
        elif region == 'Korea':
            currency = 'KRW'
        elif region == 'Hong Kong':
            currency = 'HKD'
        else:
            currency = 'USD'
        
        # Convert market value to USD
        market_value_usd = market_value * conversion_rates[currency]
        total_usd_value += market_value_usd
        
        # Format message for the region
        summary_message = f"Sending {shares} shares of {region} securities for {currency_symbol}{market_value:,.0f} (approx. ${market_value_usd:,.0f} USD)."
        summary_messages.append(summary_message)

    # Construct the full summary message
    total_summary = f"Total Market Value in USD: ${total_usd_value:,.0f}"
    summary_messages.append(total_summary)
    
    return "\n".join(summary_messages)

# Example usage
trade_summary = summarize_trade(portfolio_df)
print(trade_summary)
