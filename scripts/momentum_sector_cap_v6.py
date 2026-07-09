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

SECTOR_MAP = {
    "RELIANCE.NS": "Energy",
    "HDFCBANK.NS": "Financials",
    "ICICIBANK.NS": "Financials",
    "INFY.NS": "Information Technology",
    "TCS.NS": "Information Technology",
    "LT.NS": "Industrials",
    "ITC.NS": "Consumer Staples",
    "SBIN.NS": "Financials",
    "BHARTIARTL.NS": "Communication Services",
    "MARUTI.NS": "Consumer Discretionary",
    "AXISBANK.NS": "Financials",
    "KOTAKBANK.NS": "Financials",
    "SUNPHARMA.NS": "Healthcare",
    "HINDUNILVR.NS": "Consumer Staples",
    "BAJFINANCE.NS": "Financials",
    "ASIANPAINT.NS": "Materials",
    "M&M.NS": "Consumer Discretionary",
    "TITAN.NS": "Consumer Discretionary",
    "ULTRACEMCO.NS": "Materials",
    "NESTLEIND.NS": "Consumer Staples",
    "POWERGRID.NS": "Utilities",
    "NTPC.NS": "Utilities",
    "ONGC.NS": "Energy",
    "COALINDIA.NS": "Energy",
    "TATASTEEL.NS": "Materials",
    "JSWSTEEL.NS": "Materials",
    "HCLTECH.NS": "Information Technology",
    "TECHM.NS": "Information Technology",
    "WIPRO.NS": "Information Technology",
    "ADANIENT.NS": "Industrials",
    "ADANIPORTS.NS": "Industrials",
    "BAJAJFINSV.NS": "Financials",
    "GRASIM.NS": "Materials",
    "CIPLA.NS": "Healthcare",
    "DRREDDY.NS": "Healthcare",
    "EICHERMOT.NS": "Consumer Discretionary",
    "HEROMOTOCO.NS": "Consumer Discretionary",
    "HINDALCO.NS": "Materials",
    "INDUSINDBK.NS": "Financials",
    "BRITANNIA.NS": "Consumer Staples",
    "DIVISLAB.NS": "Healthcare",
    "APOLLOHOSP.NS": "Healthcare",
    "TATAMOTORS.NS": "Consumer Discretionary",
    "BAJAJ-AUTO.NS": "Consumer Discretionary",
    "BPCL.NS": "Energy",
    "SBILIFE.NS": "Financials",
    "HDFCLIFE.NS": "Financials",
    "SHRIRAMFIN.NS": "Financials",
    "TATACONSUM.NS": "Consumer Staples",
    "UPL.NS": "Materials",
}

BENCHMARK = "^NSEI"
START = "2021-01-01"
END = "2025-12-31"
CAPITAL = 100000

LOOKBACK = 12
TOP_N = 20
SECTOR_CAPS = [3, 4, 5]
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
            "sector": SECTOR_MAP.get(ticker, "Unknown"),
            "rows": len(s),
            "first_date": s.index.min(),
            "last_date": s.index.max(),
            "missing_values": int(prices[ticker].isna().sum()),
            "usable": len(s) >= 900,
        })

    return pd.DataFrame(rows)


def apply_sector_cap(sorted_scores: pd.Series, sector_cap: int, top_n: int) -> list[str]:
    selected = []
    sector_counts = {}

    for ticker in sorted_scores.index:
        sector = SECTOR_MAP.get(ticker, "Unknown")
        current_count = sector_counts.get(sector, 0)

        if current_count < sector_cap:
            selected.append(ticker)
            sector_counts[sector] = current_count + 1

        if len(selected) == top_n:
            break

    return selected


