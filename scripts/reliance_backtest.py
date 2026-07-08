import yfinance as yf
import pandas as pd
import numpy as np

TICKER = "RELIANCE.NS"
START = "2021-01-01"
END = "2025-12-31"
CAPITAL = 100000
COST = 0.002


def load_close(ticker: str) -> pd.Series:
    df = yf.download(ticker, start=START, end=END, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df["Close"].dropna().astype(float)


def cagr(series: pd.Series) -> float:
    years = (series.index[-1] - series.index[0]).days / 365.25
    return float((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1)


def annual_vol(series: pd.Series) -> float:
    return float(series.pct_change().dropna().std() * np.sqrt(252))


def sharpe(series: pd.Series) -> float:
    returns = series.pct_change().dropna()
    return float((returns.mean() / returns.std()) * np.sqrt(252)) if returns.std() != 0 else np.nan


def max_drawdown(series: pd.Series) -> float:
    return float((series / series.cummax() - 1).min())


def run_backtest(short_window: int, long_window: int) -> None:
    close = load_close(TICKER)
    sma_short = close.rolling(short_window).mean()
    sma_long = close.rolling(long_window).mean()

    signal = (sma_short > sma_long).astype(int)
    position = signal.shift(1).fillna(0)

    returns = close.pct_change().fillna(0)
    trades = signal.diff().abs().fillna(0)
    strategy_returns = position * returns - trades * COST

    equity = CAPITAL * (1 + strategy_returns).cumprod()
    buy_hold = CAPITAL * (close / close.iloc[0])

    buy_signals = int(((sma_short > sma_long) & (sma_short.shift(1) <= sma_long.shift(1))).sum())
    sell_signals = int(((sma_short < sma_long) & (sma_short.shift(1) >= sma_long.shift(1))).sum())

    print(f"\n{TICKER} {short_window}/{long_window} SMA Backtest")
    print("-" * 40)
    print(f"Rows: {len(close)}")
    print(f"Latest Close: ₹{close.iloc[-1]:.2f}")
    print(f"Latest SMA{short_window}: ₹{sma_short.iloc[-1]:.2f}")
    print(f"Latest SMA{long_window}: ₹{sma_long.iloc[-1]:.2f}")
    print(f"Buy signals: {buy_signals}")
    print(f"Sell signals: {sell_signals}")
    print(f"Total signals: {buy_signals + sell_signals}\n")
    print(f"Strategy final value: ₹{equity.iloc[-1]:,.2f}")
    print(f"Buy & hold final value: ₹{buy_hold.iloc[-1]:,.2f}")
    print(f"Strategy CAGR: {cagr(equity):.2%}")
    print(f"Buy & hold CAGR: {cagr(buy_hold):.2%}")
    print(f"Strategy annual volatility: {annual_vol(equity):.2%}")
    print(f"Buy & hold annual volatility: {annual_vol(buy_hold):.2%}")
    print(f"Strategy Sharpe: {sharpe(equity):.2f}")
    print(f"Buy & hold Sharpe: {sharpe(buy_hold):.2f}")
    print(f"Strategy max drawdown: {max_drawdown(equity):.2%}")
    print(f"Buy & hold max drawdown: {max_drawdown(buy_hold):.2%}")


if __name__ == "__main__":
    run_backtest(20, 50)
    run_backtest(50, 200)
