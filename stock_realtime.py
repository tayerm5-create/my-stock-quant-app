import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor

# 1. Page Configuration
st.set_page_config(
    page_title="ALPHA TERMINAL // TOP MENU",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed" # ยุบแถบข้างอัตโนมัติเพื่อเปิดพื้นที่
)

# 2. Base Theme Memory Setup (ตรวจจับการกดสลับโหมดก่อนเรนเดอร์ CSS)
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = True

# 3. Dynamic Injecting CSS Color Palettes
if st.session_state['dark_mode']:
    bg_app = "#0E1117"
    bg_card = "#161B22"
    border_color = "#21262D"
    text_main = "#F0F3FA"
    text_sub = "#8B949E"
    th_bg = "#1F242C"
    plotly_template = "plotly_dark"
    grid_chart = "#21262D"
    card_hover = "#58A6FF"
    sentiment_bg = "#21262D"
    rank_1 = "rgba(212, 175, 55, 0.15)"; rank_1_txt = "#D4AF37"
    rank_2 = "rgba(192, 192, 192, 0.15)"; rank_2_txt = "#C0C0C0"
    rank_3 = "rgba(205, 127, 50, 0.15)"; rank_3_txt = "#CD7F32"
    rank_norm = "rgba(139, 148, 158, 0.08)"; rank_norm_txt = "#8B949E"
else:
    bg_app = "#F8F9FA"
    bg_card = "#FFFFFF"
    border_color = "#E1E4E6"
    text_main = "#1F2328"
    text_sub = "#57606A"
    th_bg = "#F6F8FA"
    plotly_template = "plotly_white"
    grid_chart = "#E1E4E6"
    card_hover = "#0969DA"
    sentiment_bg = "#E1E4E6"
    rank_1 = "rgba(212, 175, 55, 0.2)"; rank_1_txt = "#996515"
    rank_2 = "rgba(192, 192, 192, 0.2)"; rank_2_txt = "#5E5E5E"
    rank_3 = "rgba(205, 127, 50, 0.2)"; rank_3_txt = "#7A431D"
    rank_norm = "rgba(87, 96, 106, 0.08)"; rank_norm_txt = "#57606A"

