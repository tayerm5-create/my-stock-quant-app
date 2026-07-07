import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor
import time

# 1. Page Configuration
st.set_page_config(
    page_title="NEXUS QUANT // TERMINAL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Setup State Memory
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = True
if 'selected_ticker' not in st.session_state:
    st.session_state['selected_ticker'] = "AAPL"

# 3. Premium High-Tech CSS Styling
if st.session_state['dark_mode']:
    bg_app = "#0B0E14"
    bg_card = "#131722"
    border_color = "#2A2E39"
    text_main = "#F0F3FA"
    text_sub = "#848E9C"
    th_bg = "#1C2030"
    plotly_template = "plotly_dark"
    grid_chart = "#1E222D"
    card_hover = "#2962FF"
    sentiment_bg = "#1E222D"
    rank_bg = "rgba(132, 142, 156, 0.1)"
    rank_txt = "#848E9C"
else:
    bg_app = "#F8F9FA"
    bg_card = "#FFFFFF"
    border_color = "#E0E3EB"
    text_main = "#131722"
    text_sub = "#707A8A"
    th_bg = "#F0F3FA"
    plotly_template = "plotly_white"
    grid_chart = "#E0E3EB"
    card_hover = "#2962FF"
    sentiment_bg = "#F0F3FA"
    rank_bg = "rgba(112, 122, 138, 0.1)"
    rank_txt = "#707A8A"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_app}; color: {text_main}; font-family: 'Inter', sans-serif; transition: all 0.3s ease; }}
    .top-config-bar {{ background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 8px; padding: 12px 18px 2px 18px; margin-bottom: 15px; }}
    .section-title {{ font-size: 11px; font-weight: 700; color: {card_hover}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; padding-bottom: 4px; border-bottom: 1px solid {border_color}; }}
    
    .quant-card {{ background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 6px; padding: 10px; text-align: center; transition: all 0.2s ease; }}
    .card-bullish {{ border-top: 3px solid #00E676; }}
    .card-bearish {{ border-top: 3px solid #FF5252; }}
    .quant-card:hover {{ border-color: {card_hover}; transform: translateY(-1px); }}
    .card-title {{ font-size: 9px; color: {text_sub}; font-weight: 600; text-transform: uppercase; margin-bottom: 2px; }}
    .card-value {{ font-size: 18px; font-weight: 700; color: {text_main}; }}
    
    .badge-zone {{ padding: 8px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-bottom: 6px; border: 1px solid; text-align: center; }}
    .zone-buy {{ background-color: rgba(0, 230, 118, 0.04); color: #00E676; border-color: rgba(0, 230, 118, 0.15); }}
    .zone-tp {{ background-color: rgba(255, 214, 0, 0.04); color: #FFD600; border-color: rgba(255, 214, 0, 0.15); }}
    .zone-sl {{ background-color: rgba(255, 82, 82, 0.04); color: #FF5252; border-color: rgba(255, 82, 82, 0.15); }}
    
    .rank-box-container {{ background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 6px; margin-bottom: 6px; padding: 2px 10px; transition: all 0.2s ease; display: block; position: relative; }}
    .rank-box-container:hover {{ border-color: {card_hover}; }}
    .active-row-fx {{ border-color: {card_hover} !important; background-color: rgba(41, 98, 255, 0.04) !important; }}
    
    div.stButton > button {{ background-color: transparent !important; color: {text_main} !important; border: none !important; padding: 6px 0px !important; width: 100% !important; text-align:
