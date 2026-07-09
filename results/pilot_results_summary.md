# Pilot Results Summary

## Tested Period

2021-01-01 to 2025-12-31, subject to available yfinance data and aligned benchmark windows.

## Data Validation

- `RELIANCE.NS`, `HDFCBANK.NS`, and `INFY.NS` were tested successfully.
- `^NSEI` was tested successfully as a Nifty 50 benchmark.
- OHLCV and adjusted price data were available in the tested workflow.
- In the broader 50-stock universe tests, `TATAMOTORS.NS` failed yfinance download and was excluded automatically.

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

### Momentum Lookback Comparison — Top 10

| Lookback | Final Value | CAGR | Volatility | Sharpe | Max Drawdown | Nifty CAGR | Nifty Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3-month | ₹181,675.39 | 12.45% | 11.51% | 1.08 | -13.84% | 11.75% | 0.96 |
| 6-month | ₹178,699.76 | 12.37% | 11.40% | 1.08 | -9.39% | 10.04% | 0.85 |
| 9-month | ₹155,989.07 | 12.40% | 11.45% | 1.08 | -14.08% | 10.92% | 0.91 |
| 12-month | ₹159,756.85 | 14.11% | 11.29% | 1.23 | -12.23% | 11.99% | 0.98 |

## Momentum Research V2 — Turnover-Aware Exporting Script

The V2 script adds monthly returns, holdings, equity curves, summary CSV output, turnover-aware transaction costs, and latest holdings export.

### V2 Results

| Lookback | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Average Turnover |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 months | ₹198,212.72 | ₹177,285.72 | 14.61% | 11.75% | 1.25 | 0.96 | -13.13% | 21.43% |
| 6 months | ₹195,434.60 | ₹164,554.77 | 14.72% | 10.04% | 1.27 | 0.85 | -8.56% | 14.72% |
| 9 months | ₹170,284.63 | ₹146,782.27 | 14.84% | 10.92% | 1.27 | 0.91 | -13.33% | 11.40% |
| 12 months | ₹173,491.45 | ₹149,590.97 | 16.58% | 11.99% | 1.43 | 0.98 | -11.45% | 11.28% |

## Momentum Research V3 — Broader Universe Test

The V3 script expands the test from 15 tickers to a broader 50-stock Indian large-cap universe, adds a data-quality report, automatically excludes unusable tickers, and compares Top 10, Top 15, and Top 20 selections using 12-month momentum.

### V3 Results

| Top N | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Average Turnover |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | ₹181,750.06 | ₹149,590.97 | 16.43% | 11.99% | 1.02 | 0.98 | -25.04% | 25.32% |
| 15 | ₹181,012.97 | ₹149,590.97 | 16.67% | 11.99% | 1.09 | 0.98 | -21.69% | 20.43% |
| 20 | ₹177,415.87 | ₹149,590.97 | 16.22% | 11.99% | 1.13 | 0.98 | -19.41% | 19.89% |

## Momentum Research V4 — Nifty Trend Risk Filter

The V4 script invests only when Nifty is above its 10-month moving average; otherwise it holds cash. The filter is lagged by one month to reduce look-ahead bias.

### V4 Results

| Top N | Risk-On Months | Cash Months | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Average Turnover |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 37 | 20 | ₹172,266.49 | ₹190,242.84 | 11.70% | 12.73% | 0.95 | 1.04 | -15.91% | 28.07% |
| 15 | 37 | 20 | ₹166,705.44 | ₹190,242.84 | 10.96% | 12.73% | 0.99 | 1.04 | -12.88% | 25.85% |
| 20 | 37 | 20 | ₹161,448.30 | ₹190,242.84 | 10.24% | 12.73% | 1.00 | 1.04 | -12.05% | 25.70% |

V4 verdict: the Nifty trend filter reduced drawdown, but it also reduced CAGR and Sharpe too much. It is useful as a defensive experiment, but it is not the current best strategy.