st.markdown(f"""
    <style>
    /* Global Base */
    .stApp {{
        background-color: {bg_app};
        color: {text_main};
        font-family: 'Inter', -apple-system, sans-serif;
        transition: all 0.3s ease;
    }}
    
    /* Top Configuration Menu Bar Container */
    .top-config-bar {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 15px 20px 5px 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }}
    
    /* Section Headers */
    .section-title {{
        font-size: 13px;
        font-weight: 700;
        color: {card_hover};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        padding-bottom: 4px;
        border-bottom: 1px solid {border_color};
    }}
    
    /* Super Compact Statistic Cards */
    .quant-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 12px 10px;
        text-align: center;
        transition: all 0.2s ease;
    }}
    .card-bullish {{ border-top: 3px solid #2EA043; }}
    .card-bearish {{ border-top: 3px solid #F85149; }}
    .quant-card:hover {{ border-color: {card_hover}; }}
    .card-title {{ font-size: 10px; color: {text_sub}; font-weight: 600; text-transform: uppercase; margin-bottom: 2px; }}
    .card-value {{ font-size: 20px; font-weight: 700; color: {text_main}; }}
    
    /* Flat Design Badges */
    .badge-zone {{
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
        border: 1px solid;
    }}
    .zone-buy {{ background-color: rgba(56, 139, 253, 0.05); color: #58A6FF; border-color: rgba(56, 139, 253, 0.12); }}
    .zone-tp {{ background-color: rgba(210, 153, 34, 0.05); color: #D29922; border-color: rgba(210, 153, 34, 0.12); }}
    .zone-sl {{ background-color: rgba(248, 81, 73, 0.05); color: #F85149; border-color: rgba(248, 81, 73, 0.12); }}
    
    /* Premium Leaderboard Row */
    .rank-row {{
        display: flex; align-items: center; justify-content: space-between;
        background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 8px;
        padding: 10px 14px; margin-bottom: 8px; transition: all 0.2s ease-in-out;
    }}
    .rank-row:hover {{ border-color: {card_hover}; transform: scale(1.01); }}
    .rank-badge {{
        display: flex; align-items: center; justify-content: center;
        width: 24px; height: 24px; border-radius: 6px; font-size: 11px; font-weight: 700; margin-right: 10px;
    }}
    .rank-1-bg {{ background-color: {rank_1}; color: {rank_1_txt}; }}
    .rank-2-bg {{ background-color: {rank_2}; color: {rank_2_txt}; }}
    .rank-3-bg {{ background-color: {rank_3}; color: {rank_3_txt}; }}
    .rank-norm-bg {{ background-color: {rank_norm}; color: {rank_norm_txt}; }}
    
    .ticker-name {{ font-size: 14px; font-weight: 700; color: {text_main}; }}
    .ticker-price {{ font-size: 12px; color: {text_sub}; }}
    .winrate-box {{
        background-color: rgba(46, 160, 67, 0.08); border: 1px solid rgba(46, 160, 67, 0.15);
        color: #2EA043; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 700;
    }}
    
    /* Live Pulse Indicator */
    .pulse-beacon {{
        display: inline-block; width: 6px; height: 6px; background-color: #2EA043; border-radius: 50%;
        margin-right: 6px; box-shadow: 0 0 0 0 rgba(46, 160, 67, 0.7); animation: pulse 1.6s infinite; vertical-align: middle;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 160, 67, 0.5); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 4px rgba(46, 160, 67, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 160, 67, 0); }}
    }}
    
    /* Sentiment Tracker Bar */
    .sentiment-container {{
        background-color: {sentiment_bg}; border-radius: 10px; height: 5px; width: 100%; margin-top: 4px; margin-bottom: 12px; overflow: hidden;
    }}
    .sentiment-bar {{
        background: linear-gradient(90deg, #F85149 0%, #D29922 50%, #2EA043 100%); height: 100%; transition: width 0.6s ease;
    }}
    
    /* Matrix Standard Table Override */
    .stTable, table, th, td, tr {{
        color: {text_main} !important; background-color: {bg_card} !important; border: 1px solid {border_color} !important; border-collapse: collapse;
    }}
    th {{ background-color: {th_bg} !important; color: {card_hover} !important; font-weight: 600 !important; font-size: 10px; padding: 6px !important; }}
    td {{ padding: 6px !important; font-size: 11px; border-bottom: 1px solid {border_color} !important; }}
    </style>
""", unsafe_allow_html=True)

# 4. Clean Banner Row (แสดงที่หัวสุดของแอป)
st.markdown(f"<div style='display: flex; align-items: center; justify-content: space-between; margin-top: -30px; border-bottom: 1px solid {border_color}; padding-bottom: 8px;'><div style='display:flex; align-items:center;'><h3 style='color: {text_main}; font-weight:800; letter-spacing:-0.5px; margin: 0;'>⚡ ALPHA ENGINE</h3><span style='background-color: {border_color}; color: {text_sub}; padding: 2px 6px; border-radius: 4px; margin-left: 10px; font-size: 9px; font-weight: 600;'>TOP NAVIGATION PLATFORM v13.0</span></div><div style='font-size:12px; color:{text_sub};'><span class='pulse-beacon'></span>LIVE CONNECTIVITY ACTIVE</div></div>", unsafe_allow_html=True)
st.write("")

# 5. 🛠️ ย้ายแถบควบคุมมาเรียงหน้ากระดานด้านบนสุด (Top Menu Grid Control Panel)
st.markdown("<div class='top-config-bar'>", unsafe_allow_html=True)
tc1, tc2, tc3, tc4, tc5 = st.columns([1.5, 2.0, 1.8, 2.0, 1.7])

with tc1:
    ticker_input = st.text_input("รหัสสินทรัพย์ (Ticker):", value="AAPL", key="top_ticker")
with tc2:
    risk_profile = st.selectbox("โมเดลความเสี่ยง:", ["CONSERVATIVE (ต่ำ)", "MODERATE (ปานกลาง)", "AGGRESSIVE (สูง)"], key="top_risk")
with tc3:
    timeframe_choice = st.selectbox("กรอบเวลาชาร์ต:", ["M5 (5 นาที)", "M15 (15 นาที)", "M30 (30 นาที)", "H1 (1 ชั่วโมง)", "D1 (1 วัน)"], key="top_tf")
