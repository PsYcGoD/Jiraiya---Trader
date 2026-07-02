import base64
import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.broker_data import credential_status, fetch_market_data
from components.strategy import run_backtest


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


st.set_page_config(page_title="PsYcGoD Strategy Lab", layout="wide")


def apply_css_file(path: Path) -> None:
    if path.exists():
        st.markdown(f"<style>{path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def set_background(img_path: Path) -> None:
    if not img_path.exists():
        return
    encoded = base64.b64encode(img_path.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <style>
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background-image:
              radial-gradient(80% 120% at 10% 10%, rgba(120,0,255,0.20), transparent 40%),
              radial-gradient(80% 120% at 90% 90%, rgba(0,255,220,0.18), transparent 40%),
              url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            opacity: 0.22;
            z-index: -1;
            filter: saturate(120%) hue-rotate(8deg);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def strategy_params(strategy_name: str) -> dict:
    if strategy_name == "Moving Average Crossover":
        short_window = st.slider("Short MA", 3, 50, 9)
        long_window = st.slider("Long MA", 5, 200, 21)
        if long_window <= short_window:
            st.warning("Long MA should be greater than Short MA.")
        return {"short_window": short_window, "long_window": long_window}

    if strategy_name == "RSI Reversion":
        return {
            "rsi_period": st.slider("RSI Period", 5, 40, 14),
            "rsi_lower": st.slider("RSI Buy Level", 5, 45, 30),
            "rsi_upper": st.slider("RSI Sell Level", 55, 95, 70),
        }

    return {"breakout_lookback": st.slider("Breakout Lookback", 5, 100, 20)}


def make_chart(df: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color="#00e5a0",
            decreasing_line_color="#ff4d6d",
            increasing_fillcolor="#00e5a0",
            decreasing_fillcolor="#ff4d6d",
            name="Price",
        )
    )

    buys = df[df.get("signal", 0) == 1]
    sells = df[df.get("signal", 0) == -1]
    if not buys.empty:
        fig.add_scatter(
            x=buys.index,
            y=buys["Low"],
            mode="markers",
            name="Buy",
            marker=dict(color="#00ffd1", size=10, symbol="triangle-up", line=dict(width=1, color="#021b1f")),
        )
    if not sells.empty:
        fig.add_scatter(
            x=sells.index,
            y=sells["High"],
            mode="markers",
            name="Sell",
            marker=dict(color="#ff4d6d", size=10, symbol="triangle-down", line=dict(width=1, color="#2a0b13")),
        )

    for col, color in [
        ("short_ma", "#f7d154"),
        ("long_ma", "#7dd3fc"),
        ("breakout_high", "#22c55e"),
        ("breakout_low", "#ef4444"),
    ]:
        if col in df:
            fig.add_scatter(x=df.index, y=df[col], mode="lines", name=col, line=dict(color=color, width=1.4))

    fig.update_layout(
        template="plotly_dark",
        height=560,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_rangeslider_visible=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title=title,
        font=dict(color="#d8f3ff"),
    )
    return fig


apply_css_file(ASSETS_DIR / "styles.css")
set_background(ASSETS_DIR / "psy_bg.png")

st.markdown('<div class="app-header">PsYcGoD Strategy Lab</div>', unsafe_allow_html=True)
st.caption("Create strategy rules, fetch historical data, and backtest before any live trading.")

with st.sidebar:
    st.header("Data")
    source = st.selectbox("Source", ["Yahoo Finance", "Dhan", "Kite"], index=0)
    ticker = st.text_input("Symbol", "RELIANCE.NS").strip().upper()
    mode = st.selectbox("Mode", ["Intraday", "Daily"], index=0)
    if mode == "Intraday":
        interval = st.selectbox("Interval", ["1m", "2m", "5m", "15m"], index=2)
        lookback = st.selectbox("Lookback days", [1, 3, 5, 7, 10, 14], index=2)
        daily_period = "1mo"
    else:
        interval = "1d"
        lookback = 30
        daily_period = st.selectbox("Daily period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

    st.header("Strategy")
    strategy = st.selectbox(
        "Strategy Builder",
        ["Moving Average Crossover", "RSI Reversion", "Breakout"],
        index=0,
    )
    params = strategy_params(strategy)

    st.header("Backtest")
    capital = st.number_input("Capital", min_value=1000.0, value=50000.0, step=1000.0)
    quantity = st.number_input("Quantity per trade", min_value=1, value=1, step=1)
    brokerage = st.number_input("Brokerage per side", min_value=0.0, value=20.0, step=1.0)
    run_btn = st.button("Run Backtest", type="primary")

    st.header("Credentials")
    status = credential_status()
    st.write(f"Dhan: {status['Dhan']}")
    st.write(f"Kite: {status['Kite']}")
    st.caption("Credentials are read from environment variables. Do not commit .env files.")

if "result" not in st.session_state:
    st.session_state["result"] = None

if run_btn:
    try:
        data = fetch_market_data(source, ticker, mode, interval, int(lookback), daily_period)
        if data.frame.empty:
            st.warning("No data returned. Try another symbol, source, interval, or period.")
        else:
            result = run_backtest(data.frame, strategy, params, capital, int(quantity), brokerage)
            st.session_state["result"] = {
                "data_source": data.source,
                "message": data.message,
                "strategy": strategy,
                "params": params,
                "result": result,
            }
    except Exception as exc:
        st.error(str(exc))

saved = st.session_state.get("result")

if not saved:
    st.info("Choose a data source and strategy, then click Run Backtest.")
else:
    result = saved["result"]
    metrics = result.metrics
    title = f"{ticker} | {saved['strategy']} | {saved['data_source']}"

    a, b, c, d, e = st.columns(5)
    a.metric("Trades", metrics["trades"])
    b.metric("Total P&L", f"Rs {metrics['total_pnl']:,.2f}")
    c.metric("Return", f"{metrics['return_pct']:.2f}%")
    d.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
    e.metric("Max Drawdown", f"Rs {metrics['max_drawdown']:,.2f}")

    st.caption(saved["message"])
    st.markdown('<div class="panel chart-panel">', unsafe_allow_html=True)
    st.plotly_chart(make_chart(result.frame, title), width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([0.55, 0.45])
    with left:
        st.subheader("Trades")
        if result.trades.empty:
            st.write("No completed trades for these rules.")
        else:
            st.dataframe(result.trades, use_container_width=True)
            st.download_button(
                "Download trades CSV",
                result.trades.to_csv(index=False),
                file_name="jiraiya_backtest_trades.csv",
                mime="text/csv",
            )

    with right:
        st.subheader("Strategy Parameters")
        st.json(saved["params"])
        st.warning(
            "Backtesting is research only. It does not guarantee live profit. "
            "Use paper trading before any real order placement."
        )

st.markdown('<div class="footer-log">Strategy Lab ready | backtest-only | no live orders</div>', unsafe_allow_html=True)