## Momentum Research V5 — Volatility-Weighted Momentum

The V5 script compares equal-weight momentum against inverse-volatility weighted momentum across Top 10, Top 15, and Top 20 selections. It uses 12-month momentum and 6-month realized volatility for weighting.

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

## Momentum Research V6 — Sector-Capped Momentum

The V6 script applies a sector cap to Top-20 12-month momentum. It tests caps of 3, 4, and 5 stocks per sector, equal-weights the selected portfolio, and exports sector exposure.

### V6 Results

| Sector Cap | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Average Turnover |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | ₹172,881.37 | ₹149,590.97 | 15.18% | 11.99% | 1.06 | 0.98 | -20.68% | 19.57% |
| 4 | ₹174,022.97 | ₹149,590.97 | 15.44% | 11.99% | 1.09 | 0.98 | -19.15% | 21.06% |
| 5 | ₹173,034.17 | ₹149,590.97 | 15.46% | 11.99% | 1.08 | 0.98 | -19.41% | 20.96% |

V6 verdict: sector caps improved portfolio balance and slightly reduced drawdown at the 4-stock cap, but CAGR and Sharpe fell versus the uncapped Top-20 equal-weight momentum result. Sector caps are useful for risk governance, but they are not yet a better main strategy in this sample.

## Momentum Research V7 — Walk-Forward Calendar-Year Validation

The V7 script validates the current broader-universe Top-20 12-month momentum candidate year by year. It checks calendar-year returns, alpha versus Nifty, yearly Sharpe, drawdown, and consistency.

### V7 Summary

| Metric | Result |
|---|---:|
| Strategy final value | ₹177,415.88 |
| Benchmark final value | ₹149,590.97 |
| Strategy CAGR | 16.22% |
| Benchmark CAGR | 11.99% |
| Strategy Sharpe | 1.11 |
| Benchmark Sharpe | 0.89 |
| Strategy max drawdown | -19.41% |
| Average turnover | 19.89% |
| Alpha hit rate | 75.00% |
| Average alpha | 4.97% |

### Calendar-Year Validation

| Year | Months | Strategy Return | Benchmark Return | Alpha | Strategy Sharpe | Benchmark Sharpe | Strategy Max Drawdown |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 11 | 7.91% | 4.41% | 3.49% | 0.58 | 0.36 | -12.02% |
| 2023 | 12 | 29.42% | 20.03% | 9.40% | 1.69 | 1.56 | -5.61% |
| 2024 | 12 | 15.80% | 8.80% | 7.00% | 1.18 | 0.83 | -11.88% |
| 2025 | 12 | 9.70% | 9.70% | -0.00% | 0.83 | 0.84 | -5.85% |

V7 verdict: this is a positive validation result. The strategy produced positive returns in all four tested calendar years and beat Nifty in three out of four years. The alpha hit rate of 75% supports further testing, though the sample remains short and not survivorship-bias-free.

## Momentum Research V8 — Transaction-Cost Sensitivity

The V8 script tests the current Top-20 equal-weight 12-month momentum candidate across multiple transaction-cost assumptions. Costs are applied per unit of monthly turnover.

### V8 Results

| Cost | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Avg Turnover | Beats CAGR | Beats Sharpe |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0.00% | ₹180,743.19 | ₹149,590.97 | 16.72% | 11.99% | 1.14 | 0.89 | -19.24% | 19.89% | Yes | Yes |
| 0.10% | ₹179,072.05 | ₹149,590.97 | 16.47% | 11.99% | 1.13 | 0.89 | -19.33% | 19.89% | Yes | Yes |
| 0.20% | ₹177,415.88 | ₹149,590.97 | 16.22% | 11.99% | 1.11 | 0.89 | -19.41% | 19.89% | Yes | Yes |
| 0.30% | ₹175,774.55 | ₹149,590.97 | 15.97% | 11.99% | 1.09 | 0.89 | -19.49% | 19.89% | Yes | Yes |
| 0.50% | ₹172,535.90 | ₹149,590.97 | 15.47% | 11.99% | 1.06 | 0.89 | -19.66% | 19.89% | Yes | Yes |
| 1.00% | ₹164,690.09 | ₹149,590.97 | 14.23% | 11.99% | 0.97 | 0.89 | -20.08% | 19.89% | Yes | Yes |

