import yfinance as yf
import pandas as pd
from datetime import datetime
from tqdm import tqdm

# Load the lists of companies from Wikipedia for S&P 500 and NASDAQ-100.
sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
nasdaq100 = pd.read_html("https://en.wikipedia.org/wiki/NASDAQ-100")[4]

# Combine and deduplicate the stock codes.
stock_codes = list(set(sp500['Symbol'].tolist() + nasdaq100['Ticker'].tolist()))

def fetch_data(tickers):
    """ Fetches financial information for each ticker using yfinance with a progress bar. """
    stock_data = {}
    for ticker in tqdm(tickers, desc="Fetching data"):
        try:
            info = yf.Ticker(ticker).info
            if info:
                stock_data[ticker] = info
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")
    return stock_data

def filter_stocks(data):
    """ Filters stocks based on given financial criteria with a progress bar. """
    filtered_stocks = {}
    for ticker, d in tqdm(data.items(), desc="Filtering stocks"):
        try:
            # Check and log which condition fails
            if (d.get('operatingMargins', 0) > 0.10 and
                d.get('heldPercentInstitutions', 0) > 0.20 and
                d.get('debtToEquity', 1) < 1.5 and
                d.get('currentRatio', 0) > 1 and
                d.get('profitMargins', 0) > 0.05):
                print(f"Filtered out {ticker} due to not meeting criteria.")
                continue
            filtered_stocks[ticker] = d['previousClose']
        except KeyError as e:
            print(f"Key error for {ticker}: {e}")
            continue
    return filtered_stocks

def save_to_file(stocks, filename):
    """ Saves the filtered stock information to a file. """
    with open(filename, 'w') as f:
        for stock, price in stocks.items():
            f.write(f"{stock}: {price}\n")

# Fetch stock data
stock_data = fetch_data(stock_codes)

# Filter stocks based on the criteria
filtered_stocks = filter_stocks(stock_data)

# Save the results to a file
today = datetime.now().strftime("%Y-%m-%d")
filename = f"{today}_filtered_stocks.txt"
save_to_file(filtered_stocks, filename)
