import numpy as np
import yfinance as yf

TRADING_DAYS_IN_YEAR = 252

def get_market_params(ticker="SPY", start="2000-01-01"):
    data = yf.download(ticker, start, progress=False)
    data.columns = data.columns.get_level_values(0)
    # natural log of today's price divided by yesterday's price
    log_returns = np.log(data["Close"] / data["Close"].shift(1).dropna())

    # annualized mean
    mu = float(log_returns.mean() * TRADING_DAYS_IN_YEAR)
    # annualized standard deviation
    sigma = float(log_returns.std() * np.sqrt(TRADING_DAYS_IN_YEAR))
    
    return mu, sigma