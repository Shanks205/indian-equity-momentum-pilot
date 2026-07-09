# Project Limitations

This document records the main limitations of the Indian Equity Momentum Pilot. These limitations are important because the project is a research pilot, not a live trading system.

## 1. Data Source Limitations

The project uses public yfinance data. This is useful for rapid research but is not institutional-grade market data.

Potential issues include:

- missing symbols,
- stale ticker mappings,
- corporate action adjustments,
- benchmark alignment differences,
- occasional download failures,
- no official NSE constituent history.

In the broader universe tests, `TATAMOTORS.NS` failed the yfinance download and was excluded automatically.

## 2. Survivorship Bias

The universes are manually selected and do not fully reconstruct historical Nifty 50, Nifty 100, or Nifty 200 membership at each point in time.

This means the results may benefit from hindsight because the tested stock list contains companies known today, not necessarily the exact investable universe at each historical rebalance date.

## 3. Short Backtest Window

The main test window is 2021 to 2025. This covers multiple market regimes but is still short for a robust equity strategy conclusion.

The strategy should be tested across longer windows before any stronger claim is made.

## 4. Simplified Transaction Costs

Transaction costs are modeled as a percentage cost per unit of turnover.

This does not fully capture:

- bid-ask spread,
- market impact,
- brokerage differences,
- taxes,
- exchange fees,
- stamp duty,
- liquidity constraints,
- execution timing.

V8 tested transaction-cost sensitivity up to 1.00%, but this is still a simplified model.

## 5. No Slippage Model

The strategy assumes trades are executed at monthly close-derived returns. It does not model slippage or implementation delay beyond the signal lag.

A future version should include realistic execution assumptions.

## 6. No Liquidity Constraint

The project does not yet include liquidity filters such as average daily turnover, market impact estimates, or minimum tradable value.

This matters especially if the strategy expands beyond liquid large-cap stocks.

## 7. No Tax Impact

The backtests do not model short-term capital gains tax, long-term capital gains tax, securities transaction tax, or other tax effects.

Tax treatment can materially affect realized investor returns.

## 8. No Risk-Free Rate Adjustment

Sharpe ratios are calculated using simple monthly returns without explicitly subtracting a time-varying risk-free rate.

This is acceptable for a pilot comparison, but a more formal report should include risk-free-rate-adjusted Sharpe.

## 9. No Out-of-Sample Paper Trading Yet

The project does not yet include forward paper trading. Backtests can overfit even when they look robust.

A future stage should freeze the strategy and track monthly forward performance without changing rules.

## 10. Research Interpretation Limit

The final pilot winner is not a live recommendation. The result only says that, within this specific public-data test setup, the Top-10 12-month momentum strategy on the 15-stock universe had the best pilot research score.

The broader Top-20 strategy remains the preferred scalable candidate for future research.
