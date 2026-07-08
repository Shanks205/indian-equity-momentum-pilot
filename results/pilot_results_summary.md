# Pilot Results Summary

## Tested Period

2021-01-01 to 2025-12-31, subject to available yfinance data and aligned benchmark windows.

## Data Validation

- `RELIANCE.NS`, `HDFCBANK.NS`, and `INFY.NS` were tested successfully.
- `^NSEI` was tested successfully as a Nifty 50 benchmark.
- OHLCV and adjusted price data were available in the tested workflow.

## Strategy Results

### RELIANCE 20/50 SMA Crossover

| Metric | Strategy | Buy & Hold |
|---|---:|---:|
| Final Value | ₹104,395.65 | ₹170,862.08 |
| CAGR | 0.87% | 11.32% |
| Annual Volatility | 15.33% | 22.73% |
| Sharpe | 0.13 | 0.59 |
| Max Drawdown | -34.28% | -27.18% |

Verdict: failed.

### RELIANCE 50/200 SMA Crossover

| Metric | Strategy | Buy & Hold |
|---|---:|---:|
| Final Value | ₹104,968.41 | ₹170,862.09 |
| CAGR | 0.98% | 11.32% |
| Annual Volatility | 17.83% | 22.73% |
| Sharpe | 0.14 | 0.59 |
| Max Drawdown | -25.20% | -27.18% |

Verdict: failed.

### 3-Stock Equal-Weight Portfolio

Tickers: `RELIANCE.NS`, `HDFCBANK.NS`, `INFY.NS`

| Metric | Portfolio | Nifty 50 |
|---|---:|---:|
| Final Value | ₹150,493.30 | ₹190,242.84 |
| CAGR | 7.09% | 12.73% |
| Annual Volatility | 13.67% | 12.32% |
| Sharpe | 0.57 | 1.04 |
| Max Drawdown | -13.17% | -14.28% |

Verdict: underperformed benchmark.

## Momentum Research V1

### Momentum Top-N Comparison

| Strategy | Final Value | CAGR | Volatility | Sharpe | Max Drawdown | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Top 3 Momentum | ₹125,625.06 | 3.72% | 13.94% | 0.33 | -25.71% | Failed |
| Top 5 Momentum | ₹158,567.62 | 9.61% | 11.86% | 0.83 | -11.43% | Close to benchmark |
| Top 10 Momentum | ₹178,699.74 | 12.37% | 11.40% | 1.08 | -9.39% | Best Top-N result |

Benchmark for aligned Top-N comparison:

- Nifty final value: ₹164,554.77
- Nifty CAGR: 10.04%
- Nifty Sharpe: 0.85

### Momentum Lookback Comparison — Top 10

| Lookback | Final Value | CAGR | Volatility | Sharpe | Max Drawdown | Nifty CAGR | Nifty Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3-month | ₹181,675.39 | 12.45% | 11.51% | 1.08 | -13.84% | 11.75% | 0.96 |
| 6-month | ₹178,699.76 | 12.37% | 11.40% | 1.08 | -9.39% | 10.04% | 0.85 |
| 9-month | ₹155,989.07 | 12.40% | 11.45% | 1.08 | -14.08% | 10.92% | 0.91 |
| 12-month | ₹159,756.85 | 14.11% | 11.29% | 1.23 | -12.23% | 11.99% | 0.98 |

## Momentum Research V2 — Turnover-Aware Exporting Script

The V2 script adds:

- monthly returns CSV output
- holdings CSV output
- equity curve CSV output
- summary CSV output
- turnover-aware transaction costs
- latest holdings export

### V2 Results

| Lookback | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Average Turnover |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 months | ₹198,212.72 | ₹177,285.72 | 14.61% | 11.75% | 1.25 | 0.96 | -13.13% | 21.43% |
| 6 months | ₹195,434.60 | ₹164,554.77 | 14.72% | 10.04% | 1.27 | 0.85 | -8.56% | 14.72% |
| 9 months | ₹170,284.63 | ₹146,782.27 | 14.84% | 10.92% | 1.27 | 0.91 | -13.33% | 11.40% |
| 12 months | ₹173,491.45 | ₹149,590.97 | 16.58% | 11.99% | 1.43 | 0.98 | -11.45% | 11.28% |

## Momentum Research V3 — Broader Universe Test

