import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

TICKERS = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS",
    "LT.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "MARUTI.NS",
    "AXISBANK.NS", "KOTAKBANK.NS", "SUNPHARMA.NS", "HINDUNILVR.NS",
    "BAJFINANCE.NS", "ASIANPAINT.NS", "M&M.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "NESTLEIND.NS", "POWERGRID.NS", "NTPC.NS",
    "ONGC.NS", "COALINDIA.NS", "TATASTEEL.NS", "JSWSTEEL.NS",
    "HCLTECH.NS", "TECHM.NS", "WIPRO.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "BAJAJFINSV.NS", "GRASIM.NS", "CIPLA.NS",
    "DRREDDY.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "HINDALCO.NS",
    "INDUSINDBK.NS", "BRITANNIA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS",
    "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "BPCL.NS", "SBILIFE.NS",
    "HDFCLIFE.NS", "SHRIRAMFIN.NS", "TATACONSUM.NS", "UPL.NS",
]

BENCHMARK = "^NSEI"
START = "2021-01-01"
END = "2025-12-31"
CAPITAL = 100000

LOOKBACK = 12
TOP_N = 20

# Cost per unit of turnover.
# Example: 0.002 = 0.20%
COST_LEVELS = [0.000, 0.001, 0.002, 0.003, 0.005, 0.010]

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def cagr(series: pd.Series) -> float:
    years = (series.index[-1] - series.index[0]).days / 365.25
    if years <= 0:
        return np.nan
    return float((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1)


def annual_vol_from_returns(returns: pd.Series) -> float:
    returns = returns.dropna()
    return float(returns.std() * np.sqrt(12)) if len(returns) > 1 else np.nan


def sharpe_from_returns(returns: pd.Series) -> float:
    returns = returns.dropna()
    if len(returns) <= 1 or returns.std() == 0:
        return np.nan
    return float((returns.mean() / returns.std()) * np.sqrt(12))


def max_drawdown(series: pd.Series) -> float:
    return float((series / series.cummax() - 1).min())


def calculate_turnover(previous_holdings: set, current_holdings: set, top_n: int) -> float:
    if not previous_holdings:
        return 1.0

    changed = len(previous_holdings.symmetric_difference(current_holdings))
    return changed / (2 * top_n)


def data_quality_report(prices: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for ticker in prices.columns:
        s = prices[ticker].dropna()
        rows.append({
            "ticker": ticker,
            "rows": len(s),
            "first_date": s.index.min(),
            "last_date": s.index.max(),
            "missing_values": int(prices[ticker].isna().sum()),
            "usable": len(s) >= 900,
        })

    return pd.DataFrame(rows)


def build_gross_returns_and_turnover(monthly_prices: pd.DataFrame, monthly_returns: pd.DataFrame):
    momentum = monthly_prices.pct_change(LOOKBACK).shift(1)

    rows = []
    holdings_rows = []
    previous_holdings = set()

    for date in monthly_returns.index:
        scores = momentum.loc[date].dropna() if date in momentum.index else pd.Series(dtype=float)
        rets = monthly_returns.loc[date].dropna()

        common = scores.index.intersection(rets.index)
        scores = scores[common]
        rets = rets[common]

        if len(scores) < TOP_N:
            continue

        selected = list(scores.sort_values(ascending=False).head(TOP_N).index)
        selected_set = set(selected)

        gross_return = float(rets[selected].mean())
        turnover = calculate_turnover(previous_holdings, selected_set, TOP_N)

        rows.append({
            "date": date,
            "gross_return": gross_return,
            "turnover": turnover,
        })

        for rank, ticker in enumerate(selected, start=1):
            holdings_rows.append({
                "date": date,
                "rank": rank,
                "ticker": ticker,
                "weight": 1 / TOP_N,
                "momentum_score": float(scores[ticker]),
                "monthly_return": float(rets[ticker]),
            })

        previous_holdings = selected_set

    base_returns = pd.DataFrame(rows).set_index("date")
    holdings = pd.DataFrame(holdings_rows)

    return base_returns, holdings


def evaluate_cost_level(base_returns: pd.DataFrame, benchmark_returns: pd.Series, cost: float):
    strategy_returns = base_returns.copy()
    strategy_returns["transaction_cost"] = strategy_returns["turnover"] * cost
    strategy_returns["net_return"] = strategy_returns["gross_return"] - strategy_returns["transaction_cost"]

    strategy_series = strategy_returns["net_return"]
    benchmark_aligned = benchmark_returns.loc[strategy_series.index.min():strategy_series.index.max()]
    benchmark_aligned = benchmark_aligned.loc[strategy_series.index]

    strategy_equity = CAPITAL * (1 + strategy_series).cumprod()
    benchmark_equity = CAPITAL * (1 + benchmark_aligned).cumprod()

    return {
        "cost": cost,
        "cost_percent": cost * 100,
        "strategy_final_value": float(strategy_equity.iloc[-1]),
        "benchmark_final_value": float(benchmark_equity.iloc[-1]),
        "strategy_cagr": cagr(strategy_equity),
        "benchmark_cagr": cagr(benchmark_equity),
        "strategy_sharpe": sharpe_from_returns(strategy_series),
        "benchmark_sharpe": sharpe_from_returns(benchmark_aligned),
        "strategy_max_drawdown": max_drawdown(strategy_equity),
        "benchmark_max_drawdown": max_drawdown(benchmark_equity),
        "average_turnover": float(base_returns["turnover"].mean()),
        "average_monthly_transaction_cost": float(strategy_returns["transaction_cost"].mean()),
        "beats_benchmark_cagr": bool(cagr(strategy_equity) > cagr(benchmark_equity)),
        "beats_benchmark_sharpe": bool(sharpe_from_returns(strategy_series) > sharpe_from_returns(benchmark_aligned)),
    }, strategy_returns, pd.DataFrame({
        "strategy_equity": strategy_equity,
        "benchmark_equity": benchmark_equity,
    })


def main():
    print("Downloading broader universe data for V8...")
    data = yf.download(TICKERS + [BENCHMARK], start=START, end=END, auto_adjust=True)["Close"]

    prices = data[TICKERS]
    benchmark = data[BENCHMARK].dropna()

    dq = data_quality_report(prices)
    usable_tickers = dq[dq["usable"]]["ticker"].tolist()

    print(f"\nUniverse requested: {len(TICKERS)}")
    print(f"Usable tickers: {len(usable_tickers)}")
    print(f"Excluded tickers: {len(TICKERS) - len(usable_tickers)}")

    excluded = dq[~dq["usable"]]["ticker"].tolist()
    if excluded:
        print(f"Excluded: {excluded}")

    prices = prices[usable_tickers].dropna(how="all")

    monthly_prices = prices.resample("ME").last()
    monthly_returns = monthly_prices.pct_change()

    benchmark_monthly_prices = benchmark.resample("ME").last()
    benchmark_returns = benchmark_monthly_prices.pct_change().dropna()

    base_returns, holdings = build_gross_returns_and_turnover(monthly_prices, monthly_returns)

    summaries = []
    returns_all = []
    equity_all = []

    for cost in COST_LEVELS:
        summary, returns_df, equity_df = evaluate_cost_level(base_returns, benchmark_returns, cost)

        summaries.append(summary)

        returns_out = returns_df.reset_index()
        returns_out["cost"] = cost
        returns_all.append(returns_out)

        equity_out = equity_df.reset_index().rename(columns={"index": "date"})
        equity_out["cost"] = cost
        equity_all.append(equity_out)

    summary_df = pd.DataFrame(summaries)
    returns_all_df = pd.concat(returns_all, ignore_index=True)
    equity_all_df = pd.concat(equity_all, ignore_index=True)

    dq.to_csv(OUTPUT_DIR / "momentum_v8_data_quality.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "momentum_v8_summary.csv", index=False)
    returns_all_df.to_csv(OUTPUT_DIR / "momentum_v8_monthly_returns.csv", index=False)
    holdings.to_csv(OUTPUT_DIR / "momentum_v8_holdings.csv", index=False)
    equity_all_df.to_csv(OUTPUT_DIR / "momentum_v8_equity_curves.csv", index=False)

    print("\nMomentum Cost Sensitivity V8 Summary")
    print("-" * 36)

    cols = [
        "cost_percent",
        "strategy_final_value",
        "benchmark_final_value",
        "strategy_cagr",
        "benchmark_cagr",
        "strategy_sharpe",
        "benchmark_sharpe",
        "strategy_max_drawdown",
        "average_turnover",
        "average_monthly_transaction_cost",
        "beats_benchmark_cagr",
        "beats_benchmark_sharpe",
    ]

    print(summary_df[cols].to_string(index=False))

    worst_cost = summary_df.sort_values("cost", ascending=False).iloc[0]
    highest_cost_beating_cagr = summary_df[summary_df["beats_benchmark_cagr"]]
    highest_cost_beating_sharpe = summary_df[summary_df["beats_benchmark_sharpe"]]

    print("\nCost Robustness Summary")
    print("-" * 23)

    if not highest_cost_beating_cagr.empty:
        row = highest_cost_beating_cagr.sort_values("cost", ascending=False).iloc[0]
        print(f"Highest cost still beating benchmark CAGR: {row['cost_percent']:.2f}%")
    else:
        print("Strategy does not beat benchmark CAGR at any tested cost level.")

    if not highest_cost_beating_sharpe.empty:
        row = highest_cost_beating_sharpe.sort_values("cost", ascending=False).iloc[0]
        print(f"Highest cost still beating benchmark Sharpe: {row['cost_percent']:.2f}%")
    else:
        print("Strategy does not beat benchmark Sharpe at any tested cost level.")

    print(f"At highest tested cost ({worst_cost['cost_percent']:.2f}%):")
    print(f"Final value: ₹{worst_cost['strategy_final_value']:,.2f}")
    print(f"CAGR: {worst_cost['strategy_cagr']:.2%}")
    print(f"Sharpe: {worst_cost['strategy_sharpe']:.2f}")
    print(f"Max drawdown: {worst_cost['strategy_max_drawdown']:.2%}")
    print(f"Benchmark CAGR: {worst_cost['benchmark_cagr']:.2%}")
    print(f"Benchmark Sharpe: {worst_cost['benchmark_sharpe']:.2f}")

    latest_date = holdings["date"].max()
    latest_holdings = holdings[holdings["date"] == latest_date].sort_values("rank")["ticker"].tolist()

    print("\nLatest holdings")
    print("-" * 15)
    print(", ".join(latest_holdings))

    print("\nSaved files")
    print("-" * 11)
    print("outputs/momentum_v8_data_quality.csv")
    print("outputs/momentum_v8_summary.csv")
    print("outputs/momentum_v8_monthly_returns.csv")
    print("outputs/momentum_v8_holdings.csv")
    print("outputs/momentum_v8_equity_curves.csv")


if __name__ == "__main__":
    main()
