# Jiraiya AI Trader

Jiraiya AI Trader is presented as an automated options-trading system for NSE F&O markets, with a focus on NIFTY, BankNifty, and FinNifty trading workflows.

This repository currently contains a static HTML investor/product presentation for the project:

```text
index.html
```

The presentation describes the intended trading system, risk controls, paper-trading validation, architecture, setup flow, and launch-readiness checklist.

> Important: Trading involves financial risk. This repository is not financial advice, investment advice, or a guarantee of profit. Use paper trading and independent review before considering any live deployment.

## Project Summary

Jiraiya AI Trader is positioned as a Python-based automated options-trading bot that integrates with the DHAN broker API for market data, order placement, trade tracking, and position management.

The presentation highlights:

- Automated NSE F&O options trading workflows
- DHAN API integration
- Multi-profile account support
- Paper trading and live trading modes
- Position-level risk controls
- Daily loss and profit limits
- Trailing stop-loss logic
- Trade persistence and crash recovery
- Dashboard-based monitoring
- Pre-production validation checklist

## Current Repository Contents

At the moment, this repository is a static presentation site.

```text
.
+-- index.html
`-- README.md
```

The actual Python bot source files referenced inside the presentation, such as runtime scripts, configuration files, validation scripts, and launch checklists, are not included in this repository at this time.

## How To View Locally

Clone the repository:

```bash
git clone https://github.com/Marketing-Studios/Jiraiya.git
cd Jiraiya
```

Open `index.html` directly in your browser.

On Windows PowerShell:

```powershell
Start-Process .\index.html
```

Or run a simple local web server:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Suggested GitHub Pages Deployment

Because this is currently a static HTML site, it can be hosted with GitHub Pages.

Recommended settings:

```text
Settings -> Pages -> Deploy from a branch
Branch: main
Folder: /root
```

After GitHub Pages is enabled, the site should be available at a URL similar to:

```text
https://marketing-studios.github.io/Jiraiya/
```

## System Described In The Presentation

The included presentation describes a larger trading system with these planned or referenced components:

### Strategy Engine

- Multi-factor market analysis
- Signal confidence scoring
- Trend, momentum, volume, and volatility checks
- Strategy logic referred to in the presentation as "Val's Logic"

### Risk Management

- Daily profit target
- Daily maximum loss
- Position sizing limits
- Stop-loss controls
- Trailing stop-loss
- Manual override and broker-app backup

### Execution Layer

- DHAN API order placement
- Option-chain and strike selection
- Trade entry and exit automation
- Paper order simulation
- Live order support after validation

### Recovery And Monitoring

- Trade state persistence
- Crash recovery
- Backup history
- Real-time dashboard
- Notifications and profile switching

## Safety Notes

Before any live trading system is added to this repository, the following should be treated as mandatory:

- Never commit `.env` files or API tokens.
- Never commit broker credentials.
- Use paper trading first.
- Start with the smallest possible position size.
- Add automated tests for every risk-control rule.
- Keep manual broker access available during market hours.
- Verify order placement, exit logic, and crash recovery independently.

Recommended secret file pattern:

```text
.env
*.key
*.pem
credentials.json
```

These should be added to `.gitignore` before any runtime code is committed.

## Recommended Roadmap

The repository can become more useful by adding the actual runtime project files in stages:

1. Add Python source code in a `src/` folder.
2. Add a safe paper-trading mode.
3. Add example configuration files without secrets.
4. Add automated tests for strategy and risk logic.
5. Add a pre-production validation script.
6. Add documentation for DHAN API setup.
7. Add screenshots of the dashboard.
8. Add deployment and launch-day checklists.

Suggested future structure:

```text
Jiraiya/
+-- README.md
+-- index.html
+-- .gitignore
+-- requirements.txt
+-- .env.example
+-- src/
|   +-- strategy/
|   +-- broker/
|   +-- risk/
|   +-- dashboard/
|   `-- storage/
+-- tests/
`-- docs/
```

## Disclaimer

This project is for educational, research, and product-presentation purposes unless and until audited live-trading code is included and independently validated.

Options trading is risky. Past performance, paper-trading results, or backtesting results do not guarantee future returns. Use this project responsibly and only with capital you can afford to lose.
