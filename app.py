import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from simulation import get_market_params, run_simulation

st.set_page_config(page_title="Retirement Simulator", layout="wide")
st.title("Monte Carlo Retirement Simulator")
st.caption("Simulates 10,000 retirement savings paths using real market data.")

st.sidebar.header("Parameters")

starting_balance = st.sidebar.slider(
    "Starting Balance ($)",
    min_value=0,
    max_value=500000,
    value=50000,
    step=5000,
    format="$%d",
)

annual_contribution = st.sidebar.slider(
    "Annual Contribution ($)",
    min_value=0,
    max_value=50000,
    value=10000,
    step=1000,
    format="$%d",
)

years_to_retirement = st.sidebar.slider(
    "Years Until Retirement", min_value=5, max_value=50, value=30
)

years_in_retirement = st.sidebar.slider(
    "Years In Retirement", min_value=5, max_value=50, value=25
)

annual_withdrawal = st.sidebar.slider(
    "Annual Withdrawal ($)",
    min_value=10000,
    max_value=200000,
    value=60000,
    step=5000,
    format="$%d",
)


@st.cache_data
def load_params():
    return get_market_params("SPY", start="2000-01-01")


mu, sigma = load_params()

st.sidebar.markdown("---")

st.sidebar.markdown("**Calibrated from SPY (2000 - present)**")
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
    f"${median_at_retirement:,.0f}",
    help="Median savings balance at end of retirement",
)

years = np.arange(balances.shape[0])
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_color('#0e1117')
ax.set_facecolor('#0e1117')

for i in range(200):
    plt.plot(years, balances[:, i] / 1e6, color="steelblue", alpha=0.1)

# plot median path
ax.plot(
    years,
    np.percentile(balances, 50, axis=1) / 1e6,
    color="white",
    linewidth=2,
    linestyle="--",
    label="median",
)

# plot 10th percentile
ax.plot(
    years,
    np.percentile(balances, 10, axis=1) / 1e6,
    color="salmon",
    linewidth=2,
    linestyle="--",
    label="10th percentile",
)

# plot 90th percentile
ax.plot(
    years,
    np.percentile(balances, 90, axis=1) / 1e6,
    color="lightgreen",
    linewidth=2,
    linestyle="--",
    label="90th percentile",
)

ax.axvline(x=years_to_retirement, color="yellow", linestyle=":", label="Retirement")

ax.set_xlabel('Year', color='white')
ax.set_ylabel('Balance ($M)', color='white')
ax.tick_params(colors='white')

ax.legend(facecolor='#1e1e1e', labelcolor='white')

for spine in ax.spines.values():
    spine.set_edgecolor('#333333')

st.pyplot(fig)
