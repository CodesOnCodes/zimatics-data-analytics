
import os
import io
import html
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SIM Revenue Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

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


# ============================================================
# 2. CUSTOM CSS - HYBRID EXECUTIVE DESIGN
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --navy: #172B3A;
        --navy-light: #223D50;
        --teal: #159D91;
        --background: #F3F6F9;
        --surface: #FFFFFF;
        --text: #172B3A;
        --muted: #758494;
        --border: #E5EBF0;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--background);
    }

    /* Main workspace */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1600px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #172B3A 0%,
            #1D3748 65%,
            #142A39 100%
        );
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

    /* Main header */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        padding: 10px 0 20px 0;
        animation: fadeIn 0.7s ease both;
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
        box-shadow: 0 0 0 4px rgba(25,185,130,0.12);
    }

    /* Section titles */
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

    /* KPI cards */
    .metric-card {
        position: relative;
        background: #FFFFFF;
        border: 1px solid #E7EDF2;
        border-radius: 15px;
        padding: 20px;
        min-height: 145px;
        overflow: hidden;
        box-shadow: 0 3px 12px rgba(23,43,58,0.035);
        animation: slideUp 0.65s ease both;
        transition: transform 0.25s ease,
                    box-shadow 0.25s ease,
                    border-color 0.25s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(23,43,58,0.09);
        border-color: #B8DED7;
    }

    .metric-card::after {
        content: "";
        position: absolute;
        width: 100px;
        height: 100px;
        right: -35px;
        top: -35px;
        border-radius: 50%;
        background: rgba(21,157,145,0.055);
    }

    .metric-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 1;
    }

    .metric-label {
        color: #758494;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }

    .metric-icon {
        width: 35px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #E8F5F3;
        border-radius: 10px;
        font-size: 17px;
    }

    .metric-value {
        font-size: clamp(21px, 2.2vw, 29px);
        font-weight: 800;
        color: #172B3A;
        margin-top: 17px;
        letter-spacing: -0.8px;
        position: relative;
        z-index: 1;
        word-break: break-word;
    }

    .metric-footer {
        font-size: 11px;
        color: #8997A4;
        margin-top: 5px;
        position: relative;
        z-index: 1;
    }

    .metric-accent {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #159D91, #6AD6B9);
    }

    /* Insight panel */
    .insight-panel {
        background: linear-gradient(120deg, #172B3A, #24495A);
        border-radius: 16px;
        padding: 22px 24px;
        color: white;
        margin: 18px 0;
        box-shadow: 0 7px 22px rgba(23,43,58,0.10);
        animation: fadeIn 0.8s ease both;
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

    /* Chart containers */
    div[data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #E7EDF2;
        box-shadow: 0 3px 12px rgba(23,43,58,0.025);
        transition: box-shadow 0.25s ease;
    }

    div[data-testid="stPlotlyChart"]:hover {
        box-shadow: 0 8px 22px rgba(23,43,58,0.07);
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        background: #FFFFFF;
        border-radius: 13px;
        border: 1px solid #E7EDF2;
        overflow: hidden;
    }

    /* Buttons */
    .stButton button,
    .stDownloadButton button {
        border-radius: 9px;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    .stButton button:hover,
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 13px rgba(21,157,145,0.15);
    }

    /* Dividers */
    hr {
        border-color: #E5EBF0;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(18px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.8rem 2rem 0.8rem;
        }

        .metric-card {
            padding: 15px;
        }

        .header-title {
            font-size: 25px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def money(value):
    """Format financial values in Ghana cedis."""
    return f"{CURRENCY} {value:,.2f}"


def number(value):
    return f"{value:,.0f}"


def safe_html(value):
    return html.escape(str(value))


def section_heading(title, description=""):
    st.markdown(
        f"""
        <div class="section-heading">{safe_html(title)}</div>
        <div class="section-description">{safe_html(description)}</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, icon, footer, delay=0):
    st.markdown(
        f"""
        <div class="metric-card" style="animation-delay:{delay}s">
            <div class="metric-top">
                <div class="metric-label">{safe_html(label)}</div>
                <div class="metric-icon">{icon}</div>
            </div>
            <div class="metric-value">{safe_html(value)}</div>
            <div class="metric-footer">{safe_html(footer)}</div>
            <div class="metric-accent"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig, height=350):
    """Apply a consistent executive chart theme."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(
            family="DM Sans, sans-serif",
            color=COLORS["text"],
            size=11,
        ),
        margin=dict(l=15, r=20, t=35, b=25),
        hoverlabel=dict(
            bgcolor=COLORS["navy"],
            font_color="white",
            font_size=12,
        ),
        transition=dict(duration=650, easing="cubic-in-out"),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EDF1F5",
        zeroline=False,
        showline=False,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EDF1F5",
        zeroline=False,
        showline=False,
    )

    return fig


def make_excel_download(dataframe):
    """Generate an Excel file in memory."""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            sheet_name="Filtered Records",
            index=False,
        )

    output.seek(0)
    return output.getvalue()


# ============================================================
# 4. DATA LOADING AND PROCESSING
# ============================================================

@st.cache_data(show_spinner="Loading connectivity records...")
def load_and_process_data(file_path, file_mtime):

    xls = pd.ExcelFile(file_path)
    all_records = []

    required_columns = [
        "Customer Name",
        "No. of SIM Cards",
        "Connectivity Unit Price (per month)",
    ]

    for sheet_name in xls.sheet_names:

        # Only process sheets with numeric year names.
        try:
            year = int(str(sheet_name).strip())
        except ValueError:
            continue

        df = pd.read_excel(
            xls,
            sheet_name=sheet_name,
            header=4,
        )

        df.columns = df.columns.astype(str).str.strip()

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            st.warning(
                f"Skipping {sheet_name}: missing columns "
                + ", ".join(missing)
            )
            continue

        # Remove blank customers and total rows.
        customer_names = (
            df["Customer Name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df = df[
            (customer_names != "")
            & (customer_names.str.upper() != "TOTAL")
        ].copy()

        if df.empty:
            continue

        df["Customer Name"] = customer_names.loc[df.index]
        df["Schedule Year"] = year

        # Clean numeric fields.
        numeric_columns = [
            "No. of SIM Cards",
            "Connectivity Unit Price (per month)",
            "Total",
        ] + MONTHS

        for col in numeric_columns:
            if col not in df.columns:
                df[col] = 0

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            ).fillna(0)

        # If the workbook has no Total column values,
        # calculate total from the monthly revenue columns.
        monthly_total = df[MONTHS].sum(axis=1)

        df["Total"] = df["Total"].where(
            df["Total"] != 0,
            monthly_total,
        )

        all_records.append(df)

    if not all_records:
        return pd.DataFrame(), pd.DataFrame()

    combined_df = pd.concat(
        all_records,
        ignore_index=True,
    )

    monthly_df = combined_df.melt(
        id_vars=[
            "Schedule Year",
            "Customer Name",
            "No. of SIM Cards",
            "Connectivity Unit Price (per month)",
        ],
        value_vars=MONTHS,
        var_name="Month",
        value_name="Revenue",
    )

    monthly_df["Month Num"] = (
        monthly_df["Month"].map(
            {month: i + 1 for i, month in enumerate(MONTHS)}
        )
    )

    monthly_df["Date"] = pd.to_datetime(
        monthly_df["Schedule Year"].astype(str)
        + "-"
        + monthly_df["Month Num"].astype(str).str.zfill(2)
        + "-01"
    )

    return combined_df, monthly_df


# ============================================================
# 5. VALIDATE AND LOAD WORKBOOK
# ============================================================

if not os.path.exists(FILE_PATH):

    st.error(
        f"Workbook not found: {FILE_PATH}. "
        "Place the Excel workbook in the same directory as app.py."
    )

    st.stop()


last_modified = os.path.getmtime(FILE_PATH)

last_updated = datetime.fromtimestamp(
    last_modified
).strftime("%d %b %Y, %I:%M %p")


try:

    df_customers, df_monthly = load_and_process_data(
        FILE_PATH,
        last_modified,
    )

except Exception as error:

    st.error(f"Unable to process the workbook: {error}")
    st.stop()


if df_customers.empty:

    st.error(
        "No valid customer records were found. "
        "Check your Excel sheet names and header positions."
    )

    st.stop()


# ============================================================
# 6. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-icon">◈</div>
            <div class="brand-name">SIM INTELLIGENCE</div>
            <div class="brand-caption">Revenue Analytics Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Dashboard Controls</div>',
        unsafe_allow_html=True,
    )

    available_years = sorted(
        df_customers["Schedule Year"].unique().tolist()
    )

    selected_years = st.multiselect(
        "Reporting Years",
        options=available_years,
        default=available_years,
        help="Choose the schedule years to include.",
    )

    all_customers = sorted(
        df_customers["Customer Name"].unique().tolist()
    )

    selected_customers = st.multiselect(
        "Customers",
        options=all_customers,
        default=[],
        placeholder="All customers",
    )

    st.markdown(
        '<div class="sidebar-section">Analysis Settings</div>',
        unsafe_allow_html=True,
    )

    top_n = st.slider(
        "Top Customers to Display",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
    )

    show_data_labels = st.toggle(
        "Show chart data labels",
        value=True,
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-section">Data Management</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "↻  Refresh Workbook",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        f"""
        <div style="margin-top:22px; font-size:11px; color:#9DB2C0;">
            <div style="font-weight:700; color:#D9E6ED;">
                SOURCE WORKBOOK
            </div>
            <div style="margin-top:6px; word-break:break-word;">
                {safe_html(FILE_PATH)}
            </div>
            <div style="margin-top:13px;">
                Last updated
            </div>
            <div style="color:#FFFFFF; margin-top:3px;">
                {safe_html(last_updated)}
            </div>
            <div style="margin-top:20px; opacity:0.7;">
                SIM Revenue Intelligence · 2026
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 7. FILTER DATA
# ============================================================

filtered_cust = df_customers[
    df_customers["Schedule Year"].isin(selected_years)
].copy()

filtered_monthly = df_monthly[
    df_monthly["Schedule Year"].isin(selected_years)
].copy()

if selected_customers:

    filtered_cust = filtered_cust[
        filtered_cust["Customer Name"].isin(selected_customers)
    ]

    filtered_monthly = filtered_monthly[
        filtered_monthly["Customer Name"].isin(selected_customers)
    ]


if filtered_cust.empty:

    st.warning(
        "No records match the selected filters. "
        "Please select at least one reporting year and review your customer selection."
    )

    st.stop()


# ============================================================
# 8. HEADER
# ============================================================

st.markdown(
    f"""
    <div class="dashboard-header">
        <div>
            <div class="header-title">
                Revenue Intelligence
            </div>
            <div class="header-subtitle">
                SIM Connectivity Financial Performance &amp; Customer Analytics
                <br>
                Reporting period: {min(selected_years) if selected_years else "—"}
                – {max(selected_years) if selected_years else "—"}
            </div>
        </div>
        <div class="status-pill">
            <span class="status-dot"></span>
            WORKBOOK CONNECTED
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# 9. EXECUTIVE METRICS
# ============================================================

total_revenue = filtered_cust["Total"].sum()

total_sims = int(
    filtered_cust["No. of SIM Cards"].sum()
)

unique_customers = (
    filtered_cust["Customer Name"].nunique()
)

average_yield = (
    total_revenue / total_sims
    if total_sims > 0 else 0
)

average_customer_revenue = (
    total_revenue / unique_customers
    if unique_customers > 0 else 0
)

section_heading(
    "Executive Overview",
    "A consolidated snapshot of your connectivity business performance."
)

metric_cols = st.columns(4)

metrics = [
    (
        "Total Scheduled Revenue",
        money(total_revenue),
        "₵",
        "Combined scheduled revenue",
    ),
    (
        "SIM Cards Allocated",
        number(total_sims),
        "▣",
        "Total allocated SIM fleet",
    ),
    (
        "Customer Accounts",
        number(unique_customers),
        "♙",
        "Unique customer accounts",
    ),
    (
        "Average Yield per SIM",
        money(average_yield),
        "↗",
        "Average scheduled revenue per SIM",
    ),
]

for i, (label, value, icon, footer) in enumerate(metrics):

    with metric_cols[i]:

        metric_card(
            label,
            value,
            icon,
            footer,
            delay=i * 0.1,
        )


# ============================================================
# 10. YEAR-ON-YEAR PERFORMANCE
# ============================================================

yearly_summary = (
    filtered_cust.groupby("Schedule Year", as_index=False)
    .agg(
        Revenue=("Total", "sum"),
        SIMs=("No. of SIM Cards", "sum"),
        Customers=("Customer Name", "nunique"),
    )
    .sort_values("Schedule Year")
)

yearly_summary["Revenue Change"] = (
    yearly_summary["Revenue"].pct_change() * 100
)

latest_year = yearly_summary.iloc[-1]

if len(yearly_summary) >= 2:

    previous_year = yearly_summary.iloc[-2]

    revenue_change = (
        (latest_year["Revenue"] - previous_year["Revenue"])
        / abs(previous_year["Revenue"]) * 100
        if previous_year["Revenue"] != 0
        else None
    )

    sim_change = (
        latest_year["SIMs"] - previous_year["SIMs"]
    )

else:

    revenue_change = None
    sim_change = None


section_heading(
    "Performance Insights",
    "Yearly comparisons and automatically generated business observations."
)

insight_cols = st.columns([1.4, 1, 1])

with insight_cols[0]:

    if revenue_change is not None:

        change_description = (
            f"{abs(revenue_change):,.1f}% "
            + ("higher" if revenue_change >= 0 else "lower")
        )

        change_color = (
            "positive" if revenue_change >= 0 else "negative"
        )

    else:

        change_description = "Not enough yearly data"
        change_color = "neutral"

    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="insight-title">
                ◈ Revenue Performance
            </div>
            <div class="insight-text">
                The latest selected schedule year,
                <span class="insight-highlight">
                    {int(latest_year["Schedule Year"])}
                </span>,
                records scheduled revenue of
                <span class="insight-highlight">
                    {money(latest_year["Revenue"])}
                </span>.
                <br><br>
                Compared with the preceding selected year,
                the revenue is
                <span class="insight-highlight">
                    {change_description}
                </span>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with insight_cols[1]:

    st.markdown(
        f"""
        <div class="metric-card" style="min-height:160px;">
            <div class="metric-label">Average Customer Revenue</div>
            <div class="metric-value" style="font-size:23px;">
                {money(average_customer_revenue)}
            </div>
            <div class="metric-footer">
                Average across selected customer accounts
            </div>
            <div class="metric-accent"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with insight_cols[2]:

    st.markdown(
        f"""
        <div class="metric-card" style="min-height:160px;">
            <div class="metric-label">Latest Year SIM Fleet</div>
            <div class="metric-value" style="font-size:23px;">
                {number(latest_year["SIMs"])}
            </div>
            <div class="metric-footer">
                SIM cards in {int(latest_year["Schedule Year"])}
            </div>
            <div class="metric-accent"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 11. REVENUE TREND
# ============================================================

section_heading(
    "Revenue Analytics",
    "Explore scheduled revenue trends, customer contributions and financial performance."
)

chart1, chart2 = st.columns(2, gap="large")

with chart1:

    st.markdown("**Monthly Revenue Trajectory**")

    ts_data = (
        filtered_monthly.groupby(
            ["Date", "Schedule Year"],
            as_index=False,
        )["Revenue"]
        .sum()
        .sort_values("Date")
    )

    fig_trend = go.Figure()

    palette = [
        "#159D91",
        "#4786C6",
        "#E9B949",
        "#9368C8",
        "#E17C70",
    ]

    for i, year in enumerate(sorted(ts_data["Schedule Year"].unique())):

        year_data = ts_data[
            ts_data["Schedule Year"] == year
        ]

        fig_trend.add_trace(
            go.Scatter(
                x=year_data["Date"],
                y=year_data["Revenue"],
                name=str(year),
                mode="lines+markers",
                line=dict(
                    color=palette[i % len(palette)],
                    width=3,
                    shape="spline",
                ),
                marker=dict(size=5),
                fill="tozeroy",
                fillcolor="rgba(21,157,145,0.045)",
                hovertemplate=(
                    "<b>%{x|%b %Y}</b><br>"
                    "Revenue: GH₵ %{y:,.2f}"
                    "<extra></extra>"
                ),
            )
        )

    fig_trend.update_layout(
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=1.15,
            x=0,
        ),
        yaxis_title="Revenue (GH₵)",
        xaxis_title="",
    )

    fig_trend = style_figure(fig_trend, 390)

    st.plotly_chart(
        fig_trend,
        use_container_width=True,
        config={"displayModeBar": False},
        key="revenue_trend",
    )


with chart2:

    st.markdown("**Top Revenue Contributors**")

    customer_summary = (
        filtered_cust.groupby("Customer Name", as_index=False)
        .agg(
            Revenue=("Total", "sum"),
            SIMs=("No. of SIM Cards", "sum"),
        )
        .sort_values("Revenue", ascending=False)
        .head(top_n)
        .sort_values("Revenue", ascending=True)
    )

    fig_customers = px.bar(
        customer_summary,
        x="Revenue",
        y="Customer Name",
        orientation="h",
        text="Revenue" if show_data_labels else None,
        color="Revenue",
        color_continuous_scale=[
            "#DDF4EF",
            "#159D91",
            "#176B67",
        ],
        labels={
            "Revenue": "Revenue (GH₵)",
            "Customer Name": "",
        },
    )

    if show_data_labels:

        fig_customers.update_traces(
            texttemplate="GH₵ %{text:,.0f}",
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(color="white", size=10),
        )

    fig_customers.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(automargin=True),
    )

    fig_customers = style_figure(
        fig_customers,
        max(350, len(customer_summary) * 38),
    )

    st.plotly_chart(
        fig_customers,
        use_container_width=True,
        config={"displayModeBar": False},
        key="customer_revenue",
    )


# ============================================================
# 12. CUSTOMER AND SIM ANALYTICS
# ============================================================

section_heading(
    "Customer & Fleet Intelligence",
    "Understand customer concentration, fleet distribution and unit pricing."
)

chart3, chart4 = st.columns(2, gap="large")


with chart3:

    st.markdown("**SIM Fleet Distribution**")

    fleet_data = (
        filtered_cust.groupby("Customer Name", as_index=False)
        ["No. of SIM Cards"]
        .sum()
    )

    fleet_data = fleet_data[
        fleet_data["No. of SIM Cards"] > 0
    ].sort_values(
        "No. of SIM Cards",
        ascending=False,
    )

    # Show the leading customers separately and group
    # the remaining customers as Others.
    if len(fleet_data) > 8:

        top_fleet = fleet_data.head(7)

        others = pd.DataFrame({
            "Customer Name": ["Others"],
            "No. of SIM Cards": [
                fleet_data.iloc[7:]["No. of SIM Cards"].sum()
            ],
        })

        fleet_display = pd.concat(
            [top_fleet, others],
            ignore_index=True,
        )

    else:

        fleet_display = fleet_data

    if not fleet_display.empty:

        fig_pie = px.pie(
            fleet_display,
            names="Customer Name",
            values="No. of SIM Cards",
            hole=0.63,
            color_discrete_sequence=[
                "#159D91",
                "#4786C6",
                "#E9B949",
                "#9368C8",
                "#E17C70",
                "#4CA6A8",
                "#6C8799",
                "#C1CDD5",
            ],
        )

        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent",
            hole=0.63,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "SIM Cards: %{value:,.0f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            ),
        )

        fig_pie.add_annotation(
            text=(
                f"<b>{number(total_sims)}</b>"
                "<br><span style='font-size:10px'>TOTAL SIMS</span>"
            ),
            showarrow=False,
            font=dict(
                size=17,
                color=COLORS["navy"],
            ),
        )

        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                y=-0.12,
                x=0.5,
                xanchor="center",
            ),
        )

        fig_pie = style_figure(fig_pie, 390)

        st.plotly_chart(
            fig_pie,
            use_container_width=True,
            config={"displayModeBar": False},
            key="sim_distribution",
        )

    else:

        st.info("No SIM fleet data is available for this selection.")


with chart4:

    st.markdown("**Unit Pricing vs SIM Volume**")

    scatter_data = filtered_cust[
        filtered_cust["No. of SIM Cards"] > 0
    ].copy()

    if not scatter_data.empty:

        fig_scatter = px.scatter(
            scatter_data,
            x="No. of SIM Cards",
            y="Connectivity Unit Price (per month)",
            size="Total",
            color="Schedule Year",
            hover_name="Customer Name",
            size_max=35,
            color_discrete_sequence=palette,
            labels={
                "No. of SIM Cards": "SIM Cards",
                "Connectivity Unit Price (per month)": "Unit Price (GH₵)",
                "Schedule Year": "Year",
            },
        )

        fig_scatter.update_traces(
            marker=dict(
                opacity=0.78,
                line=dict(
                    width=1,
                    color="white",
                ),
            ),
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "SIM Cards: %{x:,.0f}<br>"
                "Unit Price: GH₵ %{y:,.2f}"
                "<extra></extra>"
            ),
        )

        fig_scatter.update_layout(
            legend=dict(
                orientation="h",
                y=1.12,
                x=0,
            ),
        )

        fig_scatter = style_figure(fig_scatter, 390)

        st.plotly_chart(
            fig_scatter,
            use_container_width=True,
            config={"displayModeBar": False},
            key="pricing_analysis",
        )

    else:

        st.info("No SIM pricing data is available for this selection.")


# ============================================================
# 13. YEARLY REVENUE COMPARISON
# ============================================================

section_heading(
    "Annual Financial Performance",
    "Compare scheduled revenue and SIM allocation across reporting years."
)

annual_col1, annual_col2 = st.columns(
    [1.5, 1],
    gap="large",
)

with annual_col1:

    fig_annual = go.Figure()

    fig_annual.add_trace(
        go.Bar(
            x=yearly_summary["Schedule Year"].astype(str),
            y=yearly_summary["Revenue"],
            name="Revenue",
            marker=dict(
                color="#159D91",
                line=dict(width=0),
            ),
            text=[
                f"GH₵ {v:,.0f}"
                for v in yearly_summary["Revenue"]
            ] if show_data_labels else None,
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Revenue: GH₵ %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig_annual.update_layout(
        title="Revenue by Schedule Year",
        xaxis_title="Schedule Year",
        yaxis_title="Revenue (GH₵)",
        showlegend=False,
    )

    fig_annual = style_figure(fig_annual, 360)

    st.plotly_chart(
        fig_annual,
        use_container_width=True,
        config={"displayModeBar": False},
        key="annual_revenue",
    )


with annual_col2:

    fig_sims = px.bar(
        yearly_summary,
        x="Schedule Year",
        y="SIMs",
        color="SIMs",
        color_continuous_scale=[
            "#DDF4EF",
            "#159D91",
            "#176B67",
        ],
        text="SIMs" if show_data_labels else None,
        labels={
            "Schedule Year": "Year",
            "SIMs": "SIM Cards",
        },
    )

    if show_data_labels:

        fig_sims.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
        )

    fig_sims.update_layout(
        title="SIM Allocation by Year",
        coloraxis_showscale=False,
        showlegend=False,
    )

    fig_sims = style_figure(fig_sims, 360)

    st.plotly_chart(
        fig_sims,
        use_container_width=True,
        config={"displayModeBar": False},
        key="annual_sims",
    )


# ============================================================
# 14. MONTHLY REVENUE BREAKDOWN
# ============================================================

section_heading(
    "Monthly Revenue Breakdown",
    "Identify the strongest and weakest months across the selected schedule years."
)

monthly_pivot = (
    filtered_monthly.pivot_table(
        index="Month",
        columns="Schedule Year",
        values="Revenue",
        aggfunc="sum",
        fill_value=0,
    )
    .reindex(MONTHS)
)

fig_monthly = go.Figure()

for i, year in enumerate(monthly_pivot.columns):

    fig_monthly.add_trace(
        go.Bar(
            x=monthly_pivot.index,
            y=monthly_pivot[year],
            name=str(year),
            marker_color=palette[i % len(palette)],
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"Year: {year}<br>"
                "Revenue: GH₵ %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

fig_monthly.update_layout(
    barmode="group",
    xaxis_title="Month",
    yaxis_title="Revenue (GH₵)",
    legend=dict(
        orientation="h",
        y=1.12,
        x=0,
    ),
)

fig_monthly = style_figure(fig_monthly, 400)

st.plotly_chart(
    fig_monthly,
    use_container_width=True,
    config={"displayModeBar": False},
    key="monthly_comparison",
)


# ============================================================
# 15. CUSTOMER LEADERBOARD
# ============================================================

section_heading(
    "Customer Revenue Leaderboard",
    "Rank customers by total scheduled revenue and SIM fleet size."
)

leaderboard = (
    filtered_cust.groupby("Customer Name", as_index=False)
    .agg(
        Revenue=("Total", "sum"),
        SIMs=("No. of SIM Cards", "sum"),
        Unit_Price=("Connectivity Unit Price (per month)", "mean"),
    )
    .sort_values("Revenue", ascending=False)
    .reset_index(drop=True)
)

leaderboard.insert(
    0,
    "Rank",
    range(1, len(leaderboard) + 1),
)

leaderboard["Revenue Share (%)"] = (
    leaderboard["Revenue"] / total_revenue * 100
    if total_revenue != 0 else 0
)

leaderboard_display = leaderboard.copy()

leaderboard_display["Revenue"] = (
    leaderboard_display["Revenue"].map(money)
)

leaderboard_display["Unit_Price"] = (
    leaderboard_display["Unit_Price"].map(money)
)

leaderboard_display["SIMs"] = (
    leaderboard_display["SIMs"].map(number)
)

leaderboard_display["Revenue Share (%)"] = (
    leaderboard_display["Revenue Share (%)"].map(
        lambda x: f"{x:.2f}%"
    )
)

leaderboard_display = leaderboard_display.rename(
    columns={
        "Unit_Price": "Avg. Unit Price / Month",
        "Revenue": "Total Revenue",
        "SIMs": "SIM Cards",
    }
)

st.dataframe(
    leaderboard_display,
    use_container_width=True,
    hide_index=True,
    height=350,
)


# ============================================================
# 16. DETAILED RECORDS
# ============================================================

st.divider()

section_heading(
    "Detailed Schedule Records",
    "Review, search and export individual customer schedule records."
)

search_term = st.text_input(
    "Search customer records",
    placeholder="Type a customer name...",
)

display_df = filtered_cust.copy()

if search_term.strip():

    display_df = display_df[
        display_df["Customer Name"].str.contains(
            search_term.strip(),
            case=False,
            na=False,
        )
    ]

preferred_columns = [
    "Schedule Year",
    "Customer Name",
    "No. of SIM Cards",
    "Connectivity Unit Price (per month)",
    "Start Year",
    "Start Month",
    "Months Paid (12 = 1 year)",
    "Total",
]

available_columns = [
    col for col in preferred_columns
    if col in display_df.columns
]

table_df = display_df[available_columns].copy()

st.caption(
    f"Showing {len(table_df):,} of {len(filtered_cust):,} filtered records."
)

column_config = {
    "Schedule Year": st.column_config.NumberColumn(
        "Schedule Year",
        format="%d",
    ),
    "Customer Name": st.column_config.TextColumn(
        "Customer Name",
    ),
    "No. of SIM Cards": st.column_config.NumberColumn(
        "SIM Cards",
        format="%d",
    ),
    "Connectivity Unit Price (per month)": st.column_config.NumberColumn(
        "Unit Price / Month",
        format="GH₵ %.2f",
    ),
    "Total": st.column_config.NumberColumn(
        "Total Revenue",
        format="GH₵ %.2f",
    ),
    "Months Paid (12 = 1 year)": st.column_config.NumberColumn(
        "Months Paid",
        format="%d",
    ),
}

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    height=420,
    column_config=column_config,
)


# ============================================================
# 17. EXPORT CENTRE
# ============================================================

st.divider()

section_heading(
    "Export Centre",
    "Download the filtered financial records for reporting and further analysis."
)

export_col1, export_col2, export_col3 = st.columns(
    [1, 1, 2]
)

with export_col1:

    st.download_button(
        label="↓ Download Excel",
        data=make_excel_download(display_df),
        file_name="SIM_Revenue_Records.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
    )

with export_col2:

    csv_data = display_df.to_csv(
        index=False,
    ).encode("utf-8-sig")

    st.download_button(
        label="↓ Download CSV",
        data=csv_data,
        file_name="SIM_Revenue_Records.csv",
        mime="text/csv",
        use_container_width=True,
    )

with export_col3:

    st.markdown(
        f"""
        <div style="
            padding:11px 14px;
            background:#E8F5F3;
            border-radius:10px;
            color:#267C72;
            font-size:12px;
        ">
            <b>Export ready</b><br>
            {len(display_df):,} records ·
            {len(selected_years)} selected years ·
            Ghana cedi reporting
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 18. FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        padding:35px 10px 10px 10px;
        color:#94A2AE;
        font-size:11px;
    ">
        <div style="
            width:45px;
            height:3px;
            background:linear-gradient(90deg,#159D91,#6AD6B9);
            margin:0 auto 13px auto;
            border-radius:10px;
        "></div>
        <b style="color:#526878;">SIM REVENUE INTELLIGENCE</b>
        <br>
        Connectivity Analytics & Financial Reporting Platform
        <br><br>
        © 2026 · All rights reserved.
    </div>
    """,
    unsafe_allow_html=True,
)
