import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

from src.data import get_market_params
from src.simulation import run_simulation, search_tickers
from src.plotting import plot_paths

st.set_page_config(page_title="Retirement Simulator", layout="wide")
st.title("Retirement Simulator")
st.caption(
    "Simulates 10,000 retirement savings paths using real market data, following Geometric Brownian Motion."
)

DEFAULTS = {
    "ticker": "S&P 500",
    "starting_balance": 10000,
    "annual_contribution": 10000,
    "years_to_retirement": 30,
    "years_in_retirement": 25,
    "annual_withdrawal": 20000,
}

for key, value in DEFAULTS.items():
    # save defaults in session state if user has NOT adjusted sliders
    if key not in st.session_state:
        print(f"{key} not in defsult")
        st.session_state[key] = value


st.sidebar.header("Parameters")


search_query = st.sidebar.text_input(
    "Search for a stock", key="ticker", placeholder="Apple, Tesla, SPY..."
)

options = search_tickers(search_query)

if not options:
    st.sidebar.warning("No results found. Please try a different search.")
    st.stop()

selected = st.sidebar.selectbox("Select ticker", options=options)

ticker = selected.split(" - ")[0].strip()


starting_balance = st.sidebar.slider(
    "Starting Balance ($)",
    min_value=0,
    max_value=500000,
    key="starting_balance",
    step=5000,
    format="$%d",
)

annual_contribution = st.sidebar.slider(
    "Annual Contribution ($)",
    min_value=0,
    max_value=50000,
    key="annual_contribution",
    step=1000,
    format="$%d",
)

years_to_retirement = st.sidebar.slider(
    "Years Until Retirement",
    min_value=5,
    max_value=50,
    key="years_to_retirement",
)

years_in_retirement = st.sidebar.slider(
    "Years In Retirement", min_value=5, max_value=50, key="years_in_retirement"
)

annual_withdrawal = st.sidebar.slider(
    "Annual Withdrawal ($)",
    min_value=0,
    max_value=200000,
    key="annual_withdrawal",
    step=5000,
    format="$%d",
)


@st.cache_data
def load_params(ticker="SPY"):
    return get_market_params(f"{ticker}", start="2000-01-01")


with st.spinner(f"Loading data for {ticker}..."):
    mu, sigma = load_params(ticker)


mu, sigma = load_params(ticker)

st.sidebar.markdown("---")

st.sidebar.markdown(f"**Calibrated from {ticker} (2000 - present)**")
st.sidebar.markdown(f"- Annual return (mu): `{mu:.4f}`")
st.sidebar.markdown(f"- Annual volatility (sigma): `{sigma:.4f}`")

balances = run_simulation(
    starting_balance=starting_balance,
    annual_contribution=annual_contribution,
    years_to_retirement=years_to_retirement,
    years_in_retirement=years_in_retirement,
    annual_withdrawal=annual_withdrawal,
    mu=mu,
    sigma=sigma,
    n=10000,
)


st.sidebar.markdown("---")

if st.sidebar.button("Reset to Default"):
    for key, value in DEFAULTS.items():
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


final_balances = balances[-1]
at_retirement = balances[years_to_retirement]
ruin_probability = (final_balances == 0).mean()
median_final = np.median(final_balances)
median_at_retirement = np.median(at_retirement)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Ruin Probability",
    f"{ruin_probability:.1%}",
    help="% of simulations where savings hit zero before end of retirement",
)

col2.metric(
    "Median Balance at Retirement",
    f"${median_at_retirement:,.0f}",
    help="Median savings balance at start of retirement",
)

col3.metric(
    "Median Final Balance",
    f"${median_final:,.0f}",
    help="Median savings balance at end of retirement",
)

PATH_COLOR = "#7DCFCF"
MEDIAN_COLOR = "#FFFFFF"
LOW_COLOR = "#FF4D8D"
HIGH_COLOR = "#00FFB3"
RETIRE_COLOR = "#FF9A5C"

plot_paths(balances, years_to_retirement, PATH_COLOR, MEDIAN_COLOR, LOW_COLOR, HIGH_COLOR, RETIRE_COLOR)