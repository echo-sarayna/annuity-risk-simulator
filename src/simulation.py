import numpy as np
import yfinance as yf

def run_simulation(
    starting_balance,
    annual_contribution,
    years_to_retirement,
    years_in_retirement,
    annual_withdrawal,
    mu,
    sigma,
    n=10000,
):
    total_years = years_to_retirement + years_in_retirement
    # 2D array to store simulation results for n paths
    balances = np.zeros((total_years + 1, n))

    balances[0] = starting_balance

    for t in range(1, total_years + 1):
        # use random normal distribution with one random shock per simulation for the year
        Z = np.random.standard_normal(n)
        # formula for Geometric Brownian motion
        growth = np.exp((mu - 0.5 * sigma**2) + sigma * Z)

        # apply growth to last year's balance
        balances[t] = balances[t - 1] * growth

        # if not retired, add annual contribution
        # otherwise, draw down savings
        if t <= years_to_retirement:
            balances[t] += annual_contribution
        else:
            balances[t] -= annual_withdrawal

        # ensure no negative balances
        balances[t] = np.maximum(balances[t], 0)

    return balances

def search_tickers(query):
    results = yf.Search(query, max_results=6).quotes
    options = [
        f"{r['symbol']} - {r.get('shortname', r.get('longname', 'Unknown'))}"
        for r in results
        if "symbol" in r
    ]
    return options