# Jiraiya AI Trader

Jiraiya AI Trader is a trading research project for building, testing, and presenting automated NSE-market trading workflows.

## About

Jiraiya AI Trader is a backtesting and strategy-research workspace for experimenting with NSE trading ideas before any real-world deployment. It combines a Streamlit Strategy Lab, historical market-data connectors, configurable strategy rules, and a static product presentation.

The project is designed to help users compare strategy behavior across different symbols, timeframes, and data sources. It is intentionally focused on research and backtesting, not live order execution.

The repository currently includes:

- A static investor/product presentation in `index.html`
- A Streamlit Strategy Lab in `trading_web/`
- Historical-data support through Yahoo Finance, with optional Dhan and Kite data connectors
- A safe backtesting workflow for testing strategies before any live trading work

> Important: This project is not financial advice. Trading involves risk. Backtest results, paper-trading results, and presentation claims do not guarantee future profit.

## Current Status

This repo is currently a **research, presentation, and backtesting repo**.

It does **not** currently include a production live-order execution engine inside this GitHub repository. The Streamlit app is intentionally backtest-focused and does not place live orders.

## Repository Structure

```text
.
+-- index.html
+-- README.md
+-- requirements.txt
+-- .env.example
+-- trading_web/
|   +-- app.py
|   +-- assets/
|   |   +-- psy_bg.png
|   |   `-- styles.css
|   `-- components/
|       +-- broker_data.py
|       +-- chart.py
|       +-- data.py
|       +-- layout.py
|       `-- strategy.py
```

## What Each Part Does

### `index.html`

A static presentation page for the Jiraiya AI Trader concept. It describes the larger product vision, including:

- Automated NSE F&O trading workflows
- Dhan API integration concept
- Risk-management design
- Paper-trading validation
- Launch-readiness checklist
- System architecture overview

Open it directly in a browser or host it with GitHub Pages.

### `trading_web/`

A Streamlit Strategy Lab for researching and backtesting strategy rules.

It supports:

- Symbol input
- Yahoo Finance, Dhan, or Kite as data-source options
- Intraday and daily modes
- Candlestick charts
- Strategy-generated buy/sell markers
- Backtest metrics
- Trade table export as CSV

Included strategies:

- Moving Average Crossover
- RSI Reversion
- Breakout

## Run Locally

Clone the repo:

```bash
git clone https://github.com/Marketing-Studios/Jiraiya.git
cd Jiraiya
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Strategy Lab:

```bash
streamlit run trading_web/app.py
```

## Quick Windows Commands

PowerShell:

```powershell
Set-Location "D:\work\Jiraiya"
python -m pip install -r requirements.txt
streamlit run trading_web/app.py
```

## Default Data Source

The app works out of the box with Yahoo Finance.

Example symbols:

```text
RELIANCE.NS
TCS.NS
INFY.NS
```

Yahoo Finance is useful for quick research, but broker data should be used before serious paper-trading validation.

## Optional Broker Data Setup

Broker credentials are optional and should only be stored locally.

Create a local `.env` file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then fill the provider you want.

### Dhan

```text
DHAN_CLIENT_ID=your_client_id
DHAN_TOKEN=your_access_token
DHAN_SECURITY_ID=your_security_id
DHAN_EXCHANGE_SEGMENT=NSE_EQ
DHAN_INSTRUMENT_TYPE=EQUITY
```

### Kite / Zerodha

```text
KITE_API_KEY=your_api_key
KITE_ACCESS_TOKEN=your_access_token
KITE_EXCHANGE=NSE
```

Never commit `.env` or real credentials.

## Strategy Lab Workflow

1. Choose a data source.
2. Enter a symbol.
3. Select intraday or daily data.
4. Choose a strategy.
5. Tune strategy parameters.
6. Set capital, quantity, and brokerage.
7. Click **Run Backtest**.
8. Review chart markers, P&L, return, win rate, drawdown, and trades.

The app is designed for research first. A strategy should be tested across multiple symbols, periods, and market regimes before it is trusted.

## What This Repo Does Not Do Yet

The current Streamlit app does not:

- Place live orders
- Manage live broker positions
- Run automated live trading
- Guarantee profitable signals
- Store real account credentials
- Replace broker-side risk controls

Live order placement should only be added after tests, paper trading, risk limits, and manual override flows are complete.

## Safety Rules

Before any live-trading feature is added:

- Keep real credentials out of Git.
- Use `.env` locally and `.env.example` publicly.
- Use paper trading first.
- Add tests for every risk rule.
- Keep manual broker access ready.
- Start with the smallest possible size.
- Verify stop-loss, target, and exit behavior independently.
- Assume APIs, internet, and local machines can fail.

The `.gitignore` is configured to ignore common secret files such as:

```text
.env
*.key
*.pem
credentials.json
.streamlit/secrets.toml
```

## GitHub Pages

The static presentation can be hosted using GitHub Pages:

```text
Settings -> Pages -> Deploy from a branch
Branch: main
Folder: /root
```

Expected URL format:

```text
https://marketing-studios.github.io/Jiraiya/
```

## Roadmap

Planned improvements:

1. Add more strategy templates.
2. Add proper paper-trading state.
3. Add tests for all strategy calculations.
4. Add Dhan/Kite historical-data examples.
5. Add dashboard screenshots.
6. Add a trade journal.
7. Add portfolio-level backtesting.
8. Add risk-control simulation.
9. Add broker execution only after paper-trading validation is complete.

## Disclaimer And Liability

This project is for **education, research, historical-data analysis, backtesting, and product presentation only**.

It is **not** a live-trading system, not financial advice, not investment advice, and not a recommendation to buy, sell, hold, or trade any instrument.

Backtesting has serious limitations:

- Backtest results are not guaranteed.
- Backtest results are not 100% accurate.
- Historical performance does not guarantee future performance.
- Data may be delayed, incomplete, adjusted, missing, or incorrect.
- Broker data, Yahoo Finance data, Dhan data, Kite data, and local calculations can all contain errors.
- Strategy outputs, chart signals, P&L, win rate, drawdown, and trade tables are only research outputs.
- Slippage, brokerage, taxes, liquidity, spread, order rejection, latency, outages, and real market execution may differ from backtest assumptions.

Marketing Studios, the repository owner, and contributors are **not responsible** for:

- trading losses
- financial decisions
- incorrect backtest outputs
- inaccurate signals
- software bugs
- data-provider errors
- broker/API failures
- missed trades
- unexpected trades
- misuse of this project
- any direct or indirect damages caused by using this repository

Use this project at your own risk. Always verify results independently before making any financial decision. Options trading and leveraged trading can lead to significant losses, including loss of capital.
