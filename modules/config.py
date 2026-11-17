import streamlit as st

FILE_PATH = "SIM_Connectivity_2026-2030.xlsx"

MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

CURRENCY = "GH₵"

COLORS = {
    "navy": "#172B3A",
    "navy_light": "#223D50",
    "teal": "#159D91",
    "teal_light": "#DDF4EF",
    "green": "#159D72",
    "gold": "#E9B949",
    "blue": "#4786C6",
    "red": "#DC6868",
    "background": "#F3F6F9",
    "surface": "#FFFFFF",
    "text": "#172B3A",
    "muted": "#758494",
    "border": "#E5EBF0",
}

PALETTE = ["#159D91", "#4786C6", "#E9B949", "#9368C8", "#E17C70"]


def inject_custom_css():
    """Inject executive theme CSS into the Streamlit app with Zimatics branding."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background: #F3F6F9;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1600px;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #172B3A 0%, #1D3748 65%, #142A39 100%);
            border-right: 1px solid rgba(255,255,255,0.06);
        }

        section[data-testid="stSidebar"] * {
            color: #E9F1F5 !important;
        }

        section[data-testid="stSidebar"] label {
            font-weight: 600;
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] {
            background: #294354;
            border-radius: 9px;
        }

        section[data-testid="stSidebar"] input {
            color: #172B3A !important;
        }

        .sidebar-brand {
            padding: 15px 0 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            margin-bottom: 20px;
            text-align: left;
        }

        .brand-logo-text {
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #FFFFFF;
        }

        .brand-caption {
            font-size: 11px;
            color: #A8BAC6;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-top: 4px;
        }

        .sidebar-section {
            color: #8EA8B8;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.6px;
            text-transform: uppercase;
            margin: 22px 0 12px 0;
        }

        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            padding: 10px 0 20px 0;
        }

        .header-title {
            font-size: clamp(25px, 3vw, 34px);
            font-weight: 800;
            letter-spacing: -1.3px;
            color: #172B3A;
            margin: 0;
        }

        .header-subtitle {
            font-size: 13px;
            color: #758494;
            margin-top: 7px;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 14px;
            background: #E5F6F0;
            color: #12845F;
            border-radius: 30px;
            font-size: 11px;
            font-weight: 700;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #19B982;
        }

        .section-heading {
            font-size: 17px;
            font-weight: 800;
            color: #172B3A;
            letter-spacing: -0.3px;
            margin: 25px 0 5px 0;
        }

        .section-description {
            font-size: 12px;
            color: #8493A0;
            margin-bottom: 14px;
        }

        .metric-card {
            position: relative;
            background: #FFFFFF;
            border: 1px solid #E7EDF2;
            border-radius: 15px;
            padding: 20px;
            min-height: 145px;
            box-shadow: 0 3px 12px rgba(23,43,58,0.035);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }

        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 28px rgba(23,43,58,0.09);
            border-color: #B8DED7;
        }

        .metric-label {
            color: #758494;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.7px;
        }

        .metric-value {
            font-size: clamp(21px, 2.2vw, 29px);
            font-weight: 800;
            color: #172B3A;
            margin-top: 17px;
            letter-spacing: -0.8px;
        }

        .metric-footer {
            font-size: 11px;
            color: #8997A4;
            margin-top: 5px;
        }

        .metric-accent {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, #159D91, #6AD6B9);
        }

        .insight-panel {
            background: linear-gradient(120deg, #172B3A, #24495A);
            border-radius: 16px;
            padding: 22px 24px;
            color: white;
            margin: 10px 0;
            box-shadow: 0 7px 22px rgba(23,43,58,0.10);
        }

        .insight-title {
            color: #FFFFFF;
            font-size: 15px;
            font-weight: 800;
            margin-bottom: 12px;
        }

        .insight-text {
            color: #C8D9E1;
            font-size: 13px;
            line-height: 1.8;
        }

        .insight-highlight {
            color: #65D7B5;
            font-weight: 700;
        }

        div[data-testid="stPlotlyChart"] {
            background: #FFFFFF;
            padding: 12px;
            border-radius: 15px;
            border: 1px solid #E7EDF2;
            box-shadow: 0 3px 12px rgba(23,43,58,0.025);
        }

        div[data-testid="stDataFrame"] {
            background: #FFFFFF;
            border-radius: 13px;
            border: 1px solid #E7EDF2;
            overflow: hidden;
        }

        div[data-testid="stMarkdownContainer"] p strong {
            color: #172B3A !important;
            font-size: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
