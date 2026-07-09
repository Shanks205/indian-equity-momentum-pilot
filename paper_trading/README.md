# Paper Trading Framework

This folder contains a safe, manual paper-trading framework for the Indian Equity Momentum Pilot.

The goal is to track the selected momentum portfolio forward in time without placing real trades.

> This is for research and education only. It is not investment advice and should not be treated as a buy/sell/hold recommendation system.

## Monthly Process

Run the final comparison or signal script after month-end data is available.

Recommended process:

1. Run the strategy script.
2. Record the selected stocks.
3. Record equal weights.
4. Record entry prices for the paper portfolio.
5. Track monthly returns.
6. Compare against Nifty 50.
7. Write notes on market conditions and major events.
8. Do not change the strategy rules during the paper-trading period.

## Files

| File | Purpose |
|---|---|
| `monthly_signal_log_template.csv` | Empty template for monthly paper-trading records |

## Important Rules

- No broker API connection.
- No automated order placement.
- No real-money execution from this folder.
- No changing rules after paper trading begins.
- Keep all notes factual and cautious.
- Compare results with Nifty 50 every month.

## Recommended Tracking Period

Minimum: 3 months.

Better: 6 to 12 months.

The goal is to collect forward evidence before even considering tiny manual real-money testing.