def run_strategy(monthly_prices, monthly_returns, bench_monthly, sector_cap):
    momentum = monthly_prices.pct_change(LOOKBACK).shift(1)

    rows = []
    holdings_rows = []
    sector_rows = []
    previous_holdings = set()

    for date in monthly_returns.index:
        scores = momentum.loc[date].dropna() if date in momentum.index else pd.Series(dtype=float)
        rets = monthly_returns.loc[date].dropna()

        common = scores.index.intersection(rets.index)
        scores = scores[common]
        rets = rets[common]

        if len(scores) < TOP_N:
            continue

        sorted_scores = scores.sort_values(ascending=False)
        selected = apply_sector_cap(sorted_scores, sector_cap, TOP_N)

        if len(selected) < TOP_N:
            continue

        selected_set = set(selected)

        gross_return = float(rets[selected].mean())
        turnover = calculate_turnover(previous_holdings, selected_set, TOP_N)
        transaction_cost = turnover * COST
        net_return = gross_return - transaction_cost

        rows.append({
            "date": date,
            "top_n": TOP_N,
            "sector_cap": sector_cap,
            "gross_return": gross_return,
            "turnover": turnover,
            "transaction_cost": transaction_cost,
            "net_return": net_return,
            "holdings_count": len(selected),
        })

        sector_counts = {}

        for rank, ticker in enumerate(selected, start=1):
            sector = SECTOR_MAP.get(ticker, "Unknown")
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

            holdings_rows.append({
                "date": date,
                "top_n": TOP_N,
                "sector_cap": sector_cap,
                "rank": rank,
                "ticker": ticker,
                "sector": sector,
                "weight": 1 / TOP_N,
                "momentum_score": float(scores[ticker]),
                "monthly_return": float(rets[ticker]),
            })

        for sector, count in sector_counts.items():
            sector_rows.append({
                "date": date,
                "sector_cap": sector_cap,
                "sector": sector,
                "count": count,
                "weight": count / TOP_N,
            })

        previous_holdings = selected_set

    returns_df = pd.DataFrame(rows).set_index("date")
    holdings_df = pd.DataFrame(holdings_rows)
    sector_df = pd.DataFrame(sector_rows)

    equity = CAPITAL * (1 + returns_df["net_return"]).cumprod()
    bench_aligned = bench_monthly.loc[equity.index.min():equity.index.max()]
    bench_equity = CAPITAL * (1 + bench_aligned).cumprod()

    latest_holdings = ""
    latest_sector_exposure = ""

    if not holdings_df.empty:
        latest_date = holdings_df["date"].max()
        latest_holdings = ", ".join(
            holdings_df[holdings_df["date"] == latest_date]
            .sort_values("rank")["ticker"]
            .tolist()
        )

    if not sector_df.empty:
        latest_sector_date = sector_df["date"].max()
        latest_sector_exposure = ", ".join(
            sector_df[sector_df["date"] == latest_sector_date]
            .sort_values("weight", ascending=False)
            .apply(lambda row: f"{row['sector']}: {row['weight']:.0%}", axis=1)
            .tolist()
        )

    summary = {
        "top_n": TOP_N,
        "lookback_months": LOOKBACK,
        "sector_cap": sector_cap,
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
        "latest_sector_exposure": latest_sector_exposure,
    }

    equity_df = pd.DataFrame({
        "strategy_equity": equity,
        "benchmark_equity": bench_equity,
    })

    return summary, returns_df, holdings_df, sector_df, equity_df


def main():
    print("Downloading broader universe data for V6...")
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
    sector_all = []
    equity_all = []

    for sector_cap in SECTOR_CAPS:
        summary, returns_df, holdings_df, sector_df, equity_df = run_strategy(
            monthly_prices,
            monthly_returns,
            bench_monthly,
            sector_cap,
        )

        summaries.append(summary)

        returns_all.append(returns_df.reset_index())
        holdings_all.append(holdings_df)
        sector_all.append(sector_df)

        equity_df = equity_df.reset_index().rename(columns={"index": "date"})
        equity_df["sector_cap"] = sector_cap
        equity_all.append(equity_df)

    summary_df = pd.DataFrame(summaries)
    returns_out = pd.concat(returns_all, ignore_index=True)
    holdings_out = pd.concat(holdings_all, ignore_index=True)
    sector_out = pd.concat(sector_all, ignore_index=True)
    equity_out = pd.concat(equity_all, ignore_index=True)

    dq.to_csv(OUTPUT_DIR / "momentum_v6_data_quality.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "momentum_v6_summary.csv", index=False)
    returns_out.to_csv(OUTPUT_DIR / "momentum_v6_monthly_returns.csv", index=False)
    holdings_out.to_csv(OUTPUT_DIR / "momentum_v6_holdings.csv", index=False)
    sector_out.to_csv(OUTPUT_DIR / "momentum_v6_sector_exposure.csv", index=False)
    equity_out.to_csv(OUTPUT_DIR / "momentum_v6_equity_curves.csv", index=False)

    print("\nMomentum Sector Cap V6 Summary")
    print("-" * 30)

    cols = [
        "sector_cap",
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

    print("\nBest V6 strategy by Sharpe")
    print("-" * 26)
    print(f"Top N: {int(best['top_n'])}")
    print(f"Sector cap: {int(best['sector_cap'])} stocks per sector")
    print(f"Lookback: {int(best['lookback_months'])} months")
    print(f"Final value: ₹{best['strategy_final_value']:,.2f}")
    print(f"CAGR: {best['strategy_cagr']:.2%}")
    print(f"Sharpe: {best['strategy_sharpe']:.2f}")
    print(f"Max drawdown: {best['strategy_max_drawdown']:.2%}")
    print(f"Average turnover: {best['average_turnover']:.2%}")
    print(f"Latest sector exposure: {best['latest_sector_exposure']}")
    print(f"Latest holdings: {best['latest_holdings']}")

    print("\nSaved files")
    print("-" * 11)
    print("outputs/momentum_v6_data_quality.csv")
    print("outputs/momentum_v6_summary.csv")
    print("outputs/momentum_v6_monthly_returns.csv")
    print("outputs/momentum_v6_holdings.csv")
    print("outputs/momentum_v6_sector_exposure.csv")
    print("outputs/momentum_v6_equity_curves.csv")


if __name__ == "__main__":
    main()
