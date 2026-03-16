import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

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

    print(f"mu: {mu:.4f}, sigma: {sigma:.4f}")

    return mu, sigma


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

        # if still working, add annual contribution
        # otherwise, draw down savings
        if t <= years_to_retirement:
            balances[t] += annual_contribution
        else:
            balances[t] -= annual_withdrawal

        # ensure no negative balances
        balances[t] = np.maximum(balances[t], 0)

    return balances


def plot_balances(balances, years_to_retirement):
    # generate labels for years for x-axis
    years = np.arange(balances.shape[0])

    plt.figure(figsize=(12, 6))

    for i in range(200):
        plt.plot(years, balances[:, i] / 1e6, color="steelblue", alpha=0.05)

    # plot median path
    plt.plot(
        years,
        np.percentile(balances, 50, axis=1) / 1e6,
        color="white",
        linewidth=2,
        linestyle="--",
        label="median",
    )

    # plot 10th percentile
    plt.plot(
        years,
        np.percentile(balances, 10, axis=1) / 1e6,
        color="salmon",
        linewidth=2,
        linestyle="--",
        label="10th percentile",
    )

    # plot 90th percentile
    plt.plot(
        years,
        np.percentile(balances, 90, axis=1) / 1e6,
        color="lightgreen",
        linewidth=2,
        linestyle="--",
        label="90th percentile",
    )

    plt.axvline(
        x=years_to_retirement, color="yellow", linestyle=":", label="Retirement"
    )

    plt.xlabel("Year")
    plt.ylabel("Balance ($M)")
    plt.title("Monte Carlo Retirement Simulation")
    plt.legend()
    plt.tight_layout()

    plt.savefig("simulation.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    mu, sigma = get_market_params(ticker="SPY", start="2000-01-01")

    balances = run_simulation(
        starting_balance=50000,
        annual_contribution=10000,
        years_to_retirement=30,
        years_in_retirement=25,
        annual_withdrawal=60000,
        mu=mu,
        sigma=sigma,
        n=10000,
    )

    ruin = (balances[-1] == 0).mean()
    print(f'Ruin probability: {ruin:.1%}')
    print(f'Median final balance: ${np.median(balances[-1]):,.0f}')

    plot_balances(balances, years_to_retirement=30)
