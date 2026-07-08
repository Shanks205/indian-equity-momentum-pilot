# Methodology

## Scope

This pilot studies Indian large-cap equity strategies using publicly available price data from yfinance.

The pilot compares simple single-stock timing rules, equal-weight portfolios, and momentum-ranked portfolios against the Nifty 50 benchmark.

## Data

- Source: yfinance
- Equity tickers: NSE tickers with `.NS` suffix
- Benchmark: `^NSEI`
- Frequency: daily data resampled to month-end for portfolio strategies
- Price field: adjusted prices via `auto_adjust=True`

## Benchmark

The benchmark is the Nifty 50 index represented by `^NSEI` from yfinance.

## Transaction Costs

The current scripts assume a simplified transaction cost of 0.20% per trade or rebalance.

This is only a pilot assumption. A production-grade model should include:

- brokerage
- STT
- exchange charges
- GST
- stamp duty
- bid-ask spread
- slippage
- liquidity limits

## Bias Controls Used

The momentum scripts shift the ranking signal by one month before portfolio formation. This reduces look-ahead bias.

## Bias Controls Not Yet Solved

- Survivorship bias
- Constituency changes in Nifty 50/Nifty 100
- Corporate action audit beyond yfinance adjustment
- Delisting effects
- Liquidity filtering
- Tax-aware return calculation

## Strategy Definitions

### SMA Crossover

The strategy holds the stock when the short moving average is above the long moving average and exits otherwise.

Tested variants:

- 20-day / 50-day SMA
- 50-day / 200-day SMA

### Equal-Weight Portfolio

The portfolio holds selected tickers at equal weights and rebalances monthly.

### Momentum Portfolio

At each month-end:

1. Compute historical momentum over a selected lookback window.
2. Shift signal by one month.
3. Rank stocks by momentum.
4. Select Top N stocks.
5. Equal-weight selected stocks.
6. Apply approximate rebalance cost.
7. Compare against Nifty 50.

## Current Interpretation

The pilot suggests that very simple single-stock timing is weak, while diversified large-cap momentum is more promising.

The best observed pilot variant was Top-10, 12-month momentum. This result requires further validation before any practical use.

## Research Integrity Rules

- Do not claim live-trading readiness.
- Do not present pilot results as investment recommendations.
- Report failed strategies as clearly as successful ones.
- Keep benchmark comparisons visible.
- Prefer reproducible Python calculations over LLM-generated final metrics.
