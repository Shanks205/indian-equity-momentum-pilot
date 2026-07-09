import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

SMALL_UNIVERSE = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS",
    "LT.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "MARUTI.NS",
    "AXISBANK.NS", "KOTAKBANK.NS", "SUNPHARMA.NS", "HINDUNILVR.NS",
    "BAJFINANCE.NS",
]

BROAD_UNIVERSE = [
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
COST = 0.002
SECTOR_CAP = 4

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def cagr(series: pd.Series) -> float:
    years = (series.index[-1] - series.index[0]).days / 365.25
    if years <= 0:
        return np.nan
    return float((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1)


def sharpe_from_returns(returns: pd.Series) -> float:
    returns = returns.dropna()
    if len(returns) <= 1 or returns.std() == 0:
        return np.nan
    return float((returns.mean() / returns.std()) * np.sqrt(12))


def annual_vol_from_returns(returns: pd.Series) -> float:
    returns = returns.dropna()
    return float(returns.std() * np.sqrt(12)) if len(returns) > 1 else np.nan


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
            "strategy_return": strategy_year_return,
            "benchmark_return": benchmark_year_return,
            "alpha": strategy_year_return - benchmark_year_return,
            "strategy_sharpe": sharpe_from_returns(group["strategy_return"]),
            "benchmark_sharpe": sharpe_from_returns(group["benchmark_return"]),
            "strategy_max_drawdown": max_drawdown(strategy_curve),
            "benchmark_max_drawdown": max_drawdown(benchmark_curve),
        })

    return pd.DataFrame(rows)


def run_momentum_strategy(
    strategy_name: str,
    monthly_prices: pd.DataFrame,
    monthly_returns: pd.DataFrame,
    benchmark_returns: pd.Series,
    top_n: int,
    sector_cap: int | None = None,
):
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

        if len(scores) < top_n:
            continue

        sorted_scores = scores.sort_values(ascending=False)

        if sector_cap is None:
            selected = list(sorted_scores.head(top_n).index)
        else:
            selected = apply_sector_cap(sorted_scores, sector_cap, top_n)

        if len(selected) < top_n:
            continue

        selected_set = set(selected)
        gross_return = float(rets[selected].mean())
        turnover = calculate_turnover(previous_holdings, selected_set, top_n)
        transaction_cost = turnover * COST
        net_return = gross_return - transaction_cost

        rows.append({
            "date": date,
            "strategy": strategy_name,
            "gross_return": gross_return,
            "turnover": turnover,
            "transaction_cost": transaction_cost,
            "net_return": net_return,
        })

        for rank, ticker in enumerate(selected, start=1):
            holdings_rows.append({
                "date": date,
                "strategy": strategy_name,
                "rank": rank,
                "ticker": ticker,
                "sector": SECTOR_MAP.get(ticker, "Unknown"),
                "weight": 1 / top_n,
                "momentum_score": float(scores[ticker]),
                "monthly_return": float(rets[ticker]),
            })

        previous_holdings = selected_set

    returns_df = pd.DataFrame(rows).set_index("date")
    holdings_df = pd.DataFrame(holdings_rows)

    strategy_series = returns_df["net_return"]
    benchmark_aligned = benchmark_returns.loc[strategy_series.index.min():strategy_series.index.max()]
    benchmark_aligned = benchmark_aligned.loc[strategy_series.index]

    strategy_equity = CAPITAL * (1 + strategy_series).cumprod()
    benchmark_equity = CAPITAL * (1 + benchmark_aligned).cumprod()

    yearly = calendar_year_summary(strategy_series, benchmark_aligned)
    alpha_hit_rate = float((yearly["alpha"] > 0).sum() / len(yearly)) if len(yearly) else np.nan
    positive_year_rate = float((yearly["strategy_return"] > 0).sum() / len(yearly)) if len(yearly) else np.nan

    latest_date = holdings_df["date"].max()
    latest_holdings = ", ".join(
        holdings_df[holdings_df["date"] == latest_date]
        .sort_values("rank")["ticker"]
        .tolist()
    )

    summary = {
        "strategy": strategy_name,
        "top_n": top_n,
        "sector_cap": sector_cap if sector_cap is not None else "None",
        "months_tested": len(strategy_series),
        "strategy_final_value": float(strategy_equity.iloc[-1]),
        "benchmark_final_value": float(benchmark_equity.iloc[-1]),
        "strategy_cagr": cagr(strategy_equity),
        "benchmark_cagr": cagr(benchmark_equity),
        "strategy_sharpe": sharpe_from_returns(strategy_series),
        "benchmark_sharpe": sharpe_from_returns(benchmark_aligned),
        "strategy_volatility": annual_vol_from_returns(strategy_series),
        "benchmark_volatility": annual_vol_from_returns(benchmark_aligned),
        "strategy_max_drawdown": max_drawdown(strategy_equity),
        "benchmark_max_drawdown": max_drawdown(benchmark_equity),
        "average_turnover": float(returns_df["turnover"].mean()),
        "alpha_hit_rate": alpha_hit_rate,
        "positive_year_rate": positive_year_rate,
        "average_alpha": float(yearly["alpha"].mean()),
        "latest_holdings": latest_holdings,
    }

    equity_df = pd.DataFrame({
        "date": strategy_equity.index,
        "strategy": strategy_name,
        "strategy_equity": strategy_equity.values,
        "benchmark_equity": benchmark_equity.values,
    })

    return summary, returns_df.reset_index(), holdings_df, yearly, equity_df


