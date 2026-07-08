import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

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
LOOKBACKS = [3, 6, 9, 12]

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def cagr(series: pd.Series) -> float:
    years = (series.index[-1] - series.index[0]).days / 365.25
    return float((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1)


def annual_vol(series: pd.Series) -> float:
    return float(series.pct_change().dropna().std() * np.sqrt(12))


def sharpe(series: pd.Series) -> float:
    returns = series.pct_change().dropna()
    return float((returns.mean() / returns.std()) * np.sqrt(12)) if returns.std() != 0 else np.nan


def max_drawdown(series: pd.Series) -> float:
    return float((series / series.cummax() - 1).min())


def calculate_turnover(previous_holdings: set, current_holdings: set, top_n: int) -> float:
    if not previous_holdings:
        return 1.0
    changed = len(previous_holdings.symmetric_difference(current_holdings))
    return changed / (2 * top_n)


def run_strategy(monthly_returns, monthly_prices, bench_monthly, lookback):
    momentum = monthly_prices.pct_change(lookback).shift(1)

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
        transaction_cost = turnover * COST
        net_return = gross_return - transaction_cost

        rows.append({
            "date": date,
            "lookback_months": lookback,
            "gross_return": gross_return,
            "turnover": turnover,
            "transaction_cost": transaction_cost,
            "net_return": net_return,
        })

        for rank, ticker in enumerate(selected, start=1):
            holdings_rows.append({
                "date": date,
                "lookback_months": lookback,
                "rank": rank,
                "ticker": ticker,
                "momentum_score": float(scores[ticker]),
                "monthly_return": float(rets[ticker]),
            })

        previous_holdings = selected_set

    returns_df = pd.DataFrame(rows).set_index("date")
    holdings_df = pd.DataFrame(holdings_rows)

    equity = CAPITAL * (1 + returns_df["net_return"]).cumprod()

    bench_aligned = bench_monthly.loc[equity.index.min():equity.index.max()]
    bench_equity = CAPITAL * (1 + bench_aligned).cumprod()

    summary = {
        "lookback_months": lookback,
        "top_n": TOP_N,
        "months_tested": len(equity),
        "strategy_final_value": equity.iloc[-1],
        "benchmark_final_value": bench_equity.iloc[-1],
        "strategy_cagr": cagr(equity),
        "benchmark_cagr": cagr(bench_equity),
        "strategy_volatility": annual_vol(equity),
        "benchmark_volatility": annual_vol(bench_equity),
        "strategy_sharpe": sharpe(equity),
        "benchmark_sharpe": sharpe(bench_equity),
        "strategy_max_drawdown": max_drawdown(equity),
        "benchmark_max_drawdown": max_drawdown(bench_equity),
        "average_turnover": returns_df["turnover"].mean(),
        "latest_holdings": ", ".join(
            holdings_df[holdings_df["date"] == holdings_df["date"].max()]
            .sort_values("rank")["ticker"]
            .tolist()
        ),
    }

    equity_df = pd.DataFrame({
        "strategy_equity": equity,
        "benchmark_equity": bench_equity,
    })

    return summary, returns_df, holdings_df, equity_df


def main():
    print("Downloading data...")
    data = yf.download(TICKERS + [BENCHMARK], start=START, end=END, auto_adjust=True)["Close"]

    prices = data[TICKERS].dropna(how="all")
    benchmark = data[BENCHMARK].dropna()

    monthly_prices = prices.resample("ME").last()
    monthly_returns = monthly_prices.pct_change()
    bench_monthly = benchmark.resample("ME").last().pct_change().dropna()

    all_summaries = []
    all_returns = []
    all_holdings = []
    all_equity = []

    for lookback in LOOKBACKS:
        summary, returns_df, holdings_df, equity_df = run_strategy(
            monthly_returns,
            monthly_prices,
            bench_monthly,
            lookback,
        )

        all_summaries.append(summary)

        returns_df = returns_df.reset_index()
        returns_df["lookback_months"] = lookback
        all_returns.append(returns_df)

        all_holdings.append(holdings_df)

        equity_df = equity_df.reset_index().rename(columns={"index": "date"})
        equity_df["lookback_months"] = lookback
        all_equity.append(equity_df)

    summary_df = pd.DataFrame(all_summaries)
    returns_out = pd.concat(all_returns, ignore_index=True)
    holdings_out = pd.concat(all_holdings, ignore_index=True)
    equity_out = pd.concat(all_equity, ignore_index=True)

    summary_df.to_csv(OUTPUT_DIR / "momentum_v2_summary.csv", index=False)
    returns_out.to_csv(OUTPUT_DIR / "momentum_v2_monthly_returns.csv", index=False)
    holdings_out.to_csv(OUTPUT_DIR / "momentum_v2_holdings.csv", index=False)
    equity_out.to_csv(OUTPUT_DIR / "momentum_v2_equity_curves.csv", index=False)

    print("\nMomentum Research V2 Summary")
    print("-" * 28)

    display_cols = [
        "lookback_months",
        "strategy_final_value",
        "benchmark_final_value",
        "strategy_cagr",
        "benchmark_cagr",
        "strategy_sharpe",
        "benchmark_sharpe",
        "strategy_max_drawdown",
        "average_turnover",
    ]

    print(summary_df[display_cols].to_string(index=False))

    best = summary_df.sort_values("strategy_sharpe", ascending=False).iloc[0]

    print("\nBest strategy by Sharpe")
    print("-" * 23)
    print(f"Lookback: {int(best['lookback_months'])} months")
    print(f"Final value: ₹{best['strategy_final_value']:,.2f}")
    print(f"CAGR: {best['strategy_cagr']:.2%}")
    print(f"Sharpe: {best['strategy_sharpe']:.2f}")
    print(f"Max drawdown: {best['strategy_max_drawdown']:.2%}")
    print(f"Average turnover: {best['average_turnover']:.2%}")
    print(f"Latest holdings: {best['latest_holdings']}")

    print("\nSaved files")
    print("-" * 11)
    print("outputs/momentum_v2_summary.csv")
    print("outputs/momentum_v2_monthly_returns.csv")
    print("outputs/momentum_v2_holdings.csv")
    print("outputs/momentum_v2_equity_curves.csv")


if __name__ == "__main__":
    main()
