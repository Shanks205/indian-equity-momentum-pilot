# Indian Equity Momentum Pilot

A reproducible Indian equity momentum research pilot using public data, Python, yfinance, and LLM-assisted research workflows.

This project tests simple Indian large-cap equity strategies against the Nifty 50 benchmark (`^NSEI`) and documents both successful and failed experiments.

> Status: research pilot only. This is not investment advice, not a live trading system, and it does not place orders.

## Purpose

The goal is to build a disciplined and recruiter-friendly Indian equity research workflow:

1. Validate public NSE/yfinance data availability.
2. Compare strategies against a clear benchmark.
3. Reject weak strategies early.
4. Export reproducible results in CSV format.
5. Document limitations honestly.
6. Use LLM tools only for research assistance, interpretation, and reporting.

## Tools

- Python
- pandas
- numpy
- yfinance
- GitHub
- LLM-assisted research workflow for documentation and interpretation

## Project Structure

```text
indian-equity-momentum-pilot/
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   ├── methodology.md
│   ├── final_research_note.md
│   ├── project_limitations.md
│   └── next_stage_plan.md
├── results/
│   └── pilot_results_summary.md
└── scripts/
    ├── reliance_backtest.py
    ├── portfolio_backtest.py
    ├── momentum_compare.py
    ├── momentum_lookback_compare.py
    ├── momentum_research_v2.py
    ├── momentum_universe_v3.py
    ├── momentum_risk_filter_v4.py
    ├── momentum_vol_weight_v5.py
    ├── momentum_sector_cap_v6.py
    ├── momentum_walkforward_v7.py
    ├── momentum_cost_sensitivity_v8.py
    └── momentum_final_comparison_v9.py
```

## Strategies Tested

1. RELIANCE 20/50 SMA crossover.
2. RELIANCE 50/200 SMA crossover.
3. Equal-weight 3-stock portfolio.
4. 15-stock momentum Top-N strategy.
5. 50-stock broader-universe momentum strategy.
6. Nifty trend risk filter.
7. Inverse-volatility weighting.
8. Sector-capped momentum.
9. Calendar-year validation.
10. Transaction-cost sensitivity.
11. Final candidate comparison.

## Final Pilot Winner

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
| Research score | 4.65 |

Latest winner holdings from the final comparison run:

`BAJFINANCE.NS`, `MARUTI.NS`, `BHARTIARTL.NS`, `RELIANCE.NS`, `KOTAKBANK.NS`, `SBIN.NS`, `HDFCBANK.NS`, `AXISBANK.NS`, `LT.NS`, `ICICIBANK.NS`

## Final Candidate Comparison

| Strategy | Universe | CAGR | Sharpe | Max Drawdown | Avg Turnover | Alpha Hit Rate | Research Score |
|---|---|---:|---:|---:|---:|---:|---:|
| `small_top10` | 15 stocks | 16.58% | 1.29 | -11.45% | 11.28% | 100.00% | 4.65 |
| `broad_top20` | 50 stocks, 49 usable | 16.22% | 1.11 | -19.41% | 19.89% | 75.00% | 4.00 |
| `sector_capped_top20` | 50 stocks, 49 usable | 15.44% | 1.08 | -19.15% | 21.06% | 75.00% | 3.40 |

## Key Interpretation

The small-universe Top-10 strategy wins the pilot score because it has the best Sharpe, lowest drawdown, lowest turnover, and strongest alpha consistency.

The broader Top-20 strategy remains the best scalable next-stage candidate because it uses a wider universe and is more suitable for future Nifty 100 or Nifty 200 research.

Final positioning:

- Best pilot winner: `small_top10`
- Best scalable research candidate: `broad_top20`
- Governance variant: `sector_capped_top20`

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/momentum_final_comparison_v9.py
```

For the full experiment history, run the scripts in numerical order from V2 to V9.

## Output Files

Most scripts write CSV files to the `outputs/` directory, including:

- data quality reports,
- monthly returns,
- holdings,
- equity curves,
- calendar-year validation,
- cost-sensitivity results,
- final candidate scoring.

The `outputs/` directory is intentionally not committed to GitHub.

## Important Limitations

- Uses public yfinance data, not institutional data.
- Short sample period: 2021–2025.
- Manual/static universe selection.
- No full survivorship-bias control.
- Simplified transaction-cost assumptions.
- No complete slippage model.
- No liquidity constraint model.
- No tax impact.
- No forward paper-trading track record yet.

See `docs/project_limitations.md` for the full limitation log.

## Suggested Next Stage

The recommended next project is:

**Nifty 100 Momentum + Quality Research System**

This should add:

1. historical index membership,
2. stronger data quality controls,
3. momentum plus quality factors,
4. slippage and liquidity modeling,
5. out-of-sample paper trading,
6. optional Streamlit dashboard.

See `docs/next_stage_plan.md` for the full plan.

## Disclaimer

This repository is for educational and research purposes only. It is not financial advice, investment advice, or a recommendation to buy or sell securities.
