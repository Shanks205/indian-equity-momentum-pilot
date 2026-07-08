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
MARKET_FILTER_MA = 10
TOP_NS = [10, 15, 20]

COST = 0.002
MONTHLY_CASH_RETURN = 0.0

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
    if not previous_holdings and current_holdings:
        return 1.0
    if previous_holdings and not current_holdings:
        return 1.0
    if not previous_holdings and not current_holdings:
        return 0.0

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


def run_strategy(monthly_prices, monthly_returns, bench_monthly, market_filter, top_n):
    momentum = monthly_prices.pct_change(LOOKBACK).shift(1)

    rows = []
    holdings_rows = []
    previous_holdings = set()

    for date in monthly_returns.index:
        risk_on = bool(market_filter.loc[date]) if date in market_filter.index else False

        if not risk_on:
            selected = []
            selected_set = set()
            gross_return = MONTHLY_CASH_RETURN
            turnover = calculate_turnover(previous_holdings, selected_set, top_n)
            transaction_cost = turnover * COST
            net_return = gross_return - transaction_cost

            rows.append({
                "date": date,
                "top_n": top_n,
                "risk_on": risk_on,
                "gross_return": gross_return,
                "turnover": turnover,
                "transaction_cost": transaction_cost,
                "net_return": net_return,
                "holdings_count": 0,
            })

            previous_holdings = selected_set
            continue

        scores = momentum.loc[date].dropna() if date in momentum.index else pd.Series(dtype=float)
        rets = monthly_returns.loc[date].dropna()

        common = scores.index.intersection(rets.index)
        scores = scores[common]
        rets = rets[common]

        if len(scores) < top_n:
            continue

        selected = list(scores.sort_values(ascending=False).head(top_n).index)
        selected_set = set(selected)

        gross_return = float(rets[selected].mean())
        turnover = calculate_turnover(previous_holdings, selected_set, top_n)
        transaction_cost = turnover * COST
        net_return = gross_return - transaction_cost

        rows.append({
            "date": date,
            "top_n": top_n,
            "risk_on": risk_on,
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

    risk_on_months = int(returns_df["risk_on"].sum())
    cash_months = int((~returns_df["risk_on"]).sum())

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
        "market_filter_ma_months": MARKET_FILTER_MA,
        "months_tested": len(equity),
        "risk_on_months": risk_on_months,
        "cash_months": cash_months,
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
    print("Downloading broader universe data for V4...")
    data = yf.download(TICKERS + [BENCHMARK], start=START, end=END, auto_adjust=True)["Close"]

    prices = data[TICKERS]
    benchmark = data[BENCHMARK].dropna()

    dq = data_quality_report(prices)
    usable_tickers = dq[dq["usable"]]["ticker"].tolist()

    print(f"\nUniverse requested: {len(TICKERS)}")
    print(f"Usable tickers: {len(usable_tickers)}")
    print(f"Excluded tickers: {len(TICKERS) - len(usable_tickers)}")

    prices = prices[usable_tickers].dropna(how="all")

    monthly_prices = prices.resample("ME").last()
    monthly_returns = monthly_prices.pct_change()

    benchmark_monthly_prices = benchmark.resample("ME").last()
    bench_monthly = benchmark_monthly_prices.pct_change().dropna()

    nifty_ma = benchmark_monthly_prices.rolling(MARKET_FILTER_MA).mean()
    market_filter = (benchmark_monthly_prices > nifty_ma).shift(1).fillna(False)

    summaries = []
    returns_all = []
    holdings_all = []
    equity_all = []

    for top_n in TOP_NS:
        summary, returns_df, holdings_df, equity_df = run_strategy(
            monthly_prices,
            monthly_returns,
            bench_monthly,
            market_filter,
            top_n,
        )

        summaries.append(summary)

        returns_df = returns_df.reset_index()
        returns_all.append(returns_df)

        if not holdings_df.empty:
            holdings_all.append(holdings_df)

        equity_df = equity_df.reset_index().rename(columns={"index": "date"})
        equity_df["top_n"] = top_n
        equity_all.append(equity_df)

    summary_df = pd.DataFrame(summaries)
    returns_out = pd.concat(returns_all, ignore_index=True)
    holdings_out = pd.concat(holdings_all, ignore_index=True) if holdings_all else pd.DataFrame()
    equity_out = pd.concat(equity_all, ignore_index=True)

    dq.to_csv(OUTPUT_DIR / "momentum_v4_data_quality.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "momentum_v4_summary.csv", index=False)
    returns_out.to_csv(OUTPUT_DIR / "momentum_v4_monthly_returns.csv", index=False)
    holdings_out.to_csv(OUTPUT_DIR / "momentum_v4_holdings.csv", index=False)
    equity_out.to_csv(OUTPUT_DIR / "momentum_v4_equity_curves.csv", index=False)

    print("\nMomentum Risk Filter V4 Summary")
    print("-" * 31)

    cols = [
        "top_n",
        "risk_on_months",
        "cash_months",
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

    print("\nBest V4 strategy by Sharpe")
    print("-" * 26)
    print(f"Top N: {int(best['top_n'])}")
    print(f"Lookback: {int(best['lookback_months'])} months")
    print(f"Nifty filter: above {int(best['market_filter_ma_months'])}-month MA")
    print(f"Final value: ₹{best['strategy_final_value']:,.2f}")
    print(f"CAGR: {best['strategy_cagr']:.2%}")
    print(f"Sharpe: {best['strategy_sharpe']:.2f}")
    print(f"Max drawdown: {best['strategy_max_drawdown']:.2%}")
    print(f"Average turnover: {best['average_turnover']:.2%}")
    print(f"Risk-on months: {int(best['risk_on_months'])}")
    print(f"Cash months: {int(best['cash_months'])}")
    print(f"Latest holdings: {best['latest_holdings']}")

    print("\nSaved files")
    print("-" * 11)
    print("outputs/momentum_v4_data_quality.csv")
    print("outputs/momentum_v4_summary.csv")
    print("outputs/momentum_v4_monthly_returns.csv")
    print("outputs/momentum_v4_holdings.csv")
    print("outputs/momentum_v4_equity_curves.csv")


if __name__ == "__main__":
    main()