def add_research_scores(summary_df: pd.DataFrame) -> pd.DataFrame:
    scored = summary_df.copy()

    scored["rank_cagr"] = scored["strategy_cagr"].rank(ascending=False, method="min")
    scored["rank_sharpe"] = scored["strategy_sharpe"].rank(ascending=False, method="min")
    scored["rank_drawdown"] = scored["strategy_max_drawdown"].rank(ascending=False, method="min")
    scored["rank_alpha_hit"] = scored["alpha_hit_rate"].rank(ascending=False, method="min")
    scored["rank_turnover"] = scored["average_turnover"].rank(ascending=True, method="min")

    scored["universe_credibility_score"] = scored["strategy"].map({
        "small_top10": 2,
        "broad_top20": 5,
        "sector_capped_top20": 4,
    })

    scored["simplicity_score"] = scored["strategy"].map({
        "small_top10": 4,
        "broad_top20": 5,
        "sector_capped_top20": 3,
    })

    scored["research_score"] = (
        (6 - scored["rank_cagr"]) * 0.20
        + (6 - scored["rank_sharpe"]) * 0.25
        + (6 - scored["rank_drawdown"]) * 0.15
        + (6 - scored["rank_alpha_hit"]) * 0.15
        + (6 - scored["rank_turnover"]) * 0.10
        + scored["universe_credibility_score"] * 0.10
        + scored["simplicity_score"] * 0.05
    )

    return scored.sort_values("research_score", ascending=False)


