# Final Research Note

## Indian Equity Momentum Pilot

This pilot evaluates whether simple momentum rules can produce a credible, reproducible benchmark-aware Indian equity strategy using public data only.

The project uses Python, pandas, numpy, yfinance, and manually defined Indian large-cap universes. The benchmark is the Nifty 50 proxy ticker `^NSEI` from yfinance.

> This is a research project only. It is not investment advice, not a live trading system, and not a recommendation to buy or sell securities.

## Research Question

Can a simple monthly momentum strategy on Indian large-cap stocks outperform the Nifty 50 benchmark after transaction costs, and does the result remain stable across calendar years?

## Data and Period

- Test window: 2021-01-01 to 2025-12-31, subject to available yfinance data.
- Benchmark: `^NSEI`.
- Price field: adjusted close through `auto_adjust=True` in yfinance.
- Rebalance frequency: monthly.
- Signal: 12-month price momentum with a one-month lag to reduce look-ahead bias.
- Transaction cost assumption in core tests: 0.20% per unit of turnover.

## Strategies Tested

The project tested several versions:

1. RELIANCE 20/50 SMA crossover.
2. RELIANCE 50/200 SMA crossover.
3. Equal-weight 3-stock portfolio.
4. 15-stock momentum Top-N tests.
5. Broader 50-stock momentum tests.
6. Nifty trend filter.
7. Inverse-volatility weighting.
8. Sector-capped momentum.
9. Calendar-year validation.
10. Transaction-cost sensitivity.
11. Final candidate comparison.

## Main Result

The final pilot winner is:

**Top-10 equal-weight 12-month momentum on the 15-stock universe (`small_top10`).**

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

Latest winner holdings from the final comparison run:

`BAJFINANCE.NS`, `MARUTI.NS`, `BHARTIARTL.NS`, `RELIANCE.NS`, `KOTAKBANK.NS`, `SBIN.NS`, `HDFCBANK.NS`, `AXISBANK.NS`, `LT.NS`, `ICICIBANK.NS`

## Final Candidate Comparison

| Strategy | Universe | CAGR | Sharpe | Max Drawdown | Turnover | Alpha Hit Rate | Research Score |
|---|---|---:|---:|---:|---:|---:|---:|
| `small_top10` | 15 stocks | 16.58% | 1.29 | -11.45% | 11.28% | 100.00% | 4.65 |
| `broad_top20` | 50 stocks, 49 usable | 16.22% | 1.11 | -19.41% | 19.89% | 75.00% | 4.00 |
| `sector_capped_top20` | 50 stocks, 49 usable | 15.44% | 1.08 | -19.15% | 21.06% | 75.00% | 3.40 |

## Interpretation

The small-universe Top-10 strategy wins the pilot because it has the strongest risk-adjusted profile: better Sharpe, lower drawdown, lower turnover, and stronger calendar-year alpha consistency.

The broader Top-20 strategy remains important because it is more scalable and closer to a future Nifty 100 or Nifty 200 research design. It is not the final pilot winner, but it is the best next-stage candidate.

The sector-capped version improves governance and portfolio balance but did not improve the overall return/risk profile in this sample.

## Validation Findings

The broader Top-20 candidate passed two important robustness checks:

- Calendar-year validation: positive strategy return in all four tested calendar years and positive alpha in 3 out of 4 years.
- Transaction-cost sensitivity: still beat the benchmark on CAGR and Sharpe up to the highest tested cost level of 1.00% per unit of turnover.

These checks support continued research, but they do not remove survivorship bias, data limitations, or the need for out-of-sample testing.

## Conclusion

The final pilot winner is `small_top10`, while `broad_top20` is the preferred scalable candidate for the next research stage.

The project is now suitable as a recruiter-facing research pilot because it includes rejected strategies, validation tests, cost sensitivity, documented limitations, and a clear final interpretation.
