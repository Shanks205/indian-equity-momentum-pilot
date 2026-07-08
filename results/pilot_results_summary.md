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

## Current Best Pilot Candidate

Top-10 momentum with 12-month lookback had the best Sharpe in this pilot.

## Important Note

This pilot is not sufficient for live deployment. The next stage should test a broader universe, rolling walk-forward windows, sector constraints, turnover, slippage, and out-of-sample robustness.
