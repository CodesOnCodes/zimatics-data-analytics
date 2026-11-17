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
    """Inject executive theme CSS into the Streamlit app."""
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

        .sidebar-brand {
            padding: 12px 0 22px 0;
            border-bottom: 1px solid rgba(255,255,255,0.13);
            margin-bottom: 24px;
        }

        .brand-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 43px;
            height: 43px;
            background: linear-gradient(135deg, #159D91, #35C6A8);
            border-radius: 13px;
            font-size: 21px;
            margin-bottom: 12px;
            box-shadow: 0 6px 20px rgba(21,157,145,0.25);
        }

        .brand-name {
            font-size: 19px;
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
        }

        .metric-label {
            color: #758494;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .metric-value {
            font-size: clamp(21px, 2.2vw, 29px);
            font-weight: 800;
            color: #172B3A;
            margin-top: 17px;
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

        div[data-testid="stMarkdownContainer"] p strong {
            color: #172B3A !important;
            font-size: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )