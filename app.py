"""
app.py — Main entry point for BIS Standard Finder
Run: python3 -m streamlit run app.py
"""
import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(
    page_title="BIS Standard Finder",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

# Redirect to home page
st.switch_page("pages/1_🏠_Home.py")