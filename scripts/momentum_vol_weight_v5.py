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
VOL_LOOKBACK = 6
TOP_NS = [10, 15, 20]
COST = 0.002

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


def calculate_turnover(previous_weights: pd.Series, current_weights: pd.Series) -> float:
    if previous_weights.empty and current_weights.empty:
        return 0.0

    all_tickers = previous_weights.index.union(current_weights.index)
    previous = previous_weights.reindex(all_tickers).fillna(0)
    current = current_weights.reindex(all_tickers).fillna(0)

    return float((current - previous).abs().sum() / 2)


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


def equal_weights(selected: list[str]) -> pd.Series:
    return pd.Series(1 / len(selected), index=selected)


def inverse_vol_weights(selected: list[str], vol_scores: pd.Series) -> pd.Series:
    selected_vol = vol_scores[selected].replace(0, np.nan).dropna()

    if selected_vol.empty:
        return equal_weights(selected)

    inv_vol = 1 / selected_vol
    weights = inv_vol / inv_vol.sum()

    # Re-add any missing selected tickers with zero weight.
    return weights.reindex(selected).fillna(0)


def run_strategy(monthly_prices, monthly_returns, bench_monthly, top_n, weighting_method):
    momentum = monthly_prices.pct_change(LOOKBACK).shift(1)
    volatility = monthly_returns.rolling(VOL_LOOKBACK).std().shift(1)

    rows = []
    holdings_rows = []
    previous_weights = pd.Series(dtype=float)

    for date in monthly_returns.index:
        scores = momentum.loc[date].dropna() if date in momentum.index else pd.Series(dtype=float)
        rets = monthly_returns.loc[date].dropna()
        vols = volatility.loc[date].dropna() if date in volatility.index else pd.Series(dtype=float)

        common = scores.index.intersection(rets.index)
        scores = scores[common]
        rets = rets[common]

        if len(scores) < top_n:
            continue

        selected = list(scores.sort_values(ascending=False).head(top_n).index)

        if weighting_method == "equal_weight":
            weights = equal_weights(selected)
        elif weighting_method == "inverse_vol":
            weights = inverse_vol_weights(selected, vols)
            weights = weights[weights > 0]
            selected = list(weights.index)
        else:
            raise ValueError(f"Unknown weighting method: {weighting_method}")

        selected_returns = rets[selected]
        gross_return = float((selected_returns * weights).sum())

        turnover = calculate_turnover(previous_weights, weights)
        transaction_cost = turnover * COST
        net_return = gross_return - transaction_cost

        rows.append({
            "date": date,
            "top_n": top_n,
            "weighting_method": weighting_method,
            "gross_return": gross_return,
            "turnover": turnover,
            "transaction_cost": transaction_cost,
            "net_return": net_return,
            "holdings_count": len(selected),
        })

        for rank, ticker in enumerate(selected, start=1):
            holdings_rows.append({
                "date": date,
                "top_n": top_n,
                "weighting_method": weighting_method,
                "rank": rank,
                "ticker": ticker,
                "weight": float(weights[ticker]),
                "momentum_score": float(scores[ticker]),
                "volatility_score": float(vols[ticker]) if ticker in vols.index else np.nan,
                "monthly_return": float(rets[ticker]),
            })

        previous_weights = weights.copy()

    returns_df = pd.DataFrame(rows).set_index("date")
    holdings_df = pd.DataFrame(holdings_rows)

    equity = CAPITAL * (1 + returns_df["net_return"]).cumprod()
    bench_aligned = bench_monthly.loc[equity.index.min():equity.index.max()]
    bench_equity = CAPITAL * (1 + bench_aligned).cumprod()

    latest_holdings = ""
    if not holdings_df.empty:
        latest_date = holdings_df["date"].max()
        latest_holdings = ", ".join(
            holdings_df[holdings_df["date"] == latest_date]
            .sort_values("rank")["ticker"]
            .tolist()
        )

    summary = {
        "top_n": top_n,
        "lookback_months": LOOKBACK,
        "vol_lookback_months": VOL_LOOKBACK,
        "weighting_method": weighting_method,
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
        "latest_holdings": latest_holdings,
    }

    equity_df = pd.DataFrame({
        "strategy_equity": equity,
        "benchmark_equity": bench_equity,
    })

    return summary, returns_df, holdings_df, equity_df


def main():
    print("Downloading broader universe data for V5...")
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
    bench_monthly = benchmark_monthly_prices.pct_change().dropna()

    summaries = []
    returns_all = []
    holdings_all = []
    equity_all = []

    for top_n in TOP_NS:
        for weighting_method in ["equal_weight", "inverse_vol"]:
            summary, returns_df, holdings_df, equity_df = run_strategy(
                monthly_prices,
                monthly_returns,
                bench_monthly,
                top_n,
                weighting_method,
            )

            summaries.append(summary)

            returns_df = returns_df.reset_index()
            returns_all.append(returns_df)

            holdings_all.append(holdings_df)

            equity_df = equity_df.reset_index().rename(columns={"index": "date"})
            equity_df["top_n"] = top_n
            equity_df["weighting_method"] = weighting_method
            equity_all.append(equity_df)

    summary_df = pd.DataFrame(summaries)
    returns_out = pd.concat(returns_all, ignore_index=True)
    holdings_out = pd.concat(holdings_all, ignore_index=True)
    equity_out = pd.concat(equity_all, ignore_index=True)

    dq.to_csv(OUTPUT_DIR / "momentum_v5_data_quality.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "momentum_v5_summary.csv", index=False)
    returns_out.to_csv(OUTPUT_DIR / "momentum_v5_monthly_returns.csv", index=False)
    holdings_out.to_csv(OUTPUT_DIR / "momentum_v5_holdings.csv", index=False)
    equity_out.to_csv(OUTPUT_DIR / "momentum_v5_equity_curves.csv", index=False)

    print("\nMomentum Volatility Weight V5 Summary")
    print("-" * 37)

    cols = [
        "top_n",
        "weighting_method",
        "strategy_final_value",
        "benchmark_final_value",
        "strategy_cagr",
        "benchmark_cagr",
        "strategy_sharpe",
        "benchmark_sharpe",
        "strategy_max_drawdown",
        "average_turnover",
    ]

    print(summary_df[cols].to_string(index=False))

    best = summary_df.sort_values("strategy_sharpe", ascending=False).iloc[0]

    print("\nBest V5 strategy by Sharpe")
    print("-" * 26)
    print(f"Top N: {int(best['top_n'])}")
    print(f"Weighting: {best['weighting_method']}")
    print(f"Lookback: {int(best['lookback_months'])} months")
    print(f"Vol lookback: {int(best['vol_lookback_months'])} months")
    print(f"Final value: ₹{best['strategy_final_value']:,.2f}")
    print(f"CAGR: {best['strategy_cagr']:.2%}")
    print(f"Sharpe: {best['strategy_sharpe']:.2f}")
    print(f"Max drawdown: {best['strategy_max_drawdown']:.2%}")
    print(f"Average turnover: {best['average_turnover']:.2%}")
    print(f"Latest holdings: {best['latest_holdings']}")

    print("\nSaved files")
    print("-" * 11)
    print("outputs/momentum_v5_data_quality.csv")
    print("outputs/momentum_v5_summary.csv")
    print("outputs/momentum_v5_monthly_returns.csv")
    print("outputs/momentum_v5_holdings.csv")
    print("outputs/momentum_v5_equity_curves.csv")


if __name__ == "__main__":
    main()
