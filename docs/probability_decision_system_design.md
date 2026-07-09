# Probability Decision System Design

This document outlines a future decision-support system that combines quantitative signals, fundamentals, risk controls, and news interpretation into a probability-style research score.

> This is a research design only. It is not investment advice, not a trading bot, and not a buy/sell/hold recommendation system.

## Objective

Build a monthly stock research dashboard that estimates the probability of a stock outperforming the benchmark over a defined horizon.

Example output:

| Ticker | Probability Score | Suggested Research Label |
|---|---:|---|
| ABC.NS | 72% | Research Positive |
| XYZ.NS | 48% | Neutral / Watch |
| DEF.NS | 31% | Research Negative |

The score should support human review. It should not automatically trade.

## Core Principle

The probability number should not come from news alone.

It should combine multiple independent evidence blocks:

1. Price momentum
2. Quality fundamentals
3. Valuation
4. Earnings and growth
5. Risk and volatility
6. Liquidity
7. Sector and macro regime
8. News and event sentiment
9. Portfolio fit
10. Human override notes

## Suggested Score Architecture

| Component | Weight | Example Inputs |
|---|---:|---|
| Momentum | 20% | 6M and 12M price momentum, relative strength |
| Quality | 20% | ROE, ROCE, margins, debt control, cash flow quality |
| Valuation | 15% | PE, EV/EBITDA, price-to-book, DCF margin of safety |
| Earnings Trend | 15% | sales growth, profit growth, earnings revisions |
| Risk | 10% | volatility, drawdown, beta, downside risk |
| Liquidity | 5% | traded value, volume stability |
| Macro/Sector | 5% | interest rates, oil, currency, sector cycle |
| News/Event Score | 10% | earnings news, regulation, management change, litigation, order wins |

Total: 100%.

## Output Labels

The system should use research labels rather than direct trading commands.

| Probability | Label | Meaning |
|---:|---|---|
| 70%+ | Research Positive | Strong candidate for deeper review |
| 55%–70% | Watchlist Positive | Good but not decisive |
| 45%–55% | Neutral | No clear edge |
| 30%–45% | Caution | Weak or risky setup |
| Below 30% | Research Negative | Avoid unless thesis changes |

## News Handling Rules

News should be summarized and scored, not copied.

For subscription sources such as Mint or WSJ:

- Do not scrape paywalled articles automatically unless the source terms allow it.
- Do not store full article text in the repository.
- Store only short metadata, manual notes, source name, date, and your own summary.
- Prefer public links, official filings, exchange announcements, company releases, and regulatory documents for permanent evidence.

## Recommended Evidence Fields

For each news item:

- date
- source
- headline
- ticker or sector
- event type
- short user-written summary
- expected impact
- confidence level
- evidence link
- whether the source is official, primary, or media

## Event Type Examples

| Event Type | Example Impact |
|---|---|
| Earnings beat | Positive if supported by cash flow and guidance |
| Earnings miss | Negative if margins and growth weaken |
| Order win | Positive if material and executable |
| Regulation | Depends on sector impact |
| Promoter pledge increase | Usually negative risk flag |
| Debt reduction | Positive quality signal |
| Auditor resignation | Serious governance risk |
| Commodity cost increase | Negative for margin-sensitive sectors |
| Currency movement | Sector-specific impact |
| Interest-rate change | Affects banks, NBFCs, real estate, autos |

## Decision-Support Workflow

Monthly workflow:

1. Run quantitative screen.
2. Generate candidate list.
3. Pull company and sector news metadata manually or through compliant APIs.
4. Score news/event impact.
5. Combine quant score and event score.
6. Apply risk and liquidity filters.
7. Produce probability-style research score.
8. Human reviews final output.
9. Record decision in paper-trading log.

## Safety Rules

The system should never:

- place orders automatically,
- promise returns,
- call itself financial advice,
- use hidden paid content in public outputs,
- copy full subscription articles,
- ignore liquidity and risk,
- rely only on LLM sentiment.

## Best First Version

The first build should be simple:

1. Momentum score from current project.
2. Basic quality score from financial ratios.
3. Manual news/event score.
4. Final probability-style score.
5. Paper-trading log.

After the first version works, add automation gradually.

## Long-Term Vision

The long-term version can become a lightweight research terminal:

- stock screener,
- factor dashboard,
- news/event tracker,
- probability score,
- portfolio risk view,
- monthly research note generator,
- paper-trading performance tracker.

This would be similar in spirit to a small research terminal, but it should not be described as a Bloomberg Terminal replacement.
