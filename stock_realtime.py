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
    st.session_state['selected_ticker'] = "AAPL" # หุ้นเริ่มต้นสำหรับการเปิดหน้าแรก

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
    rank_bg = "rgba(139, 148, 158, 0.08)"; rank_txt = "#8B949E"
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
    rank_bg = "rgba(87, 96, 106, 0.08)"; rank_txt = "#57606A"

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
    
    .rank-box-wrapper {{ background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 8px; margin-bottom: 8px; transition: all 0.2s ease; display: block; position: relative; }}
    .rank-box-wrapper:hover {{ border-color: {card_hover}; transform: scale(1.01); }}
    .active-row-fx {{ border-color: {card_hover} !important; background-color: rgba(88, 166, 255, 0.02) !important; }}
    
    .rank-badge {{ display: flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 4px; font-size: 10px; font-weight: 700; margin-right: 12px; background-color: {rank_bg}; color: {rank_txt}; }}
    .ticker-name {{ font-size: 13px; font-weight: 700; color:
