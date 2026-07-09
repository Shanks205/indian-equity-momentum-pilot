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
COST = 0.002

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


def run_top20_momentum(monthly_prices: pd.DataFrame, monthly_returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
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
        transaction_cost = turnover * COST
        net_return = gross_return - transaction_cost

        rows.append({
            "date": date,
            "gross_return": gross_return,
            "turnover": turnover,
            "transaction_cost": transaction_cost,
            "net_return": net_return,
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

    returns_df = pd.DataFrame(rows).set_index("date")
    holdings_df = pd.DataFrame(holdings_rows)

    return returns_df, holdings_df


def calendar_year_summary(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> pd.DataFrame:
    combined = pd.DataFrame({
        "strategy_return": strategy_returns,
        "benchmark_return": benchmark_returns,
    }).dropna()

    combined["year"] = combined.index.year

    rows = []

    for year, group in combined.groupby("year"):
        strategy_curve = (1 + group["strategy_return"]).cumprod()
        benchmark_curve = (1 + group["benchmark_return"]).cumprod()

        strategy_year_return = float(strategy_curve.iloc[-1] - 1)
        benchmark_year_return = float(benchmark_curve.iloc[-1] - 1)

        rows.append({
            "year": int(year),
            "months": len(group),
            "strategy_return": strategy_year_return,
            "benchmark_return": benchmark_year_return,
            "alpha": strategy_year_return - benchmark_year_return,
            "strategy_sharpe": sharpe_from_returns(group["strategy_return"]),
            "benchmark_sharpe": sharpe_from_returns(group["benchmark_return"]),
            "strategy_max_drawdown": max_drawdown(strategy_curve),
            "benchmark_max_drawdown": max_drawdown(benchmark_curve),
            "strategy_volatility": annual_vol_from_returns(group["strategy_return"]),
            "benchmark_volatility": annual_vol_from_returns(group["benchmark_return"]),
        })

    return pd.DataFrame(rows)


def consistency_summary(yearly: pd.DataFrame) -> dict:
    positive_alpha_years = int((yearly["alpha"] > 0).sum())
    total_years = int(len(yearly))
    positive_return_years = int((yearly["strategy_return"] > 0).sum())

    return {
        "years_tested": total_years,
        "positive_strategy_years": positive_return_years,
        "positive_alpha_years": positive_alpha_years,
        "alpha_hit_rate": positive_alpha_years / total_years if total_years else np.nan,
        "average_alpha": float(yearly["alpha"].mean()),
        "median_alpha": float(yearly["alpha"].median()),
        "best_year": int(yearly.sort_values("strategy_return", ascending=False).iloc[0]["year"]),
        "worst_year": int(yearly.sort_values("strategy_return", ascending=True).iloc[0]["year"]),
        "best_year_return": float(yearly["strategy_return"].max()),
        "worst_year_return": float(yearly["strategy_return"].min()),
    }


def main():
    print("Downloading broader universe data for V7...")
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

    strategy_returns_df, holdings_df = run_top20_momentum(monthly_prices, monthly_returns)

    strategy_returns = strategy_returns_df["net_return"]
    benchmark_aligned = benchmark_returns.loc[strategy_returns.index.min():strategy_returns.index.max()]

    yearly = calendar_year_summary(strategy_returns, benchmark_aligned)
    consistency = consistency_summary(yearly)

    strategy_equity = CAPITAL * (1 + strategy_returns).cumprod()
    benchmark_equity = CAPITAL * (1 + benchmark_aligned.loc[strategy_equity.index]).cumprod()

    equity_curves = pd.DataFrame({
        "strategy_equity": strategy_equity,
        "benchmark_equity": benchmark_equity,
    })

    summary_df = pd.DataFrame([{
        "top_n": TOP_N,
        "lookback_months": LOOKBACK,
        "strategy_final_value": float(strategy_equity.iloc[-1]),
        "benchmark_final_value": float(benchmark_equity.iloc[-1]),
        "strategy_cagr": cagr(strategy_equity),
        "benchmark_cagr": cagr(benchmark_equity),
        "strategy_sharpe": sharpe_from_returns(strategy_returns),
        "benchmark_sharpe": sharpe_from_returns(benchmark_aligned.loc[strategy_returns.index]),
        "strategy_max_drawdown": max_drawdown(strategy_equity),
        "benchmark_max_drawdown": max_drawdown(benchmark_equity),
        "average_turnover": float(strategy_returns_df["turnover"].mean()),
        **consistency,
    }])

    dq.to_csv(OUTPUT_DIR / "momentum_v7_data_quality.csv", index=False)
    strategy_returns_df.reset_index().to_csv(OUTPUT_DIR / "momentum_v7_monthly_returns.csv", index=False)
    holdings_df.to_csv(OUTPUT_DIR / "momentum_v7_holdings.csv", index=False)
    yearly.to_csv(OUTPUT_DIR / "momentum_v7_calendar_year_returns.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "momentum_v7_summary.csv", index=False)
    equity_curves.reset_index().rename(columns={"index": "date"}).to_csv(
        OUTPUT_DIR / "momentum_v7_equity_curves.csv",
        index=False,
    )

    print("\nMomentum Walk-Forward V7 Summary")
    print("-" * 32)
    cols = [
        "strategy_final_value",
        "benchmark_final_value",
        "strategy_cagr",
        "benchmark_cagr",
        "strategy_sharpe",
        "benchmark_sharpe",
        "strategy_max_drawdown",
        "average_turnover",
        "alpha_hit_rate",
        "average_alpha",
    ]
    print(summary_df[cols].to_string(index=False))

    print("\nCalendar-Year Validation")
    print("-" * 24)
    year_cols = [
        "year",
        "months",
        "strategy_return",
        "benchmark_return",
        "alpha",
        "strategy_sharpe",
        "benchmark_sharpe",
        "strategy_max_drawdown",
    ]
    print(yearly[year_cols].to_string(index=False))

    print("\nConsistency Summary")
    print("-" * 19)
    print(f"Years tested: {consistency['years_tested']}")
    print(f"Positive strategy years: {consistency['positive_strategy_years']}")
    print(f"Positive alpha years: {consistency['positive_alpha_years']}")
    print(f"Alpha hit rate: {consistency['alpha_hit_rate']:.2%}")
    print(f"Average alpha: {consistency['average_alpha']:.2%}")
    print(f"Median alpha: {consistency['median_alpha']:.2%}")
    print(f"Best year: {consistency['best_year']} ({consistency['best_year_return']:.2%})")
    print(f"Worst year: {consistency['worst_year']} ({consistency['worst_year_return']:.2%})")

    latest_date = holdings_df["date"].max()
    latest_holdings = holdings_df[holdings_df["date"] == latest_date].sort_values("rank")["ticker"].tolist()

    print("\nLatest holdings")
    print("-" * 15)
    print(", ".join(latest_holdings))

    print("\nSaved files")
    print("-" * 11)
    print("outputs/momentum_v7_data_quality.csv")
    print("outputs/momentum_v7_monthly_returns.csv")
    print("outputs/momentum_v7_holdings.csv")
    print("outputs/momentum_v7_calendar_year_returns.csv")
    print("outputs/momentum_v7_summary.csv")
    print("outputs/momentum_v7_equity_curves.csv")


if __name__ == "__main__":
    main()