V8 verdict: this is a strong robustness result. The strategy still beats the benchmark on both CAGR and Sharpe at every tested cost level, including the highest tested cost of 1.00%. Performance weakens as costs rise, but the edge does not disappear in this cost-sensitivity test.

## Momentum Research V9 — Final Candidate Comparison

The V9 script compares three final candidates:

1. `small_top10` — 15-stock small-universe Top-10 12-month momentum
2. `broad_top20` — 50-stock broader-universe Top-20 12-month momentum
3. `sector_capped_top20` — broader-universe Top-20 12-month momentum with a 4-stock sector cap

The final score combines CAGR, Sharpe, drawdown, alpha hit rate, turnover, universe credibility, and simplicity.

### V9 Results

| Strategy | Top N | Sector Cap | Strategy Final Value | Benchmark Final Value | Strategy CAGR | Benchmark CAGR | Strategy Sharpe | Benchmark Sharpe | Max Drawdown | Avg Turnover | Alpha Hit Rate | Avg Alpha | Research Score |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| small_top10 | 10 | None | ₹173,491.44 | ₹149,590.97 | 16.58% | 11.99% | 1.29 | 0.89 | -11.45% | 11.28% | 100.00% | 4.14% | 4.65 |
| broad_top20 | 20 | None | ₹177,415.87 | ₹149,590.97 | 16.22% | 11.99% | 1.11 | 0.89 | -19.41% | 19.89% | 75.00% | 4.97% | 4.00 |
| sector_capped_top20 | 20 | 4 | ₹174,022.95 | ₹149,590.97 | 15.44% | 11.99% | 1.08 | 0.89 | -19.15% | 21.06% | 75.00% | 4.39% | 3.40 |

### V9 Winner

The V9 research-score winner is:

**`small_top10` — Top-10 12-month momentum on the 15-stock universe**

| Metric | Result |
|---|---:|
| Final value | ₹173,491.44 |
| CAGR | 16.58% |
| Sharpe | 1.29 |
| Max drawdown | -11.45% |
| Average turnover | 11.28% |
| Alpha hit rate | 100.00% |
| Average alpha | 4.14% |
| Research score | 4.65 |

Latest winner holdings:

`BAJFINANCE.NS`, `MARUTI.NS`, `BHARTIARTL.NS`, `RELIANCE.NS`, `KOTAKBANK.NS`, `SBIN.NS`, `HDFCBANK.NS`, `AXISBANK.NS`, `LT.NS`, `ICICIBANK.NS`

### V9 Interpretation

The small-universe Top-10 strategy wins the final pilot score because it has the best Sharpe, lowest drawdown, lowest turnover, and strongest alpha consistency. However, the broader-universe Top-20 strategy remains important because it has better universe credibility and is more scalable for future Nifty 100/Nifty 200-style research.

Final positioning:

- **Best pilot winner:** `small_top10`
- **Best scalable candidate:** `broad_top20`
- **Governance variant:** `sector_capped_top20`

## Final Pilot Candidate

The final pilot winner is:

**Top-10 equal-weight 12-month momentum on the 15-stock universe (`small_top10`)**

The broader Top-20 equal-weight 12-month momentum strategy remains the best scalable candidate for the next research stage.

## Important Note

This pilot is not sufficient for live deployment. The next stage should test proper Nifty membership history, survivorship bias, slippage, out-of-sample robustness, larger universe coverage, and stronger data quality controls.