def main():
    print("Downloading data for V9 final comparison...")

    all_tickers = sorted(set(SMALL_UNIVERSE + BROAD_UNIVERSE + [BENCHMARK]))
    data = yf.download(all_tickers, start=START, end=END, auto_adjust=True)["Close"]

    small_prices = data[SMALL_UNIVERSE]
    broad_prices = data[BROAD_UNIVERSE]
    benchmark = data[BENCHMARK].dropna()

    small_dq = data_quality_report(small_prices)
    broad_dq = data_quality_report(broad_prices)

    small_usable = small_dq[small_dq["usable"]]["ticker"].tolist()
    broad_usable = broad_dq[broad_dq["usable"]]["ticker"].tolist()

    print(f"\nSmall universe requested: {len(SMALL_UNIVERSE)}")
    print(f"Small universe usable: {len(small_usable)}")
    print(f"Small universe excluded: {len(SMALL_UNIVERSE) - len(small_usable)}")

    print(f"\nBroad universe requested: {len(BROAD_UNIVERSE)}")
    print(f"Broad universe usable: {len(broad_usable)}")
    print(f"Broad universe excluded: {len(BROAD_UNIVERSE) - len(broad_usable)}")

    broad_excluded = broad_dq[~broad_dq["usable"]]["ticker"].tolist()
    if broad_excluded:
        print(f"Broad excluded: {broad_excluded}")

    small_prices = small_prices[small_usable].dropna(how="all")
    broad_prices = broad_prices[broad_usable].dropna(how="all")

    benchmark_monthly = benchmark.resample("ME").last()
    benchmark_returns = benchmark_monthly.pct_change().dropna()

    small_monthly_prices = small_prices.resample("ME").last()
    small_monthly_returns = small_monthly_prices.pct_change()

    broad_monthly_prices = broad_prices.resample("ME").last()
    broad_monthly_returns = broad_monthly_prices.pct_change()

    candidates = [
        {
            "strategy_name": "small_top10",
            "prices": small_monthly_prices,
            "returns": small_monthly_returns,
            "top_n": 10,
            "sector_cap": None,
        },
        {
            "strategy_name": "broad_top20",
            "prices": broad_monthly_prices,
            "returns": broad_monthly_returns,
            "top_n": 20,
            "sector_cap": None,
        },
        {
            "strategy_name": "sector_capped_top20",
            "prices": broad_monthly_prices,
            "returns": broad_monthly_returns,
            "top_n": 20,
            "sector_cap": SECTOR_CAP,
        },
    ]

    summaries = []
    returns_all = []
    holdings_all = []
    yearly_all = []
    equity_all = []

    for candidate in candidates:
        summary, returns_df, holdings_df, yearly_df, equity_df = run_momentum_strategy(
            strategy_name=candidate["strategy_name"],
            monthly_prices=candidate["prices"],
            monthly_returns=candidate["returns"],
            benchmark_returns=benchmark_returns,
            top_n=candidate["top_n"],
            sector_cap=candidate["sector_cap"],
        )

        summaries.append(summary)
        returns_all.append(returns_df)
        holdings_all.append(holdings_df)

        yearly_df["strategy"] = candidate["strategy_name"]
        yearly_all.append(yearly_df)

        equity_all.append(equity_df)

    summary_df = pd.DataFrame(summaries)
    scored_df = add_research_scores(summary_df)

    returns_out = pd.concat(returns_all, ignore_index=True)
    holdings_out = pd.concat(holdings_all, ignore_index=True)
    yearly_out = pd.concat(yearly_all, ignore_index=True)
    equity_out = pd.concat(equity_all, ignore_index=True)

    small_dq.to_csv(OUTPUT_DIR / "momentum_v9_small_universe_data_quality.csv", index=False)
    broad_dq.to_csv(OUTPUT_DIR / "momentum_v9_broad_universe_data_quality.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "momentum_v9_raw_summary.csv", index=False)
    scored_df.to_csv(OUTPUT_DIR / "momentum_v9_scored_summary.csv", index=False)
    returns_out.to_csv(OUTPUT_DIR / "momentum_v9_monthly_returns.csv", index=False)
    holdings_out.to_csv(OUTPUT_DIR / "momentum_v9_holdings.csv", index=False)
    yearly_out.to_csv(OUTPUT_DIR / "momentum_v9_calendar_year_returns.csv", index=False)
    equity_out.to_csv(OUTPUT_DIR / "momentum_v9_equity_curves.csv", index=False)

    print("\nMomentum Final Comparison V9")
    print("-" * 28)

    display_cols = [
        "strategy",
        "top_n",
        "sector_cap",
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
        "research_score",
    ]

    print(scored_df[display_cols].to_string(index=False))

    winner = scored_df.iloc[0]

    print("\nFinal Pilot Winner")
    print("-" * 18)
    print(f"Winner: {winner['strategy']}")
    print(f"Top N: {int(winner['top_n'])}")
    print(f"Sector cap: {winner['sector_cap']}")
    print(f"Final value: ₹{winner['strategy_final_value']:,.2f}")
    print(f"CAGR: {winner['strategy_cagr']:.2%}")
    print(f"Sharpe: {winner['strategy_sharpe']:.2f}")
    print(f"Max drawdown: {winner['strategy_max_drawdown']:.2%}")
    print(f"Average turnover: {winner['average_turnover']:.2%}")
    print(f"Alpha hit rate: {winner['alpha_hit_rate']:.2%}")
    print(f"Average alpha: {winner['average_alpha']:.2%}")
    print(f"Research score: {winner['research_score']:.2f}")

    print("\nWinner latest holdings")
    print("-" * 22)
    print(winner["latest_holdings"])

    print("\nInterpretation")
    print("-" * 14)
    print("V9 ranks candidates using return, Sharpe, drawdown, alpha consistency, turnover, universe credibility, and simplicity.")
    print("The research-score winner is not necessarily the highest-CAGR strategy; it is the most balanced pilot candidate.")

    print("\nSaved files")
    print("-" * 11)
    print("outputs/momentum_v9_small_universe_data_quality.csv")
    print("outputs/momentum_v9_broad_universe_data_quality.csv")
    print("outputs/momentum_v9_raw_summary.csv")
    print("outputs/momentum_v9_scored_summary.csv")
    print("outputs/momentum_v9_monthly_returns.csv")
    print("outputs/momentum_v9_holdings.csv")
    print("outputs/momentum_v9_calendar_year_returns.csv")
    print("outputs/momentum_v9_equity_curves.csv")


if __name__ == "__main__":
    main()