The V3 script expands the test from 15 tickers to a broader 50-stock Indian large-cap universe, adds a data-quality report, automatically excludes unusable tickers, and compares Top 10, Top 15, and Top 20 selections using 12-month momentum.

Data-quality result:

- Universe requested: 50 tickers
- Usable tickers: 49
- Excluded tickers: 1
- Excluded ticker in this run: `TATAMOTORS.NS` failed yfinance download

### V3 Results

| Top N | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Average Turnover |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | ₹181,750.06 | ₹149,590.97 | 16.43% | 11.99% | 1.02 | 0.98 | -25.04% | 25.32% |
| 15 | ₹181,012.97 | ₹149,590.97 | 16.67% | 11.99% | 1.09 | 0.98 | -21.69% | 20.43% |
| 20 | ₹177,415.87 | ₹149,590.97 | 16.22% | 11.99% | 1.13 | 0.98 | -19.41% | 19.89% |

## Momentum Research V4 — Nifty Trend Risk Filter

The V4 script adds a market-risk filter:

- invest only when Nifty is above its 10-month moving average
- otherwise hold cash
- apply the filter with a one-month lag to reduce look-ahead bias

Data-quality result:

- Universe requested: 50 tickers
- Usable tickers: 49
- Excluded tickers: 1
- Excluded ticker in this run: `TATAMOTORS.NS` failed yfinance download

### V4 Results

| Top N | Risk-On Months | Cash Months | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Average Turnover |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 37 | 20 | ₹172,266.49 | ₹190,242.84 | 11.70% | 12.73% | 0.95 | 1.04 | -15.91% | 28.07% |
| 15 | 37 | 20 | ₹166,705.44 | ₹190,242.84 | 10.96% | 12.73% | 0.99 | 1.04 | -12.88% | 25.85% |
| 20 | 37 | 20 | ₹161,448.30 | ₹190,242.84 | 10.24% | 12.73% | 1.00 | 1.04 | -12.05% | 25.70% |

V4 verdict: the Nifty trend filter reduced drawdown, but it also reduced CAGR and Sharpe too much. It is useful as a defensive experiment, but it is not the current best strategy.

## Momentum Research V5 — Volatility-Weighted Momentum

The V5 script compares equal-weight momentum against inverse-volatility weighted momentum across Top 10, Top 15, and Top 20 selections. It uses 12-month momentum and 6-month realized volatility for weighting.

Data-quality result:

- Universe requested: 50 tickers
- Usable tickers: 49
- Excluded tickers: 1
- Excluded ticker in this run: `TATAMOTORS.NS` failed yfinance download

### V5 Results

| Top N | Weighting | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Average Turnover |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | Equal weight | ₹181,929.40 | ₹149,590.97 | 16.43% | 11.99% | 1.02 | 0.98 | -25.04% | 24.26% |
| 10 | Inverse volatility | ₹178,256.39 | ₹149,590.97 | 15.89% | 11.99% | 1.02 | 0.98 | -22.95% | 32.37% |
| 15 | Equal weight | ₹181,193.67 | ₹149,590.97 | 16.67% | 11.99% | 1.09 | 0.98 | -21.69% | 19.36% |
| 15 | Inverse volatility | ₹176,343.60 | ₹149,590.97 | 15.92% | 11.99% | 1.08 | 0.98 | -19.27% | 26.49% |
| 20 | Equal weight | ₹177,593.94 | ₹149,590.97 | 16.22% | 11.99% | 1.13 | 0.98 | -19.41% | 18.83% |
| 20 | Inverse volatility | ₹169,468.21 | ₹149,590.97 | 15.19% | 11.99% | 1.07 | 0.98 | -17.73% | 26.08% |

V5 verdict: inverse-volatility weighting reduced drawdown modestly, but it also reduced CAGR and Sharpe while increasing turnover. Equal weight remains better in this test.

## Current Best Pilot Candidate

There are still two main candidates:

1. **V2 Top-10 12-month momentum** — strongest Sharpe and much lower drawdown in the smaller 15-stock universe.
2. **V3/V5 Top-20 equal-weight 12-month momentum** — best broader-universe candidate, but with higher drawdown.

V4 and V5 inverse-volatility weighting are not main candidates. They are documented experiments that improved one risk metric but weakened the overall profile.

## Important Note

This pilot is not sufficient for live deployment. The next stage should test rolling walk-forward windows, sector constraints, proper Nifty membership history, slippage, turnover sensitivity, and out-of-sample robustness.
