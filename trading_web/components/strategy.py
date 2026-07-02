from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    frame: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict


def build_signals(df: pd.DataFrame, strategy: str, params: dict) -> pd.DataFrame:
    out = df.copy()
    out["signal"] = 0
    out["strategy_note"] = ""
    close = out["Close"].astype(float)

    if strategy == "Moving Average Crossover":
        short_window = int(params.get("short_window", 9))
        long_window = int(params.get("long_window", 21))
        short_ma = close.rolling(short_window).mean()
        long_ma = close.rolling(long_window).mean()
        prev_short = short_ma.shift(1)
        prev_long = long_ma.shift(1)
        out["short_ma"] = short_ma
        out["long_ma"] = long_ma
        out.loc[(short_ma > long_ma) & (prev_short <= prev_long), "signal"] = 1
        out.loc[(short_ma < long_ma) & (prev_short >= prev_long), "signal"] = -1
        out["strategy_note"] = f"MA {short_window}/{long_window}"

    elif strategy == "RSI Reversion":
        period = int(params.get("rsi_period", 14))
        lower = float(params.get("rsi_lower", 30))
        upper = float(params.get("rsi_upper", 70))
        rsi = _rsi(close, period)
        out["rsi"] = rsi
        out.loc[(rsi > lower) & (rsi.shift(1) <= lower), "signal"] = 1
        out.loc[(rsi < upper) & (rsi.shift(1) >= upper), "signal"] = -1
        out["strategy_note"] = f"RSI {period} lower={lower:g} upper={upper:g}"

    elif strategy == "Breakout":
        lookback = int(params.get("breakout_lookback", 20))
        prior_high = out["High"].rolling(lookback).max().shift(1)
        prior_low = out["Low"].rolling(lookback).min().shift(1)
        out["breakout_high"] = prior_high
        out["breakout_low"] = prior_low
        out.loc[close > prior_high, "signal"] = 1
        out.loc[close < prior_low, "signal"] = -1
        out["strategy_note"] = f"Breakout {lookback}"

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return out


def run_backtest(
    df: pd.DataFrame,
    strategy: str,
    params: dict,
    capital: float,
    quantity: int,
    brokerage_per_trade: float,
) -> BacktestResult:
    signals = build_signals(df, strategy, params)
    trades = []
    in_position = False
    entry_time = None
    entry_price = 0.0
    qty = max(1, int(quantity or 1))
    brokerage = max(0.0, float(brokerage_per_trade or 0.0))

    for ts, row in signals.iterrows():
        sig = int(row.get("signal", 0))
        close = float(row["Close"])
        if sig == 1 and not in_position:
            in_position = True
            entry_time = ts
            entry_price = close
        elif sig == -1 and in_position:
            gross = (close - entry_price) * qty
            costs = brokerage * 2
            pnl = gross - costs
            trades.append(
                {
                    "entry_time": entry_time,
                    "exit_time": ts,
                    "entry_price": entry_price,
                    "exit_price": close,
                    "quantity": qty,
                    "gross_pnl": gross,
                    "costs": costs,
                    "pnl": pnl,
                    "return_pct": (close - entry_price) / entry_price * 100 if entry_price else 0,
                }
            )
            in_position = False

    if in_position and not signals.empty:
        last = signals.iloc[-1]
        close = float(last["Close"])
        gross = (close - entry_price) * qty
        costs = brokerage * 2
        pnl = gross - costs
        trades.append(
            {
                "entry_time": entry_time,
                "exit_time": signals.index[-1],
                "entry_price": entry_price,
                "exit_price": close,
                "quantity": qty,
                "gross_pnl": gross,
                "costs": costs,
                "pnl": pnl,
                "return_pct": (close - entry_price) / entry_price * 100 if entry_price else 0,
            }
        )

    trades_df = pd.DataFrame(trades)
    metrics = _metrics(trades_df, capital)
    return BacktestResult(signals, trades_df, metrics)


def _metrics(trades: pd.DataFrame, capital: float) -> dict:
    cap = max(float(capital or 1.0), 1.0)
    if trades.empty:
        return {
            "trades": 0,
            "total_pnl": 0.0,
            "return_pct": 0.0,
            "win_rate": 0.0,
            "avg_pnl": 0.0,
            "max_drawdown": 0.0,
        }
    pnl = trades["pnl"].astype(float)
    equity = pnl.cumsum()
    peak = equity.cummax()
    drawdown = equity - peak
    wins = int((pnl > 0).sum())
    total = int(len(trades))
    total_pnl = float(pnl.sum())
    return {
        "trades": total,
        "total_pnl": total_pnl,
        "return_pct": total_pnl / cap * 100,
        "win_rate": wins / total * 100 if total else 0.0,
        "avg_pnl": float(pnl.mean()),
        "max_drawdown": float(drawdown.min()) if len(drawdown) else 0.0,
    }


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))
