import yfinance as yf
import pandas as pd
import numpy as np

TICKERS = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS",
    "LT.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "MARUTI.NS",
    "AXISBANK.NS", "KOTAKBANK.NS", "SUNPHARMA.NS", "HINDUNILVR.NS",
    "BAJFINANCE.NS",
]
BENCHMARK = "^NSEI"
START = "2021-01-01"
END = "2025-12-31"
CAPITAL = 100000
COST = 0.002
TOP_N = 10


def cagr(series):
    years = (series.index[-1] - series.index[0]).days / 365.25
    return float((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1)


def annual_vol(series):
    return float(series.pct_change().dropna().std() * np.sqrt(12))


def sharpe(series):
    returns = series.pct_change().dropna()
    return float((returns.mean() / returns.std()) * np.sqrt(12)) if returns.std() != 0 else np.nan


def max_drawdown(series):
    return float((series / series.cummax() - 1).min())


def run_strategy(monthly_returns, monthly, bench_monthly, lookback):
    momentum = monthly.pct_change(lookback).shift(1)
    rows = []
    for date in monthly_returns.index:
        scores = momentum.loc[date].dropna() if date in momentum.index else pd.Series(dtype=float)
        rets = monthly_returns.loc[date].dropna()
        common = scores.index.intersection(rets.index)
        scores = scores[common]
        rets = rets[common]
        if len(scores) < TOP_N:
            continue
        selected = scores.sort_values(ascending=False).head(TOP_N).index
        net_return = rets[selected].mean() - COST
        rows.append((date, net_return, list(selected)))

    returns = pd.DataFrame([(d, r) for d, r, _ in rows], columns=["Date", "Return"]).set_index("Date")
    equity = CAPITAL * (1 + returns["Return"]).cumprod()
    bench_aligned = bench_monthly.loc[equity.index.min():equity.index.max()]
    bench_equity = CAPITAL * (1 + bench_aligned).cumprod()
    return equity, bench_equity, rows[-1][2]


def main():
    data = yf.download(TICKERS + [BENCHMARK], start=START, end=END, auto_adjust=True)["Close"]
    prices = data[TICKERS].dropna(how="all")
    bench = data[BENCHMARK].dropna()

    monthly = prices.resample("ME").last()
    monthly_returns = monthly.pct_change()
    bench_monthly = bench.resample("ME").last().pct_change().dropna()

    print("\nMomentum Lookback Comparison — Top 10")
    print("-" * 40)
    for lookback in [3, 6, 9, 12]:
        equity, bench_equity, latest = run_strategy(monthly_returns, monthly, bench_monthly, lookback)
        print(f"\n{lookback}-Month Momentum")
        print(f"Final Value: ₹{equity.iloc[-1]:,.2f}")
        print(f"CAGR: {cagr(equity):.2%}")
        print(f"Volatility: {annual_vol(equity):.2%}")
        print(f"Sharpe: {sharpe(equity):.2f}")
        print(f"Max Drawdown: {max_drawdown(equity):.2%}")
        print(f"Nifty Final: ₹{bench_equity.iloc[-1]:,.2f}")
        print(f"Nifty CAGR: {cagr(bench_equity):.2%}")
        print(f"Nifty Sharpe: {sharpe(bench_equity):.2f}")
        print(f"Latest selected: {latest}")


if __name__ == "__main__":
    main()