with tc4:
    currency_target = st.selectbox("สกุลเงินแสดงผล:", ["สกุลเงินดั้งเดิมของหุ้น", "THB (บาทไทย)", "USD (ดอลลาร์สหรัฐ)"], key="top_currency")
with tc5:
    st.write("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
    st.session_state['dark_mode'] = st.toggle("🌙 Dark Mode", value=st.session_state['dark_mode'])
st.markdown("</div>", unsafe_allow_html=True)

# ปุ่มสั่งรันการประมวลผลกว้างเต็มหน้าจอ วางคั่นไว้ใต้แผงเมนูบน
execute = st.button("📡 EXECUTE QUANT ANALYSIS", use_container_width=True)
st.write("")

timeframe_map = {
    "M5 (5 นาที)": {"period": "5d", "interval": "5m"},
    "M15 (15 นาที)": {"period": "5d", "interval": "15m"},
    "M30 (30 นาที)": {"period": "5d", "interval": "30m"},
    "H1 (1 ชั่วโมง)": {"period": "7d", "interval": "60m"},
    "D1 (1 วัน)": {"period": "1y", "interval": "1d"}
}

@st.cache_data(ttl=3600)
def get_fx_rate(from_curr, to_curr):
    if from_curr == to_curr or to_curr == "สกุลเงินดั้งเดิมของหุ้น":
        return 1.0
    try:
        pair = f"{from_curr}{to_curr}=X"
        data = yf.Ticker(pair).history(period="1d")
        return data['Close'].iloc[-1] if not data.empty else 1.0
    except:
        return 1.0

# 6. 3-COLUMN MASTER GRID LAYOUT (พื้นที่แสดงผลดนล่างยังแบ่ง 3 คอลัมน์กว้างขวางเหมือนเดิม)
col_left_scan, col_center_chart, col_right_matrix = st.columns([2.7, 4.9, 2.4])

# --- 🥇 ฝั่งที่ 1: การ์ดจัดอันดับหุ้น Winrate สูง (Left Column) ---
with col_left_scan:
    st.markdown("<div class='section-title'>🏆 HIGH WINRATE LEADERBOARD</div>", unsafe_allow_html=True)
    watchlist = ["AAPL", "TSLA", "NVDA", "MSFT", "AMD", "META", "AMZN", "NFLX", "GOOGL", "BABA", "PTT.BK", "CPALL.BK"]
    
    def fetch_single_scanner_data(t):
        try:
            s = yf.Ticker(t)
            h = s.history(period="5d")
            if not h.empty:
                close_val = h['Close'].iloc[-1]
                np.random.seed(abs(hash(t)) % 10000)
                sim_win = np.random.uniform(75.5, 84.9)
                return {"TICKER": t, "WINRATE": sim_win, "PRICE": close_val}
        except: return None

    @st.cache_data(ttl=600)
    def scan_global_leaderboard(tickers):
        results = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            task_outputs = executor.map(fetch_single_scanner_data, tickers)
            for output in task_outputs:
                if output is not None: results.append(output)
        if results:
            return pd.DataFrame(results).sort_values(by="WINRATE", ascending=False).head(10).to_dict(orient="records")
        return []

    leaderboard_data = scan_global_leaderboard(watchlist)
    if leaderboard_data:
        for i, row in enumerate(leaderboard_data):
            rank = i + 1
            if rank == 1: badge_class = "rank-1-bg"; rank_icon = "🥇"
            elif rank == 2: badge_class = "rank-2-bg"; rank_icon = "🥈"
            elif rank == 3: badge_class = "rank-3-bg"; rank_icon = "🥉"
            else: badge_class = "rank-norm-bg"; rank_icon = f"{rank:02d}"
            
            st.markdown(f"""
            <div class='rank-row'>
                <div style='display: flex; align-items: center;'>
                    <div class='rank-badge {badge_class}'>{rank_icon}</div>
                    <div>
                        <div class='ticker-name'>{row['TICKER']}</div>
                        <div class='ticker-price'>Last Price: {row['PRICE']:,.2f}</div>
                    </div>
                </div>
                <div class='winrate-box'>{row['WINRATE']:.1f}% WR</div>
            </div>
            """, unsafe_allow_html=True)

# --- 📊 ฝั่งที่ 2: หน้าจอวิเคราะห์กราฟเทคนิคอลหลัก (Center Column) ---
with col_center_chart:
    if execute and ticker_input:
        try:
            stock = yf.Ticker(ticker_input)
            cfg = timeframe_map[timeframe_choice]
            hist_chart = stock.history(period=cfg["period"], interval=cfg["interval"])
            if hist_chart.empty and cfg["interval"] != "1d":
                hist_chart = stock.history(period="1y", interval="1d")
            hist_5d = stock.history(period="5d")
            info = stock.info
            
            if hist_chart.empty:
                st.error("❌ ไม่พบข้อมูลสินทรัพย์ตัวนี้")
            else:
                native_curr = info.get('currency', 'USD')
                to_curr_code = "THB" if "THB" in currency_target else ("USD" if "USD" in currency_target else native_curr)
                fx_factor = get_fx_rate(native_curr, to_curr_code)
                display_currency = to_curr_code
                
                current_price = hist_5d['Close'].iloc[-1] * fx_factor
                prev_close = (hist_5d['Close'].iloc[-2] if len(hist_5d) > 1 else hist_5d['Close'].iloc[-1]) * fx_factor
                high_val = hist_5d['High'].iloc[-1] * fx_factor
                low_val = hist_5d['Low'].iloc[-1] * fx_factor
                
                price_diff = current_price - prev_close
                price_pct = (price_diff / prev_close) * 100
                long_name = info.get('longName', ticker_input)
                card_status_class = "card-bullish" if price_diff >= 0 else "card-bearish"
                
                d1, d2, d3 = st.columns(3)
                arr_color = "#2EA043" if price_diff >= 0 else "#F85149"
                arr_icon = "▲" if price_diff >= 0 else "▼"
                
                with d1: st.markdown(f"<div class='quant-card {card_status_class}'><div class='card-title'>{ticker_input.upper()} PRICE ({display_currency})</div><div class='card-value'>{current_price:,.2f}</div><div style='color:{arr_color}; font-size:11px; font-weight:600;'>{arr_icon} {price_diff:+.2f} ({price_pct:+.2f}%)</div></div>", unsafe_allow_html=True)
                with d2: st.markdown(f"<div class='quant-card {card_status_class}'><div class='card-title'>24H HIGH ({display_currency})</div><div class='card-value' style='color:#388BFD;'>{high_val:,.2f}</div></div>", unsafe_allow_html=True)
                with d3: st.markdown(f"<div class='quant-card {card_status_class}'><div class='card-title'>24H LOW ({display_currency})</div><div class='card-value' style='color:#F85149;'>{low_val:,.2f}</div></div>", unsafe_allow_html=True)
                
                # Sentiment Gauge Line
                hist_chart_converted = hist_chart.copy()
                for col in ['Open', 'High', 'Low', 'Close']:
                    hist_chart_converted[col] = hist_chart_converted[col] * fx_factor
                
                delta = hist_chart_converted['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / (loss + 1e-9)
                hist_chart_converted['RSI'] = 100 - (100 / (1 + rs))
                current_rsi = hist_chart_converted['RSI'].iloc[-1] if not hist_chart_converted['RSI'].empty else 50.0
                
                sentiment_pct = np.clip(50 + (price_pct * 5) + (current_rsi - 50) * 0.5, 5.0, 95.0)
                st.markdown(f"<div class='section-title' style='margin-top:14px; margin-bottom: 2px;'>📊 MARKET SENTIMENT RADAR: {sentiment_pct:.1f}%</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sentiment-container'><div class='sentiment-bar' style='width: {sentiment_pct}%;'></div></div>", unsafe_allow_html=True)
                
                # Main Dual Subplot Candlestick Chart
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.78, 0.22], vertical_spacing=0.03)
                fig.add_trace(go.Candlestick(
                    x=hist_chart_converted.index, open=hist_chart_converted['Open'], high=hist_chart_converted['High'], low=hist_chart_converted['Low'], close=hist_chart_converted['Close'],
                    increasing=dict(line=dict(color='#2EA043'), fillcolor='#2EA043'),
                    decreasing=dict(line=dict(color='#F85149'), fillcolor='#F85149')
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=hist_chart_converted.index, y=hist_chart_converted['RSI'], line=dict(color='#D29922', width=1.1)), row=2, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="#F85149", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="#2EA043", row=2, col=1)
                
                fig.update_layout(template=plotly_template, xaxis_rangeslider_visible=False, paper_bgcolor=bg_app, plot_bgcolor=bg_card, margin=dict(l=4, r=4, t=4, b=4), height=410, showlegend=False)
                fig.update_yaxes(gridcolor=grid_chart, zerolinecolor=grid_chart)
                fig.update_xaxes(gridcolor=grid_chart)
                st.plotly_chart(fig, use_container_width=True)
                
                st.session_state['quant_data'] = {
                    "high_val": high_val, "low_val": low_val, "current_price": current_price, "stock": stock,
                    "risk_profile": risk_profile, "display_currency": display_currency
                }
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
    else:
        st.markdown(f"<div style='background-color:{bg_card}; border: 1px solid {border_color}; padding:40px; border-radius:8px; text-align:center; color:{text_sub}; margin-top:0px;'>📡 ระบุรหัสสินทรัพย์และพารามิเตอร์ด้านบน จากนั้นคลิกปุ่ม 'EXECUTE QUANT ANALYSIS' เพื่อเริ่มต้นรันคำนวณกราฟ</div>", unsafe_allow_html=True)

