# Next Stage Plan

This document defines the recommended next stage after the Indian Equity Momentum Pilot.

The pilot winner is `small_top10`, but the preferred scalable research candidate is `broad_top20`. The next stage should focus on making the broader design more credible, robust, and closer to institutional research standards.

## Stage 1: Data Quality Upgrade

Replace or supplement yfinance with a more reliable data workflow.

Tasks:

1. Validate ticker mappings.
2. Resolve failed symbols such as `TATAMOTORS.NS`.
3. Add corporate-action checks.
4. Store raw downloaded data in `data/raw/`.
5. Store cleaned data in `data/processed/`.
6. Create repeatable data-quality reports.

## Stage 2: Historical Universe Reconstruction

The most important improvement is reducing survivorship bias.

Tasks:

1. Collect historical Nifty 50, Nifty 100, or Nifty 200 constituent lists.
2. Rebuild the investable universe at each rebalance date.
3. Exclude stocks that were not in the universe at the relevant date.
4. Compare static-universe and historical-universe results.

## Stage 3: Larger Universe Research

Move beyond the pilot universes.

Candidate universes:

- Nifty 50,
- Nifty 100,
- Nifty 200,
- Nifty LargeMidcap 250.

The first next-stage target should be Nifty 100 because it is larger than the pilot but still manageable.

## Stage 4: Better Cost and Slippage Model

Improve implementation realism.

Tasks:

1. Add brokerage assumptions.
2. Add bid-ask spread assumptions.
3. Add slippage assumptions.
4. Add liquidity filters using average traded value.
5. Test monthly versus quarterly rebalancing.
6. Compare cost sensitivity across low, medium, and high turnover regimes.

## Stage 5: Factor Expansion

Momentum should be compared with and combined with other factors.

Potential factors:

- quality,
- valuation,
- low volatility,
- profitability,
- earnings growth,
- debt control,
- price momentum.

A useful next model would be:

`momentum + quality + low volatility`

This is more defensible than momentum alone.

## Stage 6: Portfolio Construction Upgrade

Test portfolio construction methods after data quality improves.

Methods:

1. Equal weight.
2. Sector-capped equal weight.
3. Inverse-volatility weight.
4. Risk-parity weight.
5. Minimum-variance portfolio.
6. Shrinkage covariance portfolio.

These methods should be compared against the equal-weight baseline rather than assumed superior.

## Stage 7: Forward Paper Trading

Freeze the final rules and track them going forward.

Rules:

1. No changing the signal after paper trading starts.
2. Publish monthly holdings.
3. Track simulated trades.
4. Compare against Nifty 50 and Nifty 100.
5. Record slippage assumptions.
6. Keep live trading disabled.

## Stage 8: Reporting Layer

Convert the project into a recruiter-ready research product.

Outputs:

- final research note,
- monthly factsheet,
- strategy tear sheet,
- drawdown table,
- year-by-year comparison,
- GitHub README polish,
- optional Streamlit dashboard.

## Recommended Next Project

The recommended next project is:

**Nifty 100 Momentum + Quality Research System**

Main research question:

> Does a momentum-plus-quality strategy outperform equal weight and Nifty 100 in a walk-forward Indian equity universe after costs and data-quality controls?

This would be a stronger, more academically credible continuation of the current pilot.
