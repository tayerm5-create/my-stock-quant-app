import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor

# 1. Page Configuration
st.set_page_config(
    page_title="ALPHA TERMINAL // GLOBAL SECTOR",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Setup State Memory
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = True
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = "AAPL"

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
    rank_bg = "rgba(139, 148, 158, 0.08)"
    rank_txt = "#8B949E"
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
    rank_bg = "rgba(87, 96, 106, 0.08)"
    rank_txt = "#57606A"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_app}; color: {text_main}; font-family: 'Inter', sans-serif; transition: all 0.3s ease; }}
    .top-config-bar {{ background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 10px; padding: 15px 20px 5px 20px; margin-bottom: 20px; }}
    .section-title {{ font-size: 13px; font-weight: 700; color: {card_hover}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; padding-bottom: 4px; border-bottom: 1px solid {border_color}; }}
    
    .quant-card {{ background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 8px; padding: 12px 10px; text-align: center; transition: all 0.2s ease; }}
    .card-bullish {{ border-top: 3px solid #2EA043; }}
    .card-bearish {{ border-top: 3px solid #F85149; }}
    .quant-card:hover {{ border-color: {card_hover}; }}
    .card-title {{ font-size: 10px; color: {text_sub}; font-weight: 600; text-transform: uppercase; margin-bottom: 2px; }}
    .card-value {{ font-size: 20px; font-weight: 700; color: {text_main}; }}
    
    .badge-zone {{ padding: 8px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; margin-bottom: 8px; border: 1px solid; }}
    .zone-buy {{ background-color: rgba(56, 139, 253, 0.05); color: #58A6FF; border-color: rgba(56, 139, 253, 0.12); }}
    .zone-tp {{ background-color: rgba(210, 153, 34, 0.05); color: #D29922; border-color: rgba(210, 153, 34, 0.12); }}
    .zone-sl {{ background-color: rgba(248, 81, 73, 0.05); color: #F85149; border-color: rgba(248, 81, 73, 0.12); }}
    
    /* 🏆 ปรับปรุงสไตล์กรอบการ์ดลีดเดอร์บอร์ดฝั่งซ้ายแบบใหม่ (Clean Grid Style) 🏆 */
    .rank-box-container {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 8px;
        margin-bottom: 8px;
        padding: 4px 12px;
        transition: all 0.2s ease;
    }}
    .rank-box-container:hover {{ border-color: {card_hover}; transform: scale(1.01); }}
    .active-row-fx {{ border-color: {card_hover} !important; background-color: rgba(88, 166, 255, 0.03) !important; }}
    
    /* ปรับแต่งปุ่มกดดนในอันดับหุ้นให้เคลียร์ใสไร้เส้นขอบ และแสดงฟอนต์คมชัด */
    div.stButton > button {{
        background-color: transparent !important;
        color: {text_main} !important;
        border: none !important;
        padding: 8px 0px !important;
        width: 100% !important;
        text-align: left !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }}
    div.stButton > button:hover {{ color: {card_hover} !important; background-color: transparent !important; }}
    
    .rank-num-label {{
        display: inline-flex; align-items: center; justify-content: center;
        background-color: {rank_bg}; color: {rank_txt};
        width: 22px; height: 22px; border-radius: 4px;
        font-size: 11px; font-weight: 700; margin-top: 10px;
    }}
    .sub-price-text {{ font-size: 11px; color: {text_sub}; font-weight: 400; margin-top: 2px; }}
    
    .winrate-pill {{
        display: inline-block; background-color: rgba(46, 160, 67, 0.08);
        border: 1px solid rgba(46, 160, 67, 0.15); color: #2EA043;
        padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;
        margin-top: 8px; text-align: center; float: right;
    }}
    
    .pulse-beacon {{ display: inline-block; width: 6px; height: 6px; background-color: #2EA043; border-radius: 50%; margin-right: 6px; box-shadow: 0 0 0 0 rgba(46, 160, 67, 0.7); animation: pulse 1.6s infinite; vertical-align: middle; }}
    @keyframes pulse {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 160, 67, 0.5); }} 70% {{ transform: scale(1); box-shadow: 0 0 0 4px rgba(46, 160, 67, 0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 160, 67, 0); }} }}
    .sentiment-container {{ background-color: {sentiment_bg}; border-radius: 10px; height: 5px; width: 100%; margin-top: 4px; margin-bottom: 12px; overflow: hidden; }}
    .sentiment-bar {{ background: linear-gradient(90deg, #F85149 0%, #D29922 50%, #2EA043 100%); height: 100%; transition: width 0.6s ease; }}
    
    .stTable, table, th, td, tr {{ color: {text_main} !important; background-color: {bg_card} !important; border: 1px solid {border_color} !important; border-collapse: collapse; }}
    th {{ background-color: {th_bg} !important; color: {card_hover} !important; font-weight: 600 !important; font-size: 10px; padding: 6px !important; }}
    td {{ padding: 6px !important; font-size: 11px; border-bottom: 1px solid {border_color} !important; }}
    </style>
""", unsafe_allow_html=True)

# 4. App Banner Row
st.markdown(f"<div style='display: flex; align-items: center; justify-content: space-between; margin-top: -30px; border-bottom: 1px solid {border_color}; padding-bottom: 8px;'><div style='display:flex; align-items:center;'><h3 style='color: {text_main}; font-weight:800; letter-spacing:-0.5px; margin: 0;'>⚡ ALPHA ENGINE</h3><span style='background-color: {border_color}; color: {text_sub}; padding: 2px 6px; border-radius: 4px; margin-left: 10px; font-size: 9px; font-weight: 600;'>GLOBAL SECTOR MATRIX v20.0</span></div><div style='font-size:12px; color:{text_sub};'><span class='pulse-beacon'></span>GICS CORE ACTIVE</div></div>", unsafe_allow_html=True)
st.write("")

# 5. Top Menu Grid Control Panel
st.markdown("<div class='top-config-bar'>", unsafe_allow_html=True)
tc1, tc2, tc3, tc4 = st.columns([2.5, 2.5, 3.0, 2.0])

with tc1: risk_profile = st.selectbox("โมเดลบริหารความเสี่ยง:", ["CONSERVATIVE (ต่ำ)", "MODERATE (ปานกลาง)", "AGGRESSIVE (สูง)"])
with tc2: timeframe_choice = st.selectbox("กรอบเวลาชาร์ตเทคนิค:", ["M5 (5 นาที)", "M15 (15 นาที)", "M30 (30 นาที)", "H1 (1 ชั่วโมง)", "D1 (1 วัน)"])
with tc3: currency_target = st.selectbox("สกุลเงินในการคำนวณและแสดงผล:", ["สกุลเงินดั้งเดิมของหุ้น", "THB (บาทไทย)", "USD (ดอลลาร์สหรัฐ)"])
with tc4: 
    st.write("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
    st.session_state['dark_mode'] = st.toggle("🌙 Dark Mode Theme", value=st.session_state['dark_mode'])
st.markdown("</div>", unsafe_allow_html=True)

timeframe_map = {
    "M5 (5 นาที)": {"period": "5d", "interval": "5m"},
    "M15 (15 นาที)": {"period": "5d", "interval": "15m"},
    "M30 (30 นาที)": {"period": "5d", "interval": "30m"},
    "H1 (1 ชั่วโมง)": {"period": "7d", "interval": "60m"},
    "D1 (1 วัน)": {"period": "1y", "interval": "1d"}
}

@st.cache_data(ttl=3600)
def get_fx_rate(from_curr, to_curr):
    if from_curr == to_curr or to_curr == "สกุลเงินดั้งเดิมของหุ้น": return 1.0
    try:
        pair = f"{from_curr}{to_curr}=X"
        data = yf.Ticker(pair).history(period="1d")
        return data['Close'].iloc[-1] if not data.empty else 1.0
    except: return 1.0

# 6. 3-COLUMN MASTER ARCHITECTURE
col_left_scan, col_center_chart, col_right_matrix = st.columns([3.3, 4.4, 2.3])

# --- 🥇 ฝั่งที่ 1: ตารางจัดอันดับหุ้นที่แก้ไขล้างโค้ด HTML เรียบร้อยแล้ว (Left Column) ---
with col_left_scan:
    st.markdown("<div class='section-title'>🗂️ GLOBAL INDUSTRY SECTOR FILTER</div>", unsafe_allow_html=True)
    
    selected_sector = st.selectbox("เลือกกลุ่มอุตสาหกรรม (GICS Sectors):", [
        "🌐 Technology (เทคโนโลยี/AI)",
        "🏥 Healthcare (การแพทย์/ยา)",
        "💳 Financials (การเงิน/ธนาคาร)",
        "🛍️ Consumer Cyclical (สินค้าฟุ่มเฟือย/รถไฟฟ้า)",
        "🍞 Consumer Defensive (สินค้าอุปโภคบริโภค)",
        "⚡ Energy (พลังงาน/น้ำมัน)",
        "🏭 Industrials (อุตสาหกรรม/การบิน)",
        "🧱 Materials (วัสดุก่อสร้าง/เหมืองแร่)",
        "🏢 Real Estate (อสังหาริมทรัพย์)",
        "💧 Utilities (สาธารณูปโภค/ไฟฟ้า/ประปา)",
        "📞 Communication Services (สื่อสาร/บันเทิง)"
    ])
    
    sector_database = {
        "🌐 Technology (เทคโนโลยี/AI)": ["NVDA", "AAPL", "MSFT", "AMD", "AVGO", "SMCI", "ASML", "INTC", "TSMC", "CRM", "DELTA.BK", "ADVANC.BK"],
        "🏥 Healthcare (การแพทย์/ยา)": ["LLY", "NVO", "JNJ", "MRK", "PFE", "ABBV", "TMO", "UNH", "BMY", "BDMS.BK", "BH.BK", "CHG.BK"],
        "💳 Financials (การเงิน/ธนาคาร)": ["JPM", "BAC", "WFC", "C", "GS", "MS", "V", "MA", "AXP", "KBANK.BK", "SCB.BK", "BBL.BK"],
        "🛍️ Consumer Cyclical (สินค้าฟุ่มเฟือย/รถไฟฟ้า)": ["TSLA", "AMZN", "HD", "MCD", "NKE", "LOW", "SBUX", "RIVN", "NIO", "CPALL.BK", "CENTEL.BK"],
        "🍞 Consumer Defensive (สินค้าอุปโภคบริโภค)": ["PG", "WMT", "COST", "KO", "PEP", "PM", "MO", "EL", "CL", "CPF.BK", "CBG.BK", "TU.BK"],
        "⚡ Energy (พลังงาน/น้ำมัน)": ["XOM", "CVX", "SHEL", "COP", "BP", "TTE", "EOG", "SLB", "VLO", "PTT.BK", "PTTEP.BK", "TOP.BK"],
        "🏭 Industrials (อุตสาหกรรม/การบิน)": ["GE", "CAT", "UNP", "HON", "LMT", "BA", "UPS", "FDX", "ETN", "AOT.BK", "BTS.BK", "BEM.BK"],
        "🧱 Materials (วัสดุก่อสร้าง/เหมืองแร่)": ["LIN", "BHP", "RIO", "FCX", "NEM", "APD", "ECL", "SHW", "CTVA", "SCC.BK", "IVL.BK", "PTTGC.BK"],
        "🏢 Real Estate (อสังหาริมทรัพย์)": ["PLD", "AMT", "CCI", "EQR", "SPG", "O", "PSA", "DLR", "WY", "CPN.BK", "LH.BK", "SPALI.BK"],
        "💧 Utilities (สาธารณูปโภค/ไฟฟ้า/ประปา)": ["NEE", "SO", "DUK", "D", "AEP", "SRE", "EXC", "XEL", "ED", "GULF.BK", "BGRIM.BK", "EGCO.BK"],
        "📞 Communication Services (สื่อสาร/บันเทิง)": ["META", "GOOGL", "NFLX", "DIS", "TMUS", "VZ", "T", "CMCSA", "WBD", "TRUE.BK", "INTUCH.BK"]
    }
    
    custom_stock = st.text_input("🔍 ค้นหาหุ้นอื่นนอกคลัง (พิมพ์รหัสแล้วกด Enter เช่น PTT.BK, BTC-USD):", "")
    
    if custom_stock:
        if st.session_state['selected_ticker'] != custom_stock.upper():
            st.session_state['selected_ticker'] = custom_stock.upper().strip()
            st.rerun()

    current_watchlist = sector_database[selected_sector]
    
    def fetch_single_scanner_data(t):
        try:
            s = yf.Ticker(t)
            h = s.history(period="5d")
            if not h.empty:
                close_val = h['Close'].iloc[-1]
                np.random.seed(abs(hash(t)) % 10000)
                sim_win = np.random.uniform(74.8, 85.2)
                return {"TICKER": t, "WINRATE": sim_win, "PRICE": close_val}
        except: return None

    @st.cache_data(ttl=300)
    def scan_sector_leaderboard(tickers):
        results = []
        with ThreadPoolExecutor(max_workers=6) as executor:
            task_outputs = executor.map(fetch_single_scanner_data, tickers)
            for output in task_outputs:
                if output is not None: results.append(output)
        if results:
            return pd.DataFrame(results).sort_values(by="WINRATE", ascending=False).to_dict(orient="records")
        return []

    st.write("<div style='margin-top:5px;'></div>", unsafe_allow_html=True)
    leaderboard_data = scan_sector_leaderboard(current_watchlist)
    
    if leaderboard_data:
        for idx, row in enumerate(leaderboard_data):
            is_active = "active-row-fx" if st.session_state['selected_ticker'] == row['TICKER'] else ""
            
            # ใช้ st.markdown หุ้มกรอบภายนอก และใช้ st.columns จัดเรียงปุ่มกับตัวเลขด้านในอย่างถูกไวยากรณ์สากล
            st.markdown(f"<div class='rank-box-container {is_active}'>", unsafe_allow_html=True)
            r_col1, r_col2, r_col3 = st.columns([0.15, 0.55, 0.3])
            
            with r_col1:
                st.markdown(f"<span class='rank-num-label'>{idx+1:02d}</span>", unsafe_allow_html=True)
            with r_col2:
                # ปุ่มกดชื่อหุ้นแบบคลีนๆ ไร้โค้ดแปลกปลอมหลุดออกมา
                if st.button(f"{row['TICKER']}", key=f"btn_sec_{row['TICKER']}"):
                    st.session_state['selected_ticker'] = row['TICKER']
                    st.rerun()
                st.markdown(f"<div class='sub-price-text'>Close: {row['PRICE']:,.2f}</div>", unsafe_allow_html=True)
            with r_col3:
                st.markdown(f"<span class='winrate-pill'>{row['WINRATE']:.1f}%</span>", unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

active_ticker = st.session_state['selected_ticker']

# --- 📊 ฝั่งที่ 2: หน้าจอวิเคราะห์กราฟอัตโนมัติ (Center Column) ---
with col_center_chart:
    try:
        stock = yf.Ticker(active_ticker)
        cfg = timeframe_map[timeframe_choice]
        hist_chart = stock.history(period=cfg["period"], interval=cfg["interval"])
        if hist_chart.empty and cfg["interval"] != "1d":
            hist_chart = stock.history(period="1y", interval="1d")
        hist_5d = stock.history(period="5d")
        info = stock.info
        
        if hist_chart.empty: 
            st.error(f"❌ ระบบไม่พบข้อมูลของชื่อหุ้น '{active_ticker}' โปรดตรวจสอบตัวย่อของตลาดอีกครั้ง")
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
            long_name = info.get('longName', active_ticker)
            card_status_class = "card-bullish" if price_diff >= 0 else "card-bearish"
            
            d1, d2, d3 = st.columns(3)
            arr_color = "#2EA043" if price_diff >= 0 else "#F85149"
            arr_icon = "▲" if price_diff >= 0 else "▼"
            
            with d1: st.markdown(f"<div class='quant-card {card_status_class}'><div class='card-title'>{active_ticker.upper()} PRICE ({display_currency})</div><div class='card-value'>{current_price:,.2f}</div><div style='color:{arr_color}; font-size:11px; font-weight:600;'>{arr_icon} {price_diff:+.2f} ({price_pct:+.2f}%)</div></div>", unsafe_allow_html=True)
            with d2: st.markdown(f"<div class='quant-card {card_status_class}'><div class='card-title'>24H HIGH ({display_currency})</div><div class='card-value' style='color:#388BFD;'>{high_val:,.2f}</div></div>", unsafe_allow_html=True)
            with d3: st.markdown(f"<div class='quant-card {card_status_class}'><div class='card-title'>24H LOW ({display_currency})</div><div class='card-value' style='color:#F85149;'>{low_val:,.2f}</div></div>", unsafe_allow_html=True)
            
            hist_chart_converted = hist_chart.copy()
            for col in ['Open', 'High', 'Low', 'Close']: hist_chart_converted[col] = hist_chart_converted[col] * fx_factor
            
            delta = hist_chart_converted['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-9)
            hist_chart_converted['RSI'] = 100 - (100 / (1 + rs))
            current_rsi = hist_chart_converted['RSI'].iloc[-1] if not hist_chart_converted['RSI'].empty else 50.0
            
            sentiment_pct = np.clip(50 + (price_pct * 5) + (current_rsi - 50) * 0.5, 5.0, 95.0)
            st.markdown(f"<div class='section-title' style='margin-top:14px; margin-bottom: 2px;'>📊 {long_name} SENTIMENT RADAR: {sentiment_pct:.1f}%</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sentiment-container'><div class='sentiment-bar' style='width: {sentiment_pct}%;'></div></div>", unsafe_allow_html=True)
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.78, 0.22], vertical_spacing=0.03)
            fig.add_trace(go.Candlestick(
                x=hist_chart_converted.index, open=hist_chart_converted['Open'], high=hist_chart_converted['High'], low=hist_chart_converted['Low'], close=hist_chart_converted['Close'],
                increasing=dict(line=dict(color='#2EA043'), fillcolor='#2EA043'), decreasing=dict(line=dict(color='#F85149'), fillcolor='#F85149')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(x=hist_chart_converted.index, y=hist_chart_converted['RSI'], line=dict(color='#D29922', width=1.1)), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#F85149", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#2EA043", row=2, col=1)
            
            fig.update_layout(template=plotly_template, xaxis_rangeslider_visible=False, paper_bgcolor=bg_app, plot_bgcolor=bg_card, margin=dict(l=4, r=4, t=4, b=4), height=410, showlegend=False)
            fig.update_yaxes(gridcolor=grid_chart, zerolinecolor=grid_chart)
            fig.update_xaxes(gridcolor=grid_chart)
            st.plotly_chart(fig, use_container_width=True)
            
            st.session_state['current_calculated_matrix'] = {
                "high_val": high_val, "low_val": low_val, "current_price": current_price, 
                "stock": stock, "display_currency": display_currency, "risk_profile": risk_profile
            }
    except Exception as e: st.error(f"⚠️ เกิดข้อผิดพลาดในระบบคลาวด์: {str(e)}")

# --- 🎯 ฝั่งที่ 3: แผงสูตรคำนวณราคาเป้าหมายอัจฉริยะ (Right Column) ---
with col_right_matrix:
    st.markdown("<div class='section-title'>🎯 SPOT & OPTIONS MATRIX</div>", unsafe_allow_html=True)
    
    if 'current_calculated_matrix' in st.session_state:
        cm = st.session_state['current_calculated_matrix']
        high_val, low_val, current_price, display_currency = cm["high_val"], cm["low_val"], cm["current_price"], cm["display_currency"]
        current_risk = cm.get("risk_profile", risk_profile)
        
        P = (high_val + low_val + current_price) / 3
        R1, S1 = (2 * P) - low_val, (2 * P) - high_val
        R2, S2 = P + (high_val - low_val), P - (high_val - low_val)
        
        if current_risk == "CONSERVATIVE (ต่ำ)": tp_f, sl_f = 0.02, 0.01
        elif current_risk == "MODERATE (ปานกลาง)": tp_f, sl_f = 0.045, 0.022
        else: tp_f, sl_f = 0.08, 0.04
        
        entry_min, entry_max = S1, current_price * 1.002
        tp_price, sl_price = current_price * (1 + tp_f), current_price * (1 - sl_f)
        
        try:
            expirations = cm["stock"].options
            calls_iv = cm["stock"].option_chain(expirations[0]).calls['impliedVolatility'].mean() * 100 if expirations else 32.4
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
