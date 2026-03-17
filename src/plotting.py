import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

PATH_COLOR = "#7DCFCF"
MEDIAN_COLOR = "#FFFFFF"
LOW_COLOR = "#FF4D8D"
HIGH_COLOR = "#00FFB3"
RETIRE_COLOR = "#FF9A5C"


def plot_paths(balances, years_to_retirement, path_color="#7DCFCF", median_color='#FFFFFF', low_color='#FF4D8D', high_color='#00FFB3', retire_color='#FF9A5C'):
    years = np.arange(balances.shape[0])

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_color("#0A2E2E")
    ax.set_facecolor("#0D3D3D")

    for i in range(200):
        plt.plot(years, balances[:, i] / 1e6, color=path_color, alpha=0.1)

    # plot median path
    ax.plot(
        years,
        np.percentile(balances, 50, axis=1) / 1e6,
        color=median_color,
        linewidth=2,
        linestyle="--",
        label="median",
    )

    # plot 10th percentile
    ax.plot(
        years,
        np.percentile(balances, 10, axis=1) / 1e6,
        color=low_color,
        linewidth=2,
        linestyle="--",
        label="10th percentile",
    )

    # plot 90th percentile
    ax.plot(
        years,
        np.percentile(balances, 90, axis=1) / 1e6,
        color=high_color,
        linewidth=2,
        linestyle="--",
        label="90th percentile",
    )

    ax.axvline(x=years_to_retirement, color=retire_color, linestyle=":", label="Retirement")

    ax.set_xlabel("Year", color="white")
    ax.set_ylabel("Balance ($M)", color="white")
    ax.tick_params(colors="white")

    ax.legend(facecolor="#0D3D3D", labelcolor="white")

    for spine in ax.spines.values():
        spine.set_edgecolor("#333333")

    st.pyplot(fig)