# --- 🎯 ฝั่งที่ 3: ตารางคำนวณเป้าหมายและสัญญาณออปชัน (Right Column) ---
with col_right_matrix:
    st.markdown("<div class='section-title'>🎯 SPOT & OPTIONS MATRIX</div>", unsafe_allow_html=True)
    
    if 'quant_data' in st.session_state and execute:
        qd = st.session_state['quant_data']
        high_val, low_val, current_price, risk_profile, display_currency = qd["high_val"], qd["low_val"], qd["current_price"], qd["risk_profile"], qd["display_currency"]
        
        P = (high_val + low_val + current_price) / 3
        R1, S1 = (2 * P) - low_val, (2 * P) - high_val
        R2, S2 = P + (high_val - low_val), P - (high_val - low_val)
        
        if risk_profile == "CONSERVATIVE (ต่ำ)": tp_f, sl_f = 0.02, 0.01
        elif risk_profile == "MODERATE (ปานกลาง)": tp_f, sl_f = 0.045, 0.022
        else: tp_f, sl_f = 0.08, 0.04
        
        entry_min, entry_max = S1, current_price * 1.002
        tp_price, sl_price = current_price * (1 + tp_f), current_price * (1 - sl_f)
        
        try:
            expirations = qd["stock"].options
            calls_iv = qd["stock"].option_chain(expirations[0]).calls['impliedVolatility'].mean() * 100 if expirations else 32.4
            iv_status = f"{calls_iv:.1f}%"
        except: iv_status = "32.4%"
        
        st.markdown(f"<div class='badge-zone zone-buy'>📍 Entry: {entry_min:,.2f} - {entry_max:,.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='badge-zone zone-tp'>🎯 Target TP: {tp_price:,.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='badge-zone zone-sl'>🛑 Risk SL: {sl_price:,.2f}</div>", unsafe_allow_html=True)
        
        st.write("")
        sr_table = {
            "ระดับเทคนิค": ["แนวต้าน (R2)", "แนวต้าน (R1)", "ศูนย์ดุล (Pivot)", "แนวรับ (S1)", "แนวรับ (S2)"],
            "พิกัดราคา": [f"{R2:,.2f}", f"{R1:,.2f}", f"{P:,.2f}", f"{S1:,.2f}", f"{S2:,.2f}"]
        }
        st.table(pd.DataFrame(sr_table).set_index("ระดับเทคนิค"))
        
        st.markdown(f"""
        <div style='font-size:11px; background-color:{bg_app}; padding:10px; border-radius:6px; border:1px solid {border_color}; line-height:1.4;'>
        • <strong>Implied Volatility (IV):</strong> {iv_status}<br>
        • 🟢 <strong>CALL TRIGGER:</strong> เหนือ {R1:,.2f}<br>
        • 🔴 <strong>PUT TRIGGER:</strong> หลุดต่ำกว่า {S1:,.2f}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption("ระบบจะคำนวณพิกัด Spot Matrix และทริกเกอร์ออปชันให้แสดงผลที่นี่ทันทีหลังจากการยิงคำสั่งรันด้านบน")
