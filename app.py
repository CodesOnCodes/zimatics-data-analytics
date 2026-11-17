import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- PAGE CONFIGURATION & PROFESSIONAL THEME ---
st.set_page_config(
    page_title="SIM Connectivity Revenue Dashboard",
    page_icon="chart_with_upwards_trend",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main { background-color: #f8f9fa; }
        .stMetric { background-color: #ffffff; padding: 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; }
        h1, h2, h3 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #111827; }
        .stDataFrame { border-radius: 8px; border: 1px solid #e5e7eb; }
    </style>
    """,
    unsafe_allow_html=True,
)

FILE_PATH = "SIM_Connectivity_2026-2030.xlsx"
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

@st.cache_data
def load_and_process_data(file_path: str, file_mtime: float):
    xls = pd.ExcelFile(file_path)
    all_records = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=4)
        df = df[
            df["Customer Name"].notna()
            & (df["Customer Name"].astype(str).str.strip().str.upper() != "TOTAL")
        ].copy()

        if df.empty:
            continue

        df["Schedule Year"] = int(sheet_name)
        for m in MONTHS:
            df[m] = pd.to_numeric(df[m], errors="coerce").fillna(0)

        df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
        df["No. of SIM Cards"] = pd.to_numeric(df["No. of SIM Cards"], errors="coerce").fillna(0)
        df["Connectivity Unit Price (per month)"] = pd.to_numeric(
            df["Connectivity Unit Price (per month)"], errors="coerce"
        ).fillna(0)

        all_records.append(df)

    if not all_records:
        return pd.DataFrame(), pd.DataFrame()

    combined_df = pd.concat(all_records, ignore_index=True)

    monthly_df = combined_df.melt(
        id_vars=["Schedule Year", "Customer Name", "No. of SIM Cards", "Connectivity Unit Price (per month)"],
        value_vars=MONTHS,
        var_name="Month",
        value_name="Revenue",
    )
    monthly_df["Month Num"] = monthly_df["Month"].apply(lambda m: MONTHS.index(m) + 1)
    monthly_df["Date"] = pd.to_datetime(
        monthly_df["Schedule Year"].astype(str)
        + "-"
        + monthly_df["Month Num"].astype(str).str.zfill(2)
        + "-01"
    )

    return combined_df, monthly_df

if not os.path.exists(FILE_PATH):
    st.error("The workbook file SIM_Connectivity_2026-2030.xlsx was not found in the directory.")
    st.stop()

last_modified = os.path.getmtime(FILE_PATH)
last_updated_str = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M:%S")

df_customers, df_monthly = load_and_process_data(FILE_PATH, last_modified)

# --- HEADER SECTION ---
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.title("SIM Connectivity Revenue Analytics")
    st.markdown(f"Financial schedule tracker linked to `{FILE_PATH}`. Last modified: **{last_updated_str}**")
with header_col2:
    if st.button("Refresh Data", use_container_width=True):
        st.rerun()

st.divider()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Configuration")
available_years = sorted(df_customers["Schedule Year"].unique())
selected_years = st.sidebar.multiselect("Schedule Years", options=available_years, default=available_years)

all_customers = sorted(df_customers["Customer Name"].unique())
selected_customers = st.sidebar.multiselect("Filter Customers", options=all_customers)

filtered_cust = df_customers[df_customers["Schedule Year"].isin(selected_years)]
filtered_monthly = df_monthly[df_monthly["Schedule Year"].isin(selected_years)]

if selected_customers:
    filtered_cust = filtered_cust[filtered_cust["Customer Name"].isin(selected_customers)]
    filtered_monthly = filtered_monthly[filtered_monthly["Customer Name"].isin(selected_customers)]

# --- EXECUTIVE METRICS ---
total_rev = filtered_cust["Total"].sum()
active_sims = int(filtered_cust["No. of SIM Cards"].sum())
unique_clients = filtered_cust["Customer Name"].nunique()
avg_revenue_per_sim = total_rev / active_sims if active_sims > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Scheduled Revenue", f"${total_rev:,.2f}")
m2.metric("Total SIM Cards Allocated", f"{active_sims:,}")
m3.metric("Active Customer Accounts", f"{unique_clients}")
m4.metric("Average Yield per SIM", f"${avg_revenue_per_sim:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# --- ADVANCED GRAPHICAL SECTION ---
chart_row1_col1, chart_row1_col2 = st.columns(2)

with chart_row1_col1:
    st.subheader("Monthly Revenue Trajectory")
    ts_data = (
        filtered_monthly.groupby(["Date", "Schedule Year"], as_index=False)["Revenue"]
        .sum()
        .sort_values("Date")
    )
    
    fig_trend = px.area(
        ts_data,
        x="Date",
        y="Revenue",
        color="Schedule Year",
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"Revenue": "Monthly Revenue ($)", "Date": "Timeline"},
    )
    fig_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_trend.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f0f2f6")
    fig_trend.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f0f2f6")
    st.plotly_chart(fig_trend, use_container_width=True)

with chart_row1_col2:
    st.subheader("Top Revenue Contributors")
    cust_summary = (
        filtered_cust.groupby("Customer Name", as_index=False)
        .agg({"Total": "sum", "No. of SIM Cards": "sum"})
        .sort_values("Total", ascending=True)
        .tail(10)
    )
    
    fig_cust = px.bar(
        cust_summary,
        x="Total",
        y="Customer Name",
        orientation="h",
        text="Total",
        color="Total",
        color_continuous_scale="Blues",
        labels={"Total": "Total Revenue ($)", "Customer Name": ""},
    )
    fig_cust.update_traces(texttemplate="$%{text:,.0f}", textposition="inside", insidetextanchor="end")
    fig_cust.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        coloraxis_showscale=False
    )
    fig_cust.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f0f2f6")
    st.plotly_chart(fig_cust, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- SECONDARY ANALYTICS ROW ---
chart_row2_col1, chart_row2_col2 = st.columns(2)

with chart_row2_col1:
    st.subheader("SIM Fleet Concentration by Client")
    fleet_data = filtered_cust.groupby("Customer Name", as_index=False)["No. of SIM Cards"].sum()
    fleet_data = fleet_data[fleet_data["No. of SIM Cards"] > 0].sort_values("No. of SIM Cards", ascending=False)

    fig_pie = px.pie(
        fleet_data,
        names="Customer Name",
        values="No. of SIM Cards",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_row2_col2:
    st.subheader("Pricing Tiers vs SIM Volume")
    fig_scatter = px.scatter(
        filtered_cust[filtered_cust["No. of SIM Cards"] > 0],
        x="No. of SIM Cards",
        y="Connectivity Unit Price (per month)",
        size="Total",
        color="Customer Name",
        hover_name="Customer Name",
        labels={
            "No. of SIM Cards": "Number of SIM Cards",
            "Connectivity Unit Price (per month)": "Unit Price ($/month)"
        },
    )
    fig_scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False
    )
    fig_scatter.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f0f2f6")
    fig_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f0f2f6")
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# --- DATA TABLE VIEW ---
st.subheader("Detailed Schedule Records")
st.dataframe(
    filtered_cust[
        [
            "Schedule Year",
            "Customer Name",
            "No. of SIM Cards",
            "Connectivity Unit Price (per month)",
            "Start Year",
            "Start Month",
            "Months Paid (12 = 1 year)",
            "Total",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
