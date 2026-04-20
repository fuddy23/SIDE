import pandas as pd
import streamlit as st

from app.config import CONFIG
from app.db import get_conn, init_db

DB_PATH = "data/trades.db"

st.set_page_config(page_title="AI Auto Trader Dashboard", layout="wide")
st.title("📈 AI自動売買ダッシュボード")

conn = get_conn(CONFIG.db_path)
init_db(conn)
trades = pd.read_sql_query("SELECT * FROM trades ORDER BY id DESC", conn)
equity = pd.read_sql_query("SELECT * FROM equity_curve ORDER BY id", conn)
signals = pd.read_sql_query("SELECT * FROM signals ORDER BY id DESC", conn)

if equity.empty:
    st.warning("取引データがありません。先に run_trader.py を実行してください。")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("最新資産", f"{equity['total_equity'].iloc[-1]:,.0f}")
col2.metric("現金残高", f"{equity['cash'].iloc[-1]:,.0f}")
col3.metric("約定件数", f"{len(trades):,}")

st.subheader("資産推移 (Equity Curve)")
plot_df = equity.copy()
plot_df["ts"] = pd.to_datetime(plot_df["ts"])
st.line_chart(plot_df.set_index("ts")["total_equity"])

st.subheader("承認待ち/承認済みシグナル")
if signals.empty:
    st.info("まだシグナルがありません。")
else:
    signals_view = signals.copy()
    signals_view["approved"] = signals_view["approved"].map({1: "承認", 0: "見送り"})
    signals_view = signals_view.rename(
        columns={
            "ts": "日時",
            "symbol": "銘柄",
            "side": "売買",
            "qty": "数量",
            "price": "価格",
            "predicted_prob": "上昇確率",
            "reason": "投資/売買理由",
            "approved": "承認結果",
            "note": "メモ",
        }
    )
    st.dataframe(signals_view, use_container_width=True)

st.subheader("約定履歴")
if trades.empty:
    st.info("まだ約定履歴がありません。")
else:
    trades_view = trades.rename(
        columns={
            "ts": "日時",
            "symbol": "銘柄",
            "side": "売買",
            "qty": "数量",
            "price": "価格",
            "predicted_prob": "上昇確率",
            "reason": "投資/売買理由",
            "pnl": "損益",
        }
    )
    st.dataframe(trades_view, use_container_width=True)
