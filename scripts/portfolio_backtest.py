import yfinance as yf
import pandas as pd
import numpy as np

TICKERS = ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS"]
BENCHMARK = "^NSEI"
START = "2021-01-01"
END = "2025-12-31"
CAPITAL = 100000
COST = 0.002


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


def main():
    data = yf.download(TICKERS + [BENCHMARK], start=START, end=END, auto_adjust=True)["Close"]
    prices = data[TICKERS].dropna()
    bench = data[BENCHMARK].dropna()

    monthly_prices = prices.resample("ME").last()
    monthly_returns = monthly_prices.pct_change().dropna()

    portfolio_returns = monthly_returns.mean(axis=1) - COST
    portfolio_equity = CAPITAL * (1 + portfolio_returns).cumprod()

    bench_monthly = bench.resample("ME").last().pct_change().dropna()
    bench_equity = CAPITAL * (1 + bench_monthly).cumprod()

    print("\nEqual-Weight Portfolio Backtest")
    print("-" * 40)
    print(f"Tickers: {', '.join(TICKERS)}")
    print(f"Rows monthly: {len(monthly_returns)}\n")
    print(f"Portfolio final value: ₹{portfolio_equity.iloc[-1]:,.2f}")
    print(f"Nifty 50 final value: ₹{bench_equity.iloc[-1]:,.2f}")
    print(f"Portfolio CAGR: {cagr(portfolio_equity):.2%}")
    print(f"Nifty 50 CAGR: {cagr(bench_equity):.2%}")
    print(f"Portfolio annual volatility: {annual_vol(portfolio_equity):.2%}")
    print(f"Nifty 50 annual volatility: {annual_vol(bench_equity):.2%}")
    print(f"Portfolio Sharpe: {sharpe(portfolio_equity):.2f}")
    print(f"Nifty 50 Sharpe: {sharpe(bench_equity):.2f}")
    print(f"Portfolio max drawdown: {max_drawdown(portfolio_equity):.2%}")
    print(f"Nifty 50 max drawdown: {max_drawdown(bench_equity):.2%}")


if __name__ == "__main__":
    main()
