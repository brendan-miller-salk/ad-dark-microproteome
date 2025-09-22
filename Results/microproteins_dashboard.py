import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import webbrowser
from urllib.parse import quote
import numpy as np

# Set page config
st.set_page_config(
    page_title="Brain Microproteins Dashboard",
    page_icon="brain",
    layout="wide"
)

# Define color scheme from the figure
COLORS = {
    'swiss_prot': '#74a2b7',      # Blue for canonical/Swiss-Prot
    'noncanonical': '#ed8651',    # Orange for noncanonical/Salk/TrEMBL
    'background': '#f8f9fa',
    'text_light': '#2c3e50',      # Dark text for light mode
    'text_dark': '#ffffff'        # White text for dark mode
}

# Enhanced CSS with darker, high-contrast design for better readability
st.markdown(f"""
<style>
/* Force dark theme for EVERYTHING including Streamlit header */
.stApp, .main, header, .stAppHeader, [data-testid="stHeader"] {{
    background: #1a202c !important;
}}

/* Target the top toolbar/header area specifically */
.stApp > header {{
    background: #1a202c !important;
}}

.stApp > header [data-testid="stToolbar"] {{
    background: #1a202c !important;
}}

/* Force dark gradient background for entire app */
.stApp {{
    background: linear-gradient(135deg, 
        rgba(26, 32, 44, 1) 0%, 
        rgba(45, 55, 72, 0.98) 25%,
        rgba(26, 32, 44, 0.95) 50%,
        rgba(45, 55, 72, 0.98) 75%,
        rgba(26, 32, 44, 1) 100%) !important;
    min-height: 100vh !important;
}}

/* Dark main content with strong contrast */
.main .block-container {{
    background: rgba(26, 32, 44, 0.85) !important;
    backdrop-filter: blur(8px) !important;
    border-radius: 15px !important;
    padding: 2rem !important;
    margin-top: 1rem !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(116, 162, 183, 0.3) !important;
    color: #ffffff !important;
}}

/* Override Streamlit's default variables for dark theme */
:root {{
    --text-color: #ffffff;
    --bg-color: rgba(26, 32, 44, 0.8);
    --border-color: rgba(116, 162, 183, 0.3);
    --primary-color: {COLORS['swiss_prot']};
    --background-color: rgba(26, 32, 44, 0.9);
}}

/* Light mode override - force dark theme always */
@media (prefers-color-scheme: light) {{
    :root {{
        --text-color: #ffffff;
        --bg-color: rgba(26, 32, 44, 0.8);
        --border-color: rgba(116, 162, 183, 0.3);
        --background-color: rgba(26, 32, 44, 0.9);
    }}
}}

/* Dark mode enhancement */
@media (prefers-color-scheme: dark) {{
    :root {{
        --text-color: #ffffff;
        --bg-color: rgba(26, 32, 44, 0.9);
        --border-color: rgba(116, 162, 183, 0.4);
        --background-color: rgba(26, 32, 44, 0.95);
    }}
}}

/* Force white text visibility for all elements */
*, div, span, p, h1, h2, h3, h4, h5, h6, label, button, .stMarkdown, .stText {{
    color: #ffffff !important;
}}

/* Remove all light backgrounds from Streamlit containers */
.stApp > div:first-child {{
    background: transparent !important;
}}

.stApp > div:first-child > div {{
    background: transparent !important;
}}

/* Main content area - dark glass effect */
.main .block-container {{
    background: rgba(26, 32, 44, 0.85) !important;
    backdrop-filter: blur(8px) !important;
    color: #ffffff !important;
    padding-top: 2rem !important;
    border: 1px solid rgba(116, 162, 183, 0.4) !important;
}}

/* Dark all section containers */
section[data-testid="stSidebar"] > div {{
    background: transparent !important;
}}

.stApp section {{
    background: transparent !important;
}}

/* Fix any remaining light containers */
.element-container {{
    background: transparent !important;
}}

div[data-testid="stVerticalBlock"] {{
    background: transparent !important;
}}

div[data-testid="stHorizontalBlock"] {{
    background: transparent !important;
}}

/* Main header */
.main-header {{
    font-size: 1.8rem;
    font-weight: 700;
    color: {COLORS['text_dark']} !important;
    text-align: center;
    margin-bottom: 0.75rem;
    padding: 0.75rem 1rem;
    background: linear-gradient(90deg, {COLORS['swiss_prot']}80 0%, {COLORS['noncanonical']}80 100%);
    border-radius: 10px;
    line-height: 1.3;
}}

/* Analysis cards - dark theme with high contrast */
.analysis-card {{
    background: rgba(26, 32, 44, 0.9) !important;
    backdrop-filter: blur(8px) !important;
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
    margin: 0.5rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #ffffff !important;
}}

.analysis-card:hover {{
    border: 1px solid rgba(237, 134, 81, 0.8) !important;
    transform: translateX(3px);
    background: rgba(237, 134, 81, 0.2) !important;
    box-shadow: 0 6px 20px rgba(237, 134, 81, 0.4) !important;
}}

.analysis-card.selected {{
    border: 1px solid rgba(237, 134, 81, 0.7) !important;
    background: rgba(237, 134, 81, 0.25) !important;
}}

/* Badges */
.swiss-prot-badge {{
    background: {COLORS['swiss_prot']};
    color: white !important;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
}}

.noncanonical-badge {{
    background: {COLORS['noncanonical']};
    color: white !important;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
}}

/* Stat cards - glass morphism */
.stat-card {{
    flex: 1;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 12px;
    border: 1px solid rgba(116, 162, 183, 0.3) !important;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    color: var(--text-color) !important;
}}

/* UCSC buttons */
.ucsc-button {{
    background: {COLORS['swiss_prot']} !important;
    color: white !important;
    padding: 5px 10px;
    border-radius: 5px;
    text-decoration: none;
    font-weight: bold;
    display: inline-block;
    margin: 2px;
}}

.ucsc-button:hover {{
    background: {COLORS['noncanonical']} !important;
    color: white !important;
    text-decoration: none;
}}

/* Streamlit component styling - enhanced dark theme with navy backgrounds */
.stSelectbox > div > div {{
    background: #1a212d !important;
    backdrop-filter: blur(5px) !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}}

.stSelectbox select {{
    background: #1a212d !important;
    color: #ffffff !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
}}

/* Text input fields - navy background */
.stTextInput > div > div > input {{
    background: #1a212d !important;
    backdrop-filter: blur(5px) !important;
    color: #ffffff !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
    border-radius: 8px !important;
}}

.stTextInput > div > div > input::placeholder {{
    color: rgba(255, 255, 255, 0.6) !important;
}}

/* Number input fields - navy background with comprehensive selectors */
.stNumberInput > div > div > input,
.stNumberInput input,
input[type="number"] {{
    background: #1a212d !important;
    backdrop-filter: blur(5px) !important;
    color: #ffffff !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
    border-radius: 8px !important;
}}

.stNumberInput > div > div > input::placeholder,
.stNumberInput input::placeholder,
input[type="number"]::placeholder {{
    color: rgba(255, 255, 255, 0.6) !important;
}}

/* Additional number input container styling */
.stNumberInput > div {{
    background: transparent !important;
}}

.stNumberInput > div > div {{
    background: #1a212d !important;
    border-radius: 8px !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
}}

/* Number input step buttons */
.stNumberInput button {{
    background: #2d5a87 !important;
    color: #ffffff !important;
    border: none !important;
}}

.stNumberInput button:hover {{
    background: #3a6b98 !important;
    color: #ffffff !important;
}}

/* Multiselect components - navy background */
.stMultiSelect > div > div {{
    background: #1a212d !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}}

.stMultiSelect > div > div > div {{
    background: #1a212d !important;
    color: #ffffff !important;
}}

/* Multiselect dropdown menu */
.stMultiSelect > div > div > div[data-baseweb="select"] > div {{
    background: #1a212d !important;
    color: #ffffff !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
}}

/* Multiselect options in dropdown */
.stMultiSelect > div > div > div[data-baseweb="select"] li {{
    background: #1a212d !important;
    color: #ffffff !important;
}}

.stMultiSelect > div > div > div[data-baseweb="select"] li:hover {{
    background: #394254 !important;
    color: #ffffff !important;
}}

/* Selected tags in multiselect */
.stMultiSelect > div > div > div[data-baseweb="select"] > div > div > span {{
    background: rgba(116, 162, 183, 0.8) !important;
    color: #ffffff !important;
    border-radius: 4px !important;
}}

/* Input focus states */
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
input[type="number"]:focus {{
    border: 2px solid {COLORS['swiss_prot']} !important;
    outline: none !important;
    background: #1b212d !important;
    color: #ffffff !important;
}}

/* Comprehensive input styling - catch all Streamlit inputs */
.stApp input[type="number"],
.stApp input[type="text"] {{
    background: #1a212d !important;
    color: #ffffff !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
    border-radius: 8px !important;
}}

.stApp input[type="number"]:focus,
.stApp input[type="text"]:focus {{
    background: #1b212d !important;
    border: 2px solid {COLORS['swiss_prot']} !important;
    color: #ffffff !important;
}}

/* Radio button styling */
.stRadio > div {{
    background: #1a212d !important;
    backdrop-filter: blur(5px) !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
    margin-bottom: 0.5rem !important;
    border: 1px solid rgba(116, 162, 183, 0.3) !important;
}}

.stRadio > div > label {{
    color: #ffffff !important;
}}

/* All input labels - ensure white text */
.stTextInput label,
.stNumberInput label,
.stMultiSelect label,
.stSelectbox label,
.stRadio label {{
    color: #ffffff !important;
    font-weight: 500 !important;
}}

.stTextInput label {{
    color: #ffffff !important;
}}

.stRadio > div {{
    background: rgba(26, 32, 44, 0.7) !important;
    backdrop-filter: blur(5px) !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
    margin-bottom: 0.5rem !important;
    border: 1px solid rgba(116, 162, 183, 0.3) !important;
}}

.stButton > button {{
    background: #1a212d !important;
    backdrop-filter: blur(5px) !important;
    color: #ffffff !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}}

.stButton > button:hover {{
    background: #394254 !important;
    color: #ffffff !important;
    border: 1px solid {COLORS['swiss_prot']} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(116, 162, 183, 0.3) !important;
}}

/* Download button specific styling */
.stDownloadButton > button {{
    background: linear-gradient(45deg, {COLORS['swiss_prot']}, {COLORS['noncanonical']}) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}}

.stDownloadButton > button:hover {{
    background: linear-gradient(45deg, {COLORS['noncanonical']}, {COLORS['swiss_prot']}) !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(237, 134, 81, 0.4) !important;
}}

/* Metrics - refined elegance */
[data-testid="metric-container"] {{
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(3px) !important;
    border: 1px solid rgba(116, 162, 183, 0.2) !important;
    border-radius: 10px !important;
    color: var(--text-color) !important;
}}

[data-testid="metric-container"] * {{
    color: var(--text-color) !important;
}}

/* Custom colored metrics - more subtle */
.metric-swiss-prot {{
    background: rgba(116, 162, 183, 0.12) !important;
    backdrop-filter: blur(5px) !important;
    border: 2px solid rgba(116, 162, 183, 0.4) !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
    box-shadow: 0 4px 15px rgba(116, 162, 183, 0.15) !important;
}}

.metric-swiss-prot [data-testid="metric-value"] {{
    color: {COLORS['swiss_prot']} !important;
    font-weight: bold !important;
    font-size: 2rem !important;
}}

.metric-noncanonical {{
    background: rgba(237, 134, 81, 0.12) !important;
    backdrop-filter: blur(5px) !important;
    border: 2px solid rgba(237, 134, 81, 0.4) !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
    box-shadow: 0 4px 15px rgba(237, 134, 81, 0.15) !important;
}}

.metric-noncanonical [data-testid="metric-value"] {{
    color: {COLORS['noncanonical']} !important;
    font-weight: bold !important;
    font-size: 2rem !important;
}}

.metric-total {{
    background: linear-gradient(135deg, rgba(116, 162, 183, 0.1) 0%, rgba(237, 134, 81, 0.1) 100%) !important;
    backdrop-filter: blur(5px) !important;
    border: 2px solid rgba(116, 162, 183, 0.5) !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
    box-shadow: 0 4px 15px rgba(116, 162, 183, 0.2) !important;
}}

.metric-total [data-testid="metric-value"] {{
    background: linear-gradient(135deg, {COLORS['swiss_prot']} 0%, {COLORS['noncanonical']} 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: bold !important;
    font-size: 2rem !important;
}}

/* Expander - glass morphism */
.streamlit-expanderHeader {{
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(10px) !important;
    color: var(--text-color) !important;
    border: 1px solid rgba(116, 162, 183, 0.3) !important;
    border-radius: 10px !important;
}}

.streamlit-expanderContent {{
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    color: var(--text-color) !important;
    border: 1px solid rgba(116, 162, 183, 0.2) !important;
    border-radius: 0 0 10px 10px !important;
}}

/* Dataframe container */
.stDataFrame {{
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(116, 162, 183, 0.2) !important;
    color: var(--text-color) !important;
}}

/* Dark navy blue table styling - AGGRESSIVE OVERRIDE */
.stDataFrame table,
.stDataFrame .dataframe,
div[data-testid="stDataFrame"] table,
div[data-testid="stDataFrame"] .dataframe,
.stDataFrame div[data-testid="stDataFrameResizable"] table,
.element-container .stDataFrame table {{
    background: #1a212d !important; /* Dark navy blue */
    border-radius: 8px !important;
    overflow: hidden !important;
}}

/* Force all table elements to have dark navy background */
.stDataFrame table *,
.stDataFrame .dataframe *,
div[data-testid="stDataFrame"] table *,
div[data-testid="stDataFrame"] .dataframe *,
.stDataFrame div[data-testid="stDataFrameResizable"] table * {{
    background: #1a212d !important;
    color: #ffffff !important;
}}

/* Table headers - slightly lighter navy with maximum specificity */
.stDataFrame table thead th,
.stDataFrame .dataframe thead th,
div[data-testid="stDataFrame"] table thead th,
div[data-testid="stDataFrame"] .dataframe thead th,
.stDataFrame div[data-testid="stDataFrameResizable"] table thead th,
.element-container .stDataFrame table thead th {{
    background: #2a4a70 !important; /* Lighter navy for headers */
    color: #ffffff !important;
    border-bottom: 2px solid #74a2b7 !important;
    padding: 12px 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}}

/* Table body cells - dark navy with white text - MAXIMUM SPECIFICITY */
.stDataFrame table tbody td,
.stDataFrame .dataframe tbody td,
div[data-testid="stDataFrame"] table tbody td,
div[data-testid="stDataFrame"] .dataframe tbody td,
.stDataFrame div[data-testid="stDataFrameResizable"] table tbody td,
.element-container .stDataFrame table tbody td,
.stDataFrame table tbody tr td,
.stDataFrame .dataframe tbody tr td,
div[data-testid="stDataFrame"] table tbody tr td {{
    background: #1a212d !important; /* Dark navy blue */
    color: #ffffff !important;
    border-bottom: 1px solid rgba(116, 162, 183, 0.3) !important;
    padding: 10px 8px !important;
    font-size: 0.85rem !important;
}}

/* Alternating row colors for better readability - FORCE OVERRIDE */
.stDataFrame table tbody tr:nth-child(even) td,
.stDataFrame .dataframe tbody tr:nth-child(even) td,
div[data-testid="stDataFrame"] table tbody tr:nth-child(even) td,
div[data-testid="stDataFrame"] .dataframe tbody tr:nth-child(even) td,
.stDataFrame div[data-testid="stDataFrameResizable"] table tbody tr:nth-child(even) td {{
    background: #1b212d !important; /* Slightly darker navy for even rows */
    color: #ffffff !important;
}}

.stDataFrame table tbody tr:nth-child(odd) td,
.stDataFrame .dataframe tbody tr:nth-child(odd) td,
div[data-testid="stDataFrame"] table tbody tr:nth-child(odd) td,
div[data-testid="stDataFrame"] .dataframe tbody tr:nth-child(odd) td,
.stDataFrame div[data-testid="stDataFrameResizable"] table tbody tr:nth-child(odd) td {{
    background: #1a212d !important; /* Standard navy for odd rows */
    color: #ffffff !important;
}}

/* Hover effects for table rows - MAXIMUM FORCE */
.stDataFrame table tbody tr:hover td,
.stDataFrame .dataframe tbody tr:hover td,
div[data-testid="stDataFrame"] table tbody tr:hover td,
div[data-testid="stDataFrame"] .dataframe tbody tr:hover td,
.stDataFrame div[data-testid="stDataFrameResizable"] table tbody tr:hover td {{
    background: #394254 !important; /* Lighter navy on hover */
    color: #ffffff !important;
    transition: background 0.2s ease !important;
}}

/* Override ANY Streamlit default table styling */
[data-testid="stDataFrame"] {{
    background: #1a212d !important;
}}

[data-testid="stDataFrame"] > div {{
    background: #1a212d !important;
}}

/* Force white text EVERYWHERE in the dataframe */
.stDataFrame,
.stDataFrame *,
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] *,
.stDataFrame table,
.stDataFrame table *,
.stDataFrame .dataframe,
.stDataFrame .dataframe *,
div[data-testid="stDataFrame"] table,
div[data-testid="stDataFrame"] table *,
.stDataFrame div[data-testid="stDataFrameResizable"],
.stDataFrame div[data-testid="stDataFrameResizable"] * {{
    color: #ffffff !important;
}}

/* Selected/active cell styling */
.stDataFrame table td:focus,
.stDataFrame .dataframe td:focus,
div[data-testid="stDataFrame"] table td:focus {{
    outline: 2px solid #74a2b7 !important;
    outline-offset: -2px !important;
}}

/* Ensure all text in table is white */
.stDataFrame table,
.stDataFrame table *,
.stDataFrame .dataframe,
.stDataFrame .dataframe *,
div[data-testid="stDataFrame"] table,
div[data-testid="stDataFrame"] table * {{
    color: #ffffff !important;
}}

/* Special styling for classification badges in table */
.stDataFrame table tbody td:first-child,
.stDataFrame .dataframe tbody td:first-child,
div[data-testid="stDataFrame"] table tbody td:first-child {{
    font-weight: 600 !important;
    text-align: center !important;
}}

/* Link styling in table */
.stDataFrame table a,
.stDataFrame .dataframe a,
div[data-testid="stDataFrame"] table a {{
    color: #74a2b7 !important;
    text-decoration: underline !important;
}}

.stDataFrame table a:hover,
.stDataFrame .dataframe a:hover,
div[data-testid="stDataFrame"] table a:hover {{
    color: #ed8651 !important;
    text-decoration: none !important;
}}

/* Info, success, error boxes */
.stAlert {{
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(10px) !important;
    color: var(--text-color) !important;
    border-radius: 10px !important;
}}

/* Analysis Hub Header */
.analysis-hub-header {{
    background: linear-gradient(135deg, {COLORS['swiss_prot']} 0%, {COLORS['noncanonical']} 100%);
    padding: 1.5rem 1rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}

.analysis-hub-icon {{
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    display: block;
}}

.analysis-hub-title {{
    color: white !important;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    margin-bottom: 0.3rem;
}}

.analysis-hub-subtitle {{
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 1rem;
    font-weight: 400;
    margin: 0;
}}

/* Enhanced sidebar styling - dark theme */
.stSidebar > div:first-child {{
    background: linear-gradient(180deg, 
        rgba(26, 32, 44, 0.95) 0%, 
        rgba(45, 55, 72, 0.95) 50%,
        rgba(26, 32, 44, 0.95) 100%) !important;
    backdrop-filter: blur(10px) !important;
    padding: 1rem !important;
    border-right: 1px solid rgba(116, 162, 183, 0.4) !important;
}}

/* Sidebar content */
.stSidebar .element-container {{
    background: transparent !important;
    color: #ffffff !important;
}}

.stSidebar .stMarkdown {{
    color: #ffffff !important;
}}

/* Remove any remaining light from sidebar */
.css-1d391kg {{
    background: transparent !important;
    color: #ffffff !important;
}}

.sidebar .sidebar-content {{
    background: transparent !important;
    color: #ffffff !important;
}}

/* Analysis selection styling - dark theme */
.analysis-selection-container {{
    background: rgba(26, 32, 44, 0.8) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
    border: 1px solid rgba(116, 162, 183, 0.4) !important;
    backdrop-filter: blur(8px) !important;
}}

/* Enhanced legend styling - dark theme */
.legend-container {{
    background: rgba(26, 32, 44, 0.8) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin-top: 1rem !important;
    border: 1px solid rgba(116, 162, 183, 0.4) !important;
    backdrop-filter: blur(8px) !important;
}}

/* Enhanced sidebar radio buttons - dark theme */
.stRadio > div {{
    background: rgba(26, 32, 44, 0.7) !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}}

.stRadio > div > label {{
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    margin-bottom: 0.25rem !important;
    transition: all 0.3s ease !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
    color: #ffffff !important;
}}

.stRadio > div > label:hover {{
    background: rgba(116, 162, 183, 0.3) !important;
    border: 1px solid rgba(116, 162, 183, 0.6) !important;
    transform: translateX(3px) !important;
}}

.stRadio > div > label[data-checked="true"] {{
    background: linear-gradient(90deg, rgba(116, 162, 183, 0.4) 0%, rgba(237, 134, 81, 0.4) 100%) !important;
    border: 1px solid {COLORS['swiss_prot']} !important;
    font-weight: bold !important;
}}

/* Enhanced legend styling - dark theme */
.legend-container {{
    background: rgba(26, 32, 44, 0.8) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin-top: 1rem !important;
    border: 1px solid rgba(116, 162, 183, 0.4) !important;
    backdrop-filter: blur(8px) !important;
}}

/* Hover effects for Analysis Hub */
.analysis-hub-header:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}}

/* Info card styling */
.info-card {{
    background: rgba(26, 32, 44, 0.95) !important;
    border: 1px solid rgba(116, 162, 183, 0.5) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    margin: 0.75rem 0 !important;
    backdrop-filter: blur(8px) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    border-left: 3px solid {COLORS['swiss_prot']} !important;
}}

.info-card strong {{
    color: #ffffff !important;
    font-weight: 600 !important;
}}

.info-card code {{
    background: rgba(116, 162, 183, 0.25) !important;
    color: #ffffff !important;
    padding: 0.3rem 0.5rem !important;
    border-radius: 4px !important;
    font-family: 'Courier New', monospace !important;
    border: 1px solid rgba(116, 162, 183, 0.4) !important;
    font-weight: 500 !important;
    font-size: 0.9em !important;
}}

/* Dataframe */
.stDataFrame {{
    color: var(--text-color) !important;
}}

/* Info, success, error boxes */
.stAlert {{
    color: var(--text-color) !important;
}}

/* Markdown content */
.stMarkdown {{
    color: var(--text-color) !important;
}}

/* Force white text for all elements - dark theme enforcement */
body, .main, .block-container, .stApp {{
    color: #ffffff !important;
}}

/* Ensure Streamlit components inherit white text */
.stSelectbox, .stTextInput, .stRadio, .stButton, .stMetric {{
    color: #ffffff !important;
}}

/* Override any conflicting Streamlit Cloud styles with dark theme */
.stApp .main .block-container {{
    background: rgba(26, 32, 44, 0.85) !important;
    color: #ffffff !important;
}}

/* FIX THREE DOTS COLUMN MENU - The dropdown that appears when clicking ⋮ */
/* Target the dropdown menu that appears when clicking column three dots */
[data-testid*="stDataFrameColsort"],
[data-testid*="column-sort"],
[data-testid*="dataframe-toolbar"],
.column-header-menu,
.dataframe-column-menu,
.stDataFrame .column-menu,
div[data-testid="stDataFrame"] .column-menu {{
    background: #1a202c !important;
    color: #ffffff !important;
    border: 1px solid #74a2b7 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.8) !important;
}}

/* Menu items inside the three dots dropdown */
[data-testid*="stDataFrameColsort"] *,
[data-testid*="column-sort"] *,
[data-testid*="dataframe-toolbar"] *,
.column-header-menu *,
.dataframe-column-menu *,
.stDataFrame .column-menu *,
div[data-testid="stDataFrame"] .column-menu * {{
    color: #ffffff !important;
    background: transparent !important;
}}

/* Specific menu options like "Sort ascending", "Sort descending" */
.sort-option,
.menu-item,
.dropdown-item,
[role="menuitem"],
[role="option"] {{
    color: #ffffff !important;
    background: #1a202c !important;
}}

.sort-option:hover,
.menu-item:hover,
.dropdown-item:hover,
[role="menuitem"]:hover,
[role="option"]:hover {{
    color: #ffffff !important;
    background: #2d3748 !important;
}}

/* Any popover or dropdown that appears from dataframe */
[data-baseweb="popover"],
[data-baseweb="menu"],
.stPopover,
.streamlit-menu {{
    background: #1a202c !important;
    color: #ffffff !important;
    border: 1px solid #74a2b7 !important;
}}

[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
.stPopover *,
.streamlit-menu * {{
    color: #ffffff !important;
}}

/* Enhanced tooltip styling for better visibility */
[title]:hover::after {{
    content: attr(title);
    position: absolute;
    bottom: -25px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(26, 32, 44, 0.95) !important;
    color: #ffffff !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    border: 1px solid rgba(116, 162, 183, 0.6) !important;
    font-size: 0.85rem !important;
    white-space: nowrap !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6) !important;I
    backdrop-filter: blur(8px) !important;
    z-index: 9999 !important;
    pointer-events: none !important;
}}

/* Ensure dataframe tooltips are visible */
.stDataFrame [title] {{
    position: relative !important;
}}

.stDataFrame [title]:hover {{
    background: rgba(116, 162, 183, 0.1) !important;
}}

/* Custom tooltip for better contrast */
.tooltip {{
    position: relative !important;
    display: inline-block !important;
    cursor: help !important;
}}

.tooltip .tooltip-text {{
    visibility: hidden !important;
    width: 220px !important;
    background: rgba(26, 32, 44, 0.98) !important;
    color: #ffffff !important;
    text-align: center !important;
    border-radius: 8px !important;
    border: 1px solid rgba(116, 162, 183, 0.7) !important;
    padding: 8px 12px !important;
    position: absolute !important;
    z-index: 9999 !important;
    bottom: 125% !important;
    left: 50% !important;
    margin-left: -110px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7) !important;
    backdrop-filter: blur(10px) !important;
    font-size: 0.85rem !important;
    line-height: 1.3 !important;
}}

.tooltip .tooltip-text::after {{
    content: "" !important;
    position: absolute !important;
    top: 100% !important;
    left: 50% !important;
    margin-left: -5px !important;
    border-width: 5px !important;
    border-style: solid !important;
    border-color: rgba(26, 32, 44, 0.98) transparent transparent transparent !important;
}}

.tooltip:hover .tooltip-text {{
    visibility: visible !important;
    opacity: 1 !important;
    transition: opacity 0.3s ease !important;
}}

/* Ensure tooltips work properly in dataframes */
.stDataFrame table th, .stDataFrame table td {{
    position: relative !important;
}}

/* Force browser tooltip background and text color */
[title] {{
    position: relative !important;
}}

/* Alternative approach - add a custom data attribute for tooltips */
[data-tooltip]:hover::before {{
    content: attr(data-tooltip) !important;
    position: absolute !important;
    background: rgba(26, 32, 44, 0.98) !important;
    color: #ffffff !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    border: 1px solid rgba(116, 162, 183, 0.7) !important;
    font-size: 0.85rem !important;
    white-space: nowrap !important;
    z-index: 9999 !important;
    bottom: 100% !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    margin-bottom: 5px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7) !important;
    backdrop-filter: blur(10px) !important;
    pointer-events: none !important;
}}

/* COMPLETELY DISABLE ALL BROWSER TOOLTIPS */
* {{
    -webkit-touch-callout: none !important;
    -webkit-user-select: none !important;
    -khtml-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
    user-select: none !important;
}}

/* Remove all title attributes to prevent browser tooltips */
[title] {{
    position: relative !important;
}}

[title]:hover {{
    /* Disable browser tooltip completely */
    title: "" !important;
}}

/* JavaScript-powered custom tooltips */
.custom-tooltip {{
    position: fixed !important;
    background: #1a202c !important;
    color: #ffffff !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    border: 2px solid #74a2b7 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8) !important;
    z-index: 999999 !important;
    pointer-events: none !important;
    opacity: 1 !important;
    display: block !important;
    visibility: visible !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}

/* Fallback CSS tooltips with ::after */
table thead th[title]:hover::after,
.stDataFrame table thead th[title]:hover::after,
.stDataFrame .dataframe thead th[title]:hover::after,
div[data-testid="stDataFrame"] table thead th[title]:hover::after,
div[data-testid="stDataFrame"] .dataframe thead th[title]:hover::after,
div[data-testid="stDataFrame"] thead th[title]:hover::after,
.element-container table thead th[title]:hover::after,
.stDataFrame th[title]:hover::after,
.dataframe th[title]:hover::after,
th[title]:hover::after,
[data-testid="stDataFrame"] th[title]:hover::after {{
    content: attr(title) !important;
    position: fixed !important;
    top: 50px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background: #1a202c !important;
    color: #ffffff !important;
    padding: 12px 16px !important;
    border-radius: 8px !important;
    border: 2px solid #74a2b7 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.9) !important;
    z-index: 999999 !important;
    pointer-events: none !important;
    opacity: 1 !important;
    display: block !important;
    visibility: visible !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}

/* Hover effects for table headers */
table thead th[title]:hover,
.stDataFrame table thead th[title]:hover,
.stDataFrame .dataframe thead th[title]:hover,
div[data-testid="stDataFrame"] table thead th[title]:hover,
div[data-testid="stDataFrame"] .dataframe thead th[title]:hover,
div[data-testid="stDataFrame"] thead th[title]:hover,
.element-container table thead th[title]:hover,
.stDataFrame th[title]:hover,
.dataframe th[title]:hover,
th[title]:hover,
[data-testid="stDataFrame"] th[title]:hover {{
    cursor: pointer !important;
    background: rgba(116, 162, 183, 0.3) !important;
    transition: background 0.2s ease !important;
}}
</style>

<script>
// JavaScript to completely disable browser tooltips and create custom ones
document.addEventListener('DOMContentLoaded', function() {{
    // Remove all title attributes and create custom tooltips
    function setupCustomTooltips() {{
        const elementsWithTitle = document.querySelectorAll('[title]');
        
        elementsWithTitle.forEach(element => {{
            const titleText = element.getAttribute('title');
            element.removeAttribute('title'); // Remove to prevent browser tooltip
            element.setAttribute('data-custom-title', titleText);
            
            let tooltip = null;
            
            element.addEventListener('mouseenter', function(e) {{
                // Create custom tooltip
                tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = titleText;
                tooltip.style.left = e.pageX + 'px';
                tooltip.style.top = (e.pageY - 40) + 'px';
                document.body.appendChild(tooltip);
            }});
            
            element.addEventListener('mouseleave', function() {{
                if (tooltip) {{
                    tooltip.remove();
                    tooltip = null;
                }}
            }});
            
            element.addEventListener('mousemove', function(e) {{
                if (tooltip) {{
                    tooltip.style.left = e.pageX + 'px';
                    tooltip.style.top = (e.pageY - 40) + 'px';
                }}
            }});
        }});
    }}
    
    // Run initially
    setupCustomTooltips();
    
    // Re-run when Streamlit updates the DOM
    const observer = new MutationObserver(function() {{
        setupCustomTooltips();
    }});
    
    observer.observe(document.body, {{
        childList: true,
        subtree: true
    }});
}});
</script>
""", unsafe_allow_html=True)

def load_analysis_results():
    """Load all analysis result files"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    # Results should be in the same directory as this script
    base_path = script_dir
    
    analysis_files = {
        "Annotation Summary": {
            "path": base_path / "Annotations" / "Brain_Microproteins_Discovery_summary.csv",
            "description": "Noncanonical microprotein discoveries (Salk/TrEMBL only)",
            "icon": "",
            "type": "noncanonical_only"
        },
        "Proteomics (TMT)": {
            "path": base_path / "Proteomics" / "Proteomics_Results_summary.csv", 
            "description": "Mass spectrometry protein evidence (Canonical + Noncanonical)",
            "icon": "⚗️",
            "type": "mixed"
        },
        "Proteomics + RiboSeq (RP3)": {
            "path": base_path / "RP3" / "RP3_Results_summary.csv",
            "description": "Ribosome profiling translation validation (Noncanonical only)", 
            "icon": "🔄",
            "type": "noncanonical_only"
        },
        "Short-Read RNA in AD": {
            "path": base_path / "Transcriptomics" / "Short-Read_Transcriptomics_Results_summary.csv",
            "description": "Short-read RNA-seq differential expression (Canonical + Noncanonical)",
            "icon": "",
            "type": "mixed"
        },
        "Long-Read RNA in AD": {
            "path": base_path / "Transcriptomics" / "Long-Read_Transcriptomics_Results_summary.csv",
            "description": "Long-read RNA-seq analysis (Noncanonical only)",
            "icon": "📜",
            "type": "noncanonical_only"
        },
        "scRNA Enrichment": {
            "path": base_path / "scRNA_Enrichment" / "scRNA_Enrichment_summary.csv",
            "description": "Single-cell RNA-seq cell-type analysis",
            "icon": "",
            "type": "scrna"
        },
        "ShortStop Classification": {
            "path": base_path / "Annotations" / "ShortStop_Microproteins_summary.csv",
            "description": "ShortStop analysis for actively translated small ORFs and microproteins",
            "icon": "🎯",
            "type": "noncanonical_only"
        }
    }
    
    return analysis_files

@st.cache_data
def load_and_merge_all_data():
    """Load and merge all CSV files by sequence to create unified database"""
    analysis_files = load_analysis_results()
    
    # Initialize master dataframe with sequences
    master_df = pd.DataFrame()
    
    for analysis_name, info in analysis_files.items():
        if info['path'].exists():
            try:
                df = pd.read_csv(info['path'], low_memory=False)
                
                # Standardize sequence column name
                if 'Microprotein Sequence' in df.columns:
                    df = df.rename(columns={'Microprotein Sequence': 'sequence'})
                elif 'sequence' not in df.columns:
                    continue  # Skip if no sequence column
                
                # Add source information
                df[f'{analysis_name}_present'] = True
                
                # Rename columns to be analysis-specific to avoid conflicts
                analysis_prefix = analysis_name.replace(' ', '_').replace('(', '').replace(')', '').replace('+', '_')
                cols_to_rename = {}
                
                for col in df.columns:
                    if col not in ['sequence', 'CLICK_UCSC']:  # Keep these common
                        if col not in [f'{analysis_name}_present']:  # Don't rename the presence flag
                            new_col_name = f"{analysis_prefix}_{col}"
                            cols_to_rename[col] = new_col_name
                
                df = df.rename(columns=cols_to_rename)
                
                # Merge with master dataframe
                if master_df.empty:
                    master_df = df.copy()
                else:
                    master_df = pd.merge(master_df, df, on='sequence', how='outer', suffixes=('', '_dup'))
                    
                    # Remove duplicate columns
                    dup_cols = [col for col in master_df.columns if col.endswith('_dup')]
                    master_df = master_df.drop(columns=dup_cols)
                    
            except Exception as e:
                st.warning(f"Could not load {analysis_name}: {e}")
                continue
    
    # Fill NaN values for presence flags
    presence_cols = [col for col in master_df.columns if col.endswith('_present')]
    for col in presence_cols:
        master_df[col] = master_df[col].fillna(False)
    
    # Remove duplicate sequences, keeping the row with the most non-null values
    if not master_df.empty and 'sequence' in master_df.columns:
        # Calculate non-null count for each row (excluding sequence and presence columns)
        data_cols = [col for col in master_df.columns if col != 'sequence' and not col.endswith('_present')]
        master_df['_data_completeness'] = master_df[data_cols].notna().sum(axis=1)
        
        # Sort by data completeness (descending) and keep first occurrence of each sequence
        master_df = master_df.sort_values(['sequence', '_data_completeness'], ascending=[True, False])
        master_df = master_df.drop_duplicates(subset=['sequence'], keep='first')
        
        # Remove the temporary column
        master_df = master_df.drop('_data_completeness', axis=1)
    
    return master_df

def extract_unified_fields(master_df):
    """Extract and unify key fields from the merged dataset"""
    unified_data = master_df.copy()
    
    # Extract Parent Gene from multiple sources
    parent_gene_cols = [col for col in master_df.columns if 'parent' in col.lower() or 'gene' in col.lower()]
    if parent_gene_cols:
        # Use the first non-null value from any parent gene column
        unified_data['Parent_Gene'] = master_df[parent_gene_cols].bfill(axis=1).iloc[:, 0]
    
    # Extract smORF Class from multiple sources  
    smorf_class_cols = [col for col in master_df.columns if 'smorf' in col.lower() and 'class' in col.lower()]
    if smorf_class_cols:
        unified_data['smORF_Class'] = master_df[smorf_class_cols].bfill(axis=1).iloc[:, 0]
    
    # Extract ShortStop Label
    shortstop_cols = [col for col in master_df.columns if 'shortstop' in col.lower() and 'label' in col.lower()]
    if shortstop_cols:
        unified_data['ShortStop_Label'] = master_df[shortstop_cols].bfill(axis=1).iloc[:, 0]
    
    # Extract Annotation Status
    annotation_cols = [col for col in master_df.columns if 'annotation' in col.lower() and 'status' in col.lower()]
    if annotation_cols:
        unified_data['Annotation_Status'] = master_df[annotation_cols].bfill(axis=1).iloc[:, 0]
    
    # Extract Unique Spectral Counts (for proteomics filtering)
    spectral_cols = [col for col in master_df.columns if 'unique_spectral_counts' in col.lower()]
    if spectral_cols:
        unified_data['Unique_Spectral_Counts'] = master_df[spectral_cols].bfill(axis=1).iloc[:, 0]
        unified_data['Unique_Spectral_Counts'] = pd.to_numeric(unified_data['Unique_Spectral_Counts'], errors='coerce')
    
    # Extract UCSC link (use any available)
    ucsc_cols = [col for col in master_df.columns if 'ucsc' in col.lower() or 'CLICK_UCSC' in col]
    if ucsc_cols:
        unified_data['UCSC_Link'] = master_df[ucsc_cols].bfill(axis=1).iloc[:, 0]
    
    # Extract protein length
    length_cols = [col for col in master_df.columns if 'length' in col.lower()]
    if length_cols:
        unified_data['Protein_Length'] = master_df[length_cols].bfill(axis=1).iloc[:, 0]
        unified_data['Protein_Length'] = pd.to_numeric(unified_data['Protein_Length'], errors='coerce')
    
    # Extract start codon
    start_codon_cols = [col for col in master_df.columns if 'start' in col.lower() and ('codon' in col.lower() or 'start_codon' in col.lower())]
    if start_codon_cols:
        unified_data['Start_Codon'] = master_df[start_codon_cols].bfill(axis=1).iloc[:, 0]
    
    # Extract ShortStop Score
    shortstop_score_cols = [col for col in master_df.columns if 'shortstop' in col.lower() and 'score' in col.lower()]
    if shortstop_score_cols:
        unified_data['ShortStop_Score'] = master_df[shortstop_score_cols].bfill(axis=1).iloc[:, 0]
        unified_data['ShortStop_Score'] = pd.to_numeric(unified_data['ShortStop_Score'], errors='coerce')
    
    # Extract TMT q-value for significance
    tmt_qvalue_cols = [col for col in master_df.columns if 'tmt' in col.lower() and 'qvalue' in col.lower()]
    if tmt_qvalue_cols:
        unified_data['TMT_qvalue'] = master_df[tmt_qvalue_cols].bfill(axis=1).iloc[:, 0]
        unified_data['TMT_qvalue'] = pd.to_numeric(unified_data['TMT_qvalue'], errors='coerce')
    
    # Extract ROSMAP padj for significance  
    rosmap_padj_cols = [col for col in master_df.columns if 'rosmap' in col.lower() and 'padj' in col.lower()]
    if rosmap_padj_cols:
        unified_data['ROSMAP_padj'] = master_df[rosmap_padj_cols].bfill(axis=1).iloc[:, 0]
        unified_data['ROSMAP_padj'] = pd.to_numeric(unified_data['ROSMAP_padj'], errors='coerce')
    
    # Create significance indicators
    unified_data['TMT_Significant'] = unified_data.get('TMT_qvalue', pd.Series()).fillna(1.0) < 0.2
    unified_data['ROSMAP_Significant'] = unified_data.get('ROSMAP_padj', pd.Series()).fillna(1.0) < 0.2
    
    return unified_data
    
    return unified_data

def classify_microprotein(row):
    """Classify microprotein as Swiss-Prot or Noncanonical"""
    if 'Database' in row:
        if row['Database'] == 'Swiss-Prot':
            return 'Swiss-Prot'
        elif row['Database'] in ['Salk', 'TrEMBL']:
            return 'Noncanonical'
    
    # For SwissProt file that doesn't have Database column
    if 'Gene Name' in row:
        return 'Swiss-Prot'
    
    # Default for discovery summary (all noncanonical)
    return 'Noncanonical'

def create_ucsc_link(row):
    """Create UCSC Genome Browser link from coordinates or CLICK_UCSC column"""
    if 'CLICK_UCSC' in row and pd.notna(row['CLICK_UCSC']):
        click_ucsc = str(row['CLICK_UCSC'])
        
        # Check if it's a HYPERLINK formula from Excel
        if click_ucsc.startswith('=HYPERLINK('):
            # Extract URL from =HYPERLINK("URL", "display_text") format
            import re
            match = re.search(r'=HYPERLINK\("([^"]+)"', click_ucsc)
            if match:
                return match.group(1)
        
        # If it's already a direct URL
        elif click_ucsc.startswith('http'):
            return click_ucsc
    
    # Fallback: try to parse coordinates
    coords = None
    if 'smORF Coordinates' in row and pd.notna(row['smORF Coordinates']):
        coords = row['smORF Coordinates']
    elif 'genomic_coordinates' in row and pd.notna(row['genomic_coordinates']):
        coords = row['genomic_coordinates']
    
    if coords and coords.startswith('chr'):
        # Parse chr:start-end format
        try:
            chrom, pos = coords.split(':')
            start, end = pos.split('-')
            position = f"{chrom}:{start}-{end}"
            return f"https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position={position}"
        except:
            pass
    
    return None

def display_dataframe_with_ucsc(df, analysis_name, analysis_type):
    """Display dataframe with UCSC browser links and comprehensive filtering"""
    
    # Add classification column as first column
    df['Classification'] = df.apply(classify_microprotein, axis=1)
    
    # Add UCSC links as second column (just the URL, not markdown)
    df['🌐 UCSC Browser'] = df.apply(
        lambda row: create_ucsc_link(row) if create_ucsc_link(row) else None, 
        axis=1
    )
    
    # Remove CLICK_UCSC column if it exists (redundant with UCSC Browser column)
    if 'CLICK_UCSC' in df.columns:
        df = df.drop('CLICK_UCSC', axis=1)
    
    # Reorder columns to put Classification first, UCSC second
    cols = df.columns.tolist()
    if 'Classification' in cols:
        cols.remove('Classification')
    if '🌐 UCSC Browser' in cols:
        cols.remove('🌐 UCSC Browser')
    
    new_cols = ['Classification', '🌐 UCSC Browser'] + cols
    df = df[new_cols]
    
    # Statistics based on analysis type
    if analysis_type != 'scrna':  # Skip stats for scRNA
        st.markdown("### Quick Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        total_entries = len(df)
        swiss_count = len(df[df['Classification'] == 'Swiss-Prot'])
        noncanonical_count = len(df[df['Classification'] == 'Noncanonical'])
        
        with col1:
            st.markdown(f"""
            <div class="metric-total">
                <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">Total Entries</div>
                <div data-testid="metric-value" style="font-size: 2rem; font-weight: bold;">{total_entries:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if analysis_type == 'noncanonical_only':
            # For RP3 and Long-Read (noncanonical only)
            with col2:
                st.markdown(f"""
                <div class="metric-noncanonical">
                    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">Noncanonical Only</div>
                    <div data-testid="metric-value" style="font-size: 2rem; font-weight: bold;">{total_entries:,}</div>
                    <div style="font-size: 0.8rem; color: #28a745; margin-top: 0.25rem;">↗ 100% Noncanonical</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.info("This analysis contains only noncanonical microproteins")
        
        elif analysis_type in ['mixed', 'combined']:
            # For Proteomics, Short-Read, Discovery Summary
            with col2:
                st.markdown(f"""
                <div class="metric-swiss-prot">
                    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">Swiss-Prot</div>
                    <div data-testid="metric-value" style="font-size: 2rem; font-weight: bold;">{swiss_count:,}</div>
                    <div style="font-size: 0.8rem; color: #28a745; margin-top: 0.25rem;">↗ {swiss_count/total_entries*100:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-noncanonical">
                    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">Noncanonical</div>
                    <div data-testid="metric-value" style="font-size: 2rem; font-weight: bold;">{noncanonical_count:,}</div>
                    <div style="font-size: 0.8rem; color: #28a745; margin-top: 0.25rem;">↗ {noncanonical_count/total_entries*100:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Column explanations
    display_column_explanations(df, analysis_name)
    
    # Filtering options
    st.markdown("### Filter & Explore")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Classification filter
        available_classifications = ['All'] + sorted(df['Classification'].unique().tolist())
        classification_filter = st.selectbox(
            "Filter by Classification:",
            options=available_classifications,
            index=0
        )
    
    with col2:
        # Number of rows to display
        show_rows_options = ['All', 25, 50, 100, 200, 500]
        show_rows = st.selectbox("Rows to display:", show_rows_options, index=2)
    
    with col3:
        # Additional column filter (dynamic based on available columns)
        filterable_columns = [col for col in df.columns if col not in ['Classification', '🌐 UCSC Browser', 'sequence'] and df[col].dtype == 'object']
        if filterable_columns:
            selected_filter_column = st.selectbox("Additional column filter:", ['None'] + filterable_columns)
        else:
            selected_filter_column = 'None'
    
    # Additional filter controls
    additional_filter_value = None
    if selected_filter_column != 'None' and selected_filter_column:
        unique_values = ['All'] + sorted([str(val) for val in df[selected_filter_column].dropna().unique()])
        additional_filter_value = st.selectbox(
            f"Filter by {selected_filter_column}:",
            options=unique_values,
            index=0
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Apply classification filter
    if classification_filter != 'All':
        filtered_df = filtered_df[filtered_df['Classification'] == classification_filter]
    
    # Apply additional column filter
    if selected_filter_column != 'None' and additional_filter_value != 'All' and additional_filter_value:
        filtered_df = filtered_df[filtered_df[selected_filter_column].astype(str) == additional_filter_value]
    
    # Search functionality
    search_term = st.text_input("Search in all columns:", placeholder="Type to search...")
    if search_term:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        filtered_df = filtered_df[mask]
    
    st.markdown(f"**Showing {len(filtered_df):,} of {total_entries:,} entries**")
    
    # Prepare display dataframe
    if show_rows == 'All':
        display_df = filtered_df.copy()
    else:
        display_df = filtered_df.head(show_rows).copy()
    
    # Color code the classification column
    def highlight_classification(val):
        if val == 'Swiss-Prot':
            return f'background-color: {COLORS["swiss_prot"]}30; color: {COLORS["swiss_prot"]}; font-weight: bold'
        elif val == 'Noncanonical':
            return f'background-color: {COLORS["noncanonical"]}30; color: {COLORS["noncanonical"]}; font-weight: bold'
        return ''
    
    # Style the dataframe
    styled_df = display_df.style.map(highlight_classification, subset=['Classification'])
    
    # Display the dataframe
    st.dataframe(
        styled_df,
        width='stretch',
        height=600,
        column_config={
            "🌐 UCSC Browser": st.column_config.LinkColumn(
                "🌐 UCSC Browser",
                help="Click to view in UCSC Genome Browser (opens in new tab)",
                display_text="🔗 View Genome"
            )
        }
    )
    
    # Download option
    if st.button("📥 Download Filtered Data as CSV", key=f"download_{analysis_name}"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"{analysis_name.replace(' ', '_')}_filtered.csv",
            mime="text/csv"
        )
    
    return display_df

def get_column_explanations(df, analysis_name):
    """Generate dynamic column explanations based on the dataframe and analysis type"""
    columns = df.columns.tolist()
    
    # Core microprotein columns
    core_explanations = {
        'smORF_id': 'Unique identifier for small Open Reading Frame',
        'smORF_coordinates': 'Genomic coordinates (chromosome:start-end)',
        'smORF_type': 'Classification of smORF (uORF, dORF, intergenic, etc.)',
        'sequence': 'Amino acid sequence of the microprotein',
        'gene_name': 'Associated gene symbol',
        'gene_symbol': 'Associated gene symbol',
        'gene_biotype': 'Type of gene (protein_coding, lncRNA, pseudogene, etc.)',
        'transcript_id': 'Ensembl transcript identifier',
        'transcript_biotype': 'Type of transcript',
        'Classification': 'Swiss-Prot (canonical) vs Noncanonical microproteins',
        '🌐 UCSC Browser': 'Click to view genomic location in UCSC Genome Browser'
    }
    
    # Analysis-specific explanations
    analysis_specific = {
        # Proteomics (TMT) columns
        'TMT_intensity': 'Tandem Mass Tag intensity measurement',
        'log2FC': 'Log2 fold change (AD vs Control)',
        'pvalue': 'Statistical p-value',
        'padj': 'Adjusted p-value (FDR corrected)',
        'significant': 'Statistical significance indicator',
        'protein_id': 'Protein identifier',
        'peptide_count': 'Number of peptides detected',
        'unique_peptides': 'Number of unique peptides',
        'coverage': 'Protein sequence coverage percentage',
        
        # Transcriptomics columns
        'baseMean': 'Average normalized expression across samples',
        'lfcSE': 'Standard error of log2 fold change',
        'stat': 'Test statistic',
        'FPKM': 'Fragments Per Kilobase Million (expression measure)',
        'TPM': 'Transcripts Per Million (expression measure)',
        'CPM': 'Counts Per Million (expression measure)',
        'raw_counts': 'Raw read counts',
        'normalized_counts': 'Normalized read counts',
        
        # RP3 (Ribosome Profiling) columns
        'RP3_score': 'RP3 ribosome profiling score',
        'translation_efficiency': 'Translation efficiency measure',
        'ribosome_footprints': 'Number of ribosome footprints',
        'RPF_density': 'Ribosome Protected Fragment density',
        'TE_log2FC': 'Translation efficiency log2 fold change',
        
        # Annotation columns
        'discovery_method': 'Method used to discover the microprotein',
        'evidence_level': 'Level of experimental evidence',
        'database_source': 'Source database (Salk, TrEMBL, Swiss-Prot)',
        'annotation_status': 'Current annotation status',
        'length_aa': 'Length in amino acids',
        'molecular_weight': 'Molecular weight in Daltons',
        
        # Cell type enrichment
        'cell_type': 'Specific cell type',
        'enrichment_score': 'Enrichment score in specific cell types',
        'enrichment_pvalue': 'P-value for enrichment analysis',
        'fold_enrichment': 'Fold enrichment over background',
        
        # Chromosomal information
        'chromosome': 'Chromosome location',
        'chr': 'Chromosome location',
        'start': 'Start genomic coordinate',
        'end': 'End genomic coordinate',
        'strand': 'DNA strand (+ or -)',
        'genomic_context': 'Genomic context classification'
    }
    
    # Combine explanations
    all_explanations = {**core_explanations, **analysis_specific}
    
    # Get explanations for columns that exist in the dataframe
    present_explanations = {}
    for col in columns:
        if col in all_explanations:
            present_explanations[col] = all_explanations[col]
        else:
            # Generate a generic explanation for unknown columns
            present_explanations[col] = f"Data column specific to {analysis_name} analysis"
    
    return present_explanations

def display_column_explanations(df, analysis_name):
    """Display dynamic column explanations in an expander"""
    st.markdown("### Column Explanations")
    explanations = get_column_explanations(df, analysis_name)
    
    with st.expander("Click to view column descriptions", expanded=False):
        # Group explanations by category
        core_cols = ['smORF_id', 'smORF_coordinates', 'smORF_type', 'sequence', 'gene_name', 'gene_symbol', 
                    'gene_biotype', 'transcript_id', 'Classification', '🌐 UCSC Browser']
        
        analysis_cols = [col for col in explanations.keys() if col not in core_cols]
        
        # Display core columns if present
        core_present = [col for col in core_cols if col in explanations]
        if core_present:
            st.markdown("**Core Microprotein Information:**")
            for col in core_present:
                st.markdown(f"- **{col}**: {explanations[col]}")
            st.markdown("")
        
        # Display analysis-specific columns
        if analysis_cols:
            st.markdown(f"**{analysis_name} Analysis Columns:**")
            for col in sorted(analysis_cols):
                st.markdown(f"- **{col}**: {explanations[col]}")
            st.markdown("")
        
        # Add analysis-specific context
        analysis_context = {
            "Annotation Summary": "This dataset contains newly discovered noncanonical microproteins from the Salk/TrEMBL database.",
            "Proteomics (TMT)": "This dataset contains mass spectrometry results comparing protein levels between AD and control samples.",
            "Proteomics + RiboSeq Coverage (RP3)": "This dataset contains ribosome profiling results validating active translation of microproteins.",
            "RiboSeq + ShortStop": "This dataset combines ribosome sequencing with ShortStop analysis to identify actively translated small ORFs and microproteins.",
            "ShortStop": "This dataset contains ShortStop analysis results for identifying actively translated small ORFs and microproteins.",
            "Short-Read RNA": "This dataset contains RNA-seq differential expression results comparing AD vs control samples.",
            "Long-Read RNA": "This dataset contains long-read RNA sequencing results for transcript validation."
        }
        
        if analysis_name in analysis_context:
            st.info(f"**Analysis Context:** {analysis_context[analysis_name]}")

def load_and_combine_data(analysis_info):
    """Load dataset"""
    path = analysis_info['path']
    if path.exists():
        return pd.read_csv(path, low_memory=False)
    else:
        return None

def display_noncanonical_explorer():
    """Main Noncanonical Explorer interface"""
    
    # st.markdown(f"""
    # <div style="background: linear-gradient(135deg, {COLORS['swiss_prot']} 0%, {COLORS['noncanonical']} 100%); 
    #             padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;">
    #     <h1 style="color: white; margin: 0; font-size: 2.2rem; font-weight: 700;">
    #         🧬 Noncanonical Explorer
    #     </h1>
    #     <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
    #         Global microprotein database with advanced filtering
    #     </p>
    # </div>
    # """, unsafe_allow_html=True)
    
    # Load and merge all data
    with st.spinner("Loading comprehensive microprotein database..."):
        try:
            master_df = load_and_merge_all_data()
            unified_df = extract_unified_fields(master_df)
            
            # Filter out entries where Annotation Method is None
            if 'Annotation_Status' in unified_df.columns:
                before_filter_count = len(unified_df)
                annotation_mask = ~(unified_df['Annotation_Status'].isna() | (unified_df['Annotation_Status'] == 'None'))
                unified_df = unified_df[annotation_mask]
                filtered_count = before_filter_count - len(unified_df)
                
            
            if unified_df.empty:
                st.error("❌ No data could be loaded from any analysis files.")
                return
                
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return
        
    # Compact Filters Section
    st.markdown('<div class="analysis-selection-container">', unsafe_allow_html=True)
    
    # Filter header
    
    # Compact filter layout
    filter_row1, filter_row2 = st.columns(2)
    
    with filter_row1:
            # Gene name search
            gene_search = st.text_input(
                "Gene Search",
                placeholder="e.g., BCL3, RAB3C...",
                help="Search for microproteins from specific parent genes"
            )
            
            # smORF Class filter
            if 'smORF_Class' in unified_df.columns:
                smorf_classes = unified_df['smORF_Class'].dropna().unique()
                smorf_classes = sorted([str(cls) for cls in smorf_classes if str(cls) != 'nan'])
                
                selected_smorf_classes = st.multiselect(
                    "smORF Type",
                    options=['All'] + smorf_classes,
                    default=['All'],
                    help="Filter by small Open Reading Frame classification"
                )
            else:
                selected_smorf_classes = ['All']
                
    with filter_row2:
        # ShortStop Label filter
        if 'ShortStop_Label' in unified_df.columns:
            shortstop_labels = unified_df['ShortStop_Label'].dropna().unique()
            shortstop_labels = sorted([str(label) for label in shortstop_labels if str(label) != 'nan'])
            
            selected_shortstop_labels = st.multiselect(
                "ShortStop",
                options=['All'] + shortstop_labels,
                default=['All'],
                help="Filter by ShortStop ML classification"
            )
        else:
            selected_shortstop_labels = ['All']
            
        # Annotation Status filter
        if 'Annotation_Status' in unified_df.columns:
            annotation_statuses = unified_df['Annotation_Status'].dropna().unique()
            annotation_statuses = sorted([str(status) for status in annotation_statuses if str(status) != 'nan'])
            
            selected_annotation_status = st.multiselect(
                "Detection Type (i.e., MS or Ribo-Seq/ShortStop)",
                options=['All'] + annotation_statuses,
                default=['All'],
                help="Filter by annotation status"
            )
        else:
            selected_annotation_status = ['All']
    
    # Start Codon Filter (new row)
    if 'Start_Codon' in unified_df.columns:
        start_codons = unified_df['Start_Codon'].dropna().unique()
        start_codons = sorted([str(codon) for codon in start_codons if str(codon) != 'nan'])
        
        selected_start_codons = st.multiselect(
            "Start Codon",
            options=['All'] + start_codons,
            default=['ATG'],
            help="Filter by start codon (ATG, CTG, TTG, etc.)"
        )
    else:
        selected_start_codons = ['All']
    
    # Quantitative filters in a compact row
    st.markdown("**📊 Quantitative Filters**")
    quant_col1, quant_col2 = st.columns(2)
    
    with quant_col1:
        # Spectral counts range input
        if 'Unique_Spectral_Counts' in unified_df.columns:
            spectral_data = unified_df['Unique_Spectral_Counts'].dropna()
            if len(spectral_data) > 0:
                min_spectral = int(spectral_data.min()) if not np.isnan(spectral_data.min()) else 0
                max_spectral = int(spectral_data.max()) if not np.isnan(spectral_data.max()) else 100
                
                # Text inputs for precise control
                spec_col1, spec_col2 = st.columns(2)
                with spec_col1:
                    min_spectral_input = st.number_input(
                        "⚗️ Min Spectral",
                        min_value=0,
                        max_value=max_spectral,
                        value=min_spectral,
                        step=1,
                        help="Minimum unique spectral counts"
                    )
                with spec_col2:
                    max_spectral_input = st.number_input(
                        "⚗️ Max Spectral",
                        min_value=0,
                        max_value=max_spectral,
                        value=max_spectral,
                        step=1,
                        help="Maximum unique spectral counts"
                    )
                spectral_range = (min_spectral_input, max_spectral_input)
            else:
                spectral_range = (0, 100)
        else:
            spectral_range = (0, 100)
                
    with quant_col2:
        # Protein length filter
        if 'Protein_Length' in unified_df.columns:
            length_data = unified_df['Protein_Length'].dropna()
            if len(length_data) > 0:
                min_length = int(length_data.min()) if not np.isnan(length_data.min()) else 1
                max_length = int(length_data.max()) if not np.isnan(length_data.max()) else 200
                
                # Text inputs for precise control
                len_col1, len_col2 = st.columns(2)
                with len_col1:
                    min_length_input = st.number_input(
                        "📏 Min Length",
                        min_value=1,
                        max_value=max_length,
                        value=min_length,
                        step=1,
                        help="Minimum protein length (amino acids)"
                    )
                with len_col2:
                    max_length_input = st.number_input(
                        "📏 Max Length",
                        min_value=1,
                        max_value=max_length,
                        value=max_length,
                        step=1,
                        help="Maximum protein length (amino acids)"
                    )
                length_range = (min_length_input, max_length_input)
            else:
                length_range = (1, 200)
        else:
            length_range = (1, 200)
    st.markdown('</div>', unsafe_allow_html=True)  # Close analysis-selection-container
    
    # Apply filters
    filtered_df = unified_df.copy()
    
    # Gene name filter
    if gene_search:
        if 'Parent_Gene' in filtered_df.columns:
            mask = filtered_df['Parent_Gene'].str.contains(gene_search, case=False, na=False)
            filtered_df = filtered_df[mask]
    
    # smORF Class filter
    if 'All' not in selected_smorf_classes and 'smORF_Class' in filtered_df.columns:
        mask = filtered_df['smORF_Class'].isin(selected_smorf_classes)
        filtered_df = filtered_df[mask]
    
    # ShortStop Label filter
    if 'All' not in selected_shortstop_labels and 'ShortStop_Label' in filtered_df.columns:
        mask = filtered_df['ShortStop_Label'].isin(selected_shortstop_labels)
        filtered_df = filtered_df[mask]
    
    # Annotation Status filter
    if 'All' not in selected_annotation_status and 'Annotation_Status' in filtered_df.columns:
        mask = filtered_df['Annotation_Status'].isin(selected_annotation_status)
        filtered_df = filtered_df[mask]
    
    # Start Codon filter
    if 'All' not in selected_start_codons and 'Start_Codon' in filtered_df.columns:
        mask = filtered_df['Start_Codon'].isin(selected_start_codons)
        filtered_df = filtered_df[mask]
    
    # Spectral counts filter
    if 'Unique_Spectral_Counts' in filtered_df.columns:
        mask = (
            (filtered_df['Unique_Spectral_Counts'] >= spectral_range[0]) & 
            (filtered_df['Unique_Spectral_Counts'] <= spectral_range[1])
        )
        filtered_df = filtered_df[mask]
    
    # Protein length filter
    if 'Protein_Length' in filtered_df.columns:
        mask = (
            (filtered_df['Protein_Length'] >= length_range[0]) & 
            (filtered_df['Protein_Length'] <= length_range[1])
        )
        filtered_df = filtered_df[mask]
    
    # Display results with dark theme
    st.markdown('<div class="analysis-selection-container">', unsafe_allow_html=True)
    
    if len(filtered_df) == 0:
        st.warning("No microproteins match your current filters. Try adjusting the criteria.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Summary statistics with grouped layout
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h4 style="color: #ffffff; margin-bottom: 1rem; text-align: center; font-weight: 300; letter-spacing: 1px;">
            📊 FILTERED RESULTS
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Main metrics section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-total" style="border: 2px solid #4a90e2; background: linear-gradient(135deg, #1e3a5f 0%, #2a4a6f 100%);">
            <div style="font-size: 0.85rem; margin-bottom: 0.5rem; color: #a0c4ff;">TOTAL FOUND</div>
            <div data-testid="metric-value" style="font-size: 2.2rem; font-weight: bold; color: #ffffff;">{len(filtered_df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'Parent_Gene' in filtered_df.columns:
            unique_genes = filtered_df['Parent_Gene'].nunique()
            st.markdown(f"""
            <div class="metric-swiss-prot" style="border: 2px solid #2c3342; background: linear-gradient(135deg, #1a212d 0%, #3a2e6f 100%);">
                <div style="font-size: 0.85rem; margin-bottom: 0.5rem; color: #1b212d;">UNIQUE GENES</div>
                <div data-testid="metric-value" style="font-size: 2.2rem; font-weight: bold; color: #ffffff;">{unique_genes:,}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if 'smORF_Class' in filtered_df.columns:
            unique_classes = filtered_df['smORF_Class'].nunique()
            st.markdown(f"""
            <div class="metric-noncanonical" style="border: 2px solid #ff6b6b; background: linear-gradient(135deg, #5f1e1e 0%, #6f2a2a 100%);">
                <div style="font-size: 0.85rem; margin-bottom: 0.5rem; color: #ffa0a0;">smORF TYPES</div>
                <div data-testid="metric-value" style="font-size: 2.2rem; font-weight: bold; color: #ffffff;">{unique_classes:,}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Significance metrics section with visual separator
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0; padding: 0 1rem;">
        <div style="border-bottom: 1px solid #3a5f7f; margin-bottom: 1rem;"></div>
        <h5 style="color: #ffffff; text-align: center; font-weight: 300; letter-spacing: 1px; margin-bottom: 1rem;">
            🔬 SIGNIFICANCE METRICS
        </h5>
    </div>
    """, unsafe_allow_html=True)
    
    sig_col1, sig_col2 = st.columns(2)
    
    with sig_col1:
        # Count TMT significant entries
        if 'TMT_Significant' in filtered_df.columns:
            tmt_sig_count = filtered_df['TMT_Significant'].sum()
            st.markdown(f"""
            <div class="metric-total" style="border: 2px solid #ffd700; background: linear-gradient(135deg, #5f4f1e 0%, #6f5a2a 100%);">
                <div style="font-size: 0.85rem; margin-bottom: 0.5rem; color: #fff5a0;">TMT SIGNIFICANT</div>
                <div data-testid="metric-value" style="font-size: 2.2rem; font-weight: bold; color: #ffffff;">{tmt_sig_count:,}</div>
                <div style="font-size: 0.7rem; color: #e6d78a; margin-top: 0.25rem;">Proteomics</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            spectral_count = filtered_df['Unique_Spectral_Counts'].notna().sum() if 'Unique_Spectral_Counts' in filtered_df.columns else 0
            st.markdown(f"""
            <div class="metric-total" style="border: 2px solid #ffd700; background: linear-gradient(135deg, #5f4f1e 0%, #6f5a2a 100%);">
                <div style="font-size: 0.85rem; margin-bottom: 0.5rem; color: #fff5a0;">WITH SPECTRAL DATA</div>
                <div data-testid="metric-value" style="font-size: 2.2rem; font-weight: bold; color: #ffffff;">{spectral_count:,}</div>
                <div style="font-size: 0.7rem; color: #e6d78a; margin-top: 0.25rem;">Proteomics</div>
            </div>
            """, unsafe_allow_html=True)
    
    with sig_col2:
        # Count RNA significant entries
        if 'ROSMAP_Significant' in filtered_df.columns:
            rna_sig_count = filtered_df['ROSMAP_Significant'].sum()
            st.markdown(f"""
            <div class="metric-swiss-prot" style="border: 2px solid #32cd32; background: linear-gradient(135deg, #1e5f1e 0%, #2a6f2a 100%);">
                <div style="font-size: 0.85rem; margin-bottom: 0.5rem; color: #a0ffa0;">RNA SIGNIFICANT</div>
                <div data-testid="metric-value" style="font-size: 2.2rem; font-weight: bold; color: #ffffff;">{rna_sig_count:,}</div>
                <div style="font-size: 0.7rem; color: #8ae68a; margin-top: 0.25rem;">Transcriptomics</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-total" style="border: 2px solid #32cd32; background: linear-gradient(135deg, #1e5f1e 0%, #2a6f2a 100%);">
                <div style="font-size: 0.85rem; margin-bottom: 0.5rem; color: #a0ffa0;">RNA DATA</div>
                <div data-testid="metric-value" style="font-size: 2.2rem; font-weight: bold; color: #ffffff;">N/A</div>
                <div style="font-size: 0.7rem; color: #8ae68a; margin-top: 0.25rem;">Transcriptomics</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Prepare display dataframe with only the requested columns
    display_cols = ['sequence']
    
    # Add UCSC browser link first
    if 'UCSC_Link' in filtered_df.columns:
        filtered_df['🌐 UCSC Browser'] = filtered_df['UCSC_Link'].apply(
            lambda x: create_ucsc_link({'CLICK_UCSC': x}) if pd.notna(x) else None
        )
        display_cols.append('🌐 UCSC Browser')
    
    # Add the specific columns you requested with renamed headers
    column_mapping = {
        'Parent_Gene': 'Parent Gene',
        'smORF_Class': 'smORF Type', 
        'ShortStop_Label': 'ShortStop',
        'ShortStop_Score': 'ShortStop Score',
        'Annotation_Status': 'Annotation Method',
        'Unique_Spectral_Counts': 'Unique Spectral Counts',
        'Protein_Length': 'Protein Length'
    }
    
    for original_col, display_name in column_mapping.items():
        if original_col in filtered_df.columns:
            filtered_df[display_name] = filtered_df[original_col]
            display_cols.append(display_name)
    
    # Add significance indicators
    if 'TMT_Significant' in filtered_df.columns:
        filtered_df['TMT Significant (q<0.2)'] = filtered_df['TMT_Significant'].apply(
            lambda x: '✅ Yes' if x else '❌ No' if pd.notna(x) else 'N/A'
        )
        display_cols.append('TMT Significant (q<0.2)')
    
    if 'ROSMAP_Significant' in filtered_df.columns:
        filtered_df['ROSMAP Significant (padj<0.2)'] = filtered_df['ROSMAP_Significant'].apply(
            lambda x: '✅ Yes' if x else '❌ No' if pd.notna(x) else 'N/A'
        )
        display_cols.append('ROSMAP Significant (padj<0.2)')
    
    # Create final display dataframe
    display_df = filtered_df[display_cols].copy()
    
    # Reorder columns: sequence, UCSC, then the rest
    final_cols = ['sequence']
    if '🌐 UCSC Browser' in display_df.columns:
        final_cols.append('🌐 UCSC Browser')
    
    remaining_cols = [col for col in display_df.columns if col not in final_cols]
    display_df = display_df[final_cols + remaining_cols]
    
    # Add visual separator before data table
    st.markdown("""
    <div style="margin: 2.5rem 0 1.5rem 0; padding: 0 1rem;">
        <div style="border-bottom: 2px solid #4a90e2; margin-bottom: 1.5rem;"></div>
        <h4 style="color: #ffffff; text-align: center; font-weight: 300; letter-spacing: 1px; margin-bottom: 0.5rem;">
            🧬 MICROPROTEIN DATABASE
        </h4>
        <p style="color: #a0c4ff; text-align: center; font-size: 0.9rem; margin-bottom: 1.5rem; font-style: italic;">
            Explore filtered microproteins with interactive columns and UCSC browser links
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "🌐 UCSC Browser": st.column_config.LinkColumn(
                "🌐 UCSC Browser",
                help="Click to view in UCSC Genome Browser",
                max_chars=20
            ),
            "sequence": st.column_config.TextColumn(
                "Microprotein Sequence",
                help="Amino acid sequence of the microprotein",
                max_chars=50
            ),
            "Parent Gene": st.column_config.TextColumn(
                "Parent Gene",
                help="Gene from which this microprotein originates",
                max_chars=15
            ),
            "smORF Type": st.column_config.TextColumn(
                "smORF Type",
                help="Classification of small Open Reading Frame",
                max_chars=15
            ),
            "ShortStop": st.column_config.TextColumn(
                "ShortStop",
                help="ShortStop ML classification label",
                max_chars=20
            ),
            "ShortStop Score": st.column_config.NumberColumn(
                "ShortStop Score",
                help="ShortStop ML confidence score (0-1)",
                format="%.3f"
            ),
            "Annotation Method": st.column_config.TextColumn(
                "Annotation Method",
                help="Method used for annotation (MS = Mass Spectrometry, etc.)",
                max_chars=10
            ),
            "Unique Spectral Counts": st.column_config.NumberColumn(
                "Unique Spectral Counts",
                help="Number of unique mass spectrometry spectral counts",
                format="%d"
            ),
            "Protein Length": st.column_config.NumberColumn(
                "Protein Length",
                help="Length of protein in amino acids",
                format="%d"
            ),
            "TMT Significant (q<0.2)": st.column_config.TextColumn(
                "TMT Significant",
                help="Whether TMT proteomics analysis shows significant change (q-value < 0.2)",
                max_chars=10
            ),
            "ROSMAP Significant (padj<0.2)": st.column_config.TextColumn(
                "ROSMAP Significant",
                help="Whether ROSMAP analysis shows significant change (padj < 0.2)",
                max_chars=10
            )
        }
    )
    
    # Download button
    csv_data = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Results as CSV",
        data=csv_data,
        file_name=f"noncanonical_explorer_results_{len(filtered_df)}_microproteins.csv",
        mime="text/csv"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close analysis-selection-container

def main():
    # Compact Header
    st.markdown(f"""
    <div class="main-header">
        Brain Microproteins Analysis Dashboard v1.0 (2025)
        <br><small style="font-size: 0.55em; font-weight: normal; line-height: 1.2;">
        Interactive exploration of canonical vs noncanonical microproteins in Alzheimer's Disease
        </small>
        <br><small style="font-size: 0.45em; font-weight: normal; opacity: 0.8; line-height: 1.1;">
        v1 - Initial Release | TMT-MS (n=480), Ribosome Profiling + ShortStop ML (n=42), Short-Read RNA-seq (n=387), Long-Read RNA-seq (n=12) | 
        Created by Dr. Brendan Miller (Saghatelian Lab, Salk Institute)
        </small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        # Navigation Header
        st.markdown(f"""
        <div class="analysis-hub-header">
            <h2 class="analysis-hub-title">Navigation</h2>
            <p class="analysis-hub-subtitle">Choose Your Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main navigation options
        st.markdown('<div class="analysis-selection-container">', unsafe_allow_html=True)
        
        # Navigation radio buttons
        nav_options = {
            "Noncanonical Explorer": "noncanonical_explorer",
            "Individual Analysis Hub": "individual_analysis"
        }
        
        selected_nav = st.radio(
            "Navigate to:",
            options=list(nav_options.keys()),
            index=0,  # Default to Noncanonical Explorer
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced Color Legend
        st.markdown('<div class="legend-container">', unsafe_allow_html=True)
        st.markdown("### 🎨 Color Legend")
        st.markdown(f"""
        <div style="margin: 0.75rem 0; display: flex; align-items: center;">
            <span class="swiss-prot-badge">Swiss-Prot</span> 
            <span style="margin-left: 0.5rem; font-size: 0.9em;">Canonical microproteins</span>
        </div>
        <div style="margin: 0.75rem 0; display: flex; align-items: center;">
            <span class="noncanonical-badge">Noncanonical</span> 
            <span style="margin-left: 0.5rem; font-size: 0.9em;">Salk/TrEMBL discoveries</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick tips section
        st.markdown(f"""
        <div class="info-card">
            <strong>💡 Quick Tips:</strong><br>
            • Click 🔗 links to view in UCSC Browser<br>
            • Use filters to narrow your search<br>
            • Download filtered results as CSV<br>
            • Swiss-Prot = established proteins<br>
            • Noncanonical = uncharacterized microproteins
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area based on navigation selection
    selected_nav_key = nav_options[selected_nav]
    
    if selected_nav_key == "noncanonical_explorer":
        # Primary interface - Noncanonical Explorer
        display_noncanonical_explorer()
    elif selected_nav_key == "individual_analysis":
        # Secondary interface - Individual Analysis Hub
        display_individual_analysis_hub()

def display_individual_analysis_hub():
    """Individual analysis hub interface - now in main content area"""
    
    # Load analysis files
    analysis_files = load_analysis_results()
    
    # Analysis Hub Header for main content
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['swiss_prot']} 0%, {COLORS['noncanonical']} 100%); 
                padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 2.2rem; font-weight: 700;">
            📊 Individual Analysis Hub
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Explore specific analysis results in detail
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis Selection Container
    st.markdown('<div class="analysis-selection-container">', unsafe_allow_html=True)
    st.markdown("### 🔬 Select an analysis to explore:")
    
    # Create formatted options with icons
    analysis_options = {
        "Annotation Summary": "Annotation Summary",
        "Proteomics (TMT)": "Proteomics (TMT)", 
        "Proteomics + RiboSeq (RP3)": "Proteomics + RiboSeq (RP3)",
        "Short-Read RNA in AD": "Short-Read RNA in AD",
        "Long-Read RNA in AD": "Long-Read RNA in AD",
        "scRNA Enrichment": "scRNA Enrichment",
        "ShortStop Classification": "ShortStop Classification"
    }
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_display = st.radio(
            "Choose Analysis:",
            options=list(analysis_options.keys()),
            format_func=lambda x: x,
            label_visibility="collapsed",
            horizontal=False
        )
    
    with col2:
        # Get the actual analysis name and show info
        selected_analysis = analysis_options[selected_display] if selected_display else None
        
        if selected_analysis:
            analysis_info = analysis_files[selected_analysis]
            st.markdown(f"""
            <div class="info-card">
                <strong>📝 Description:</strong><br>
                {analysis_info['description']}
                <br><br>
                <strong>📁 File:</strong><br>
                <code>{analysis_info['path'].name}</code>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area for individual analysis
    if selected_analysis:
        analysis_info = analysis_files[selected_analysis]
        
        # Check if file(s) exist
        missing_files = []
        if isinstance(analysis_info['path'], list):
            for path in analysis_info['path']:
                if not path.exists():
                    missing_files.append(str(path))
        else:
            if not analysis_info['path'].exists():
                missing_files.append(str(analysis_info['path']))
        
        if missing_files:
            st.error(f"❌ Analysis file(s) not found:")
            for file in missing_files:
                st.error(f"  • `{file}`")
            st.info("💡 Make sure you've run the analysis pipeline first with `./run_all_analyses.sh --mode=run`")
            return
        
        try:
            # Load the data
            with st.spinner(f"Loading {selected_analysis}..."):
                df = load_and_combine_data(analysis_info)
            
            if df is None or len(df) == 0:
                st.error(f"❌ No data found for {selected_analysis}")
                return
            
            st.success(f"✅ Loaded {len(df):,} entries from {selected_analysis}")
            
            # Display data with interactive features
            display_df = display_dataframe_with_ucsc(df, selected_analysis, analysis_info.get('type', 'mixed'))
            
        except Exception as e:
            st.error(f"❌ Error loading {selected_analysis}: {str(e)}")
            st.info("Please check the file format and ensure it contains the expected columns.")
    
    else:
        # Welcome message for individual analysis
        st.markdown("""
        ## 👋 Individual Analysis Explorer
        
        This section provides access to specific microprotein analysis results:
        
        - **Discovery Summary**: Combined canonical (Swiss-Prot) & noncanonical discoveries
        - **Proteomics**: Mass spectrometry evidence (both canonical & noncanonical)
        - **RP3 Analysis**: Ribosome profiling validation (noncanonical only)
        - **Short-Read RNA**: RNA-seq differential expression (both canonical & noncanonical)
        - **Long-Read RNA**: Long-read transcriptomics (noncanonical only)
        - **scRNA Enrichment**: Single-cell expression patterns
        
        ### 🚀 Getting Started:
        1. **Select an analysis** from the options above
        2. **Filter and search** the data table (Classification is first column)
        3. **Click UCSC links** to view genomic locations in new browser tab
        4. **Download** filtered results as needed
        
        ### 💡 For comprehensive cross-analysis exploration, use the **Noncanonical Explorer** from the sidebar!
        """)

if __name__ == "__main__":
    main()