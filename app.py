import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="SIM Connectivity Revenue Dashboard",
    page_icon="📡",
    layout="wide",
)

FILE_PATH = "SIM_Connectivity_2026-2030.xlsx"
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# 1. Cache data using the file's last-modified timestamp as the cache key.
# Whenever SIM_Connectivity_2026-2030.xlsx is edited and saved, mtime changes
# and Streamlit automatically re-runs this function.
@st.cache_data
def load_workbook_data(file_path: str, file_mtime: float):
    xls = pd.ExcelFile(file_path)
    all_records = []

    for sheet_name in xls.sheet_names:
        # Row 5 in Excel (index 4 in pandas) contains the column headers
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=4)

        # Keep only actual customer rows (ignore blank rows and the TOTAL row)
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
        df["No. of SIM Cards"] = pd.to_numeric(
            df["No. of SIM Cards"], errors="coerce"
        ).fillna(0)
        df["Connectivity Unit Price (per month)"] = pd.to_numeric(
            df["Connectivity Unit Price (per month)"], errors="coerce"
        ).fillna(0)

        all_records.append(df)

    if not all_records:
        return pd.DataFrame(), pd.DataFrame()

    combined_df = pd.concat(all_records, ignore_index=True)

    # Reshape wide monthly columns into a clean time-series table for charting
    monthly_df = combined_df.melt(
        id_vars=["Schedule Year", "Customer Name", "No. of SIM Cards"],
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


# Check file existence and modification time
if not os.path.exists(FILE_PATH):
    st.error(f"Could not find `{FILE_PATH}` in the current directory.")
    st.stop()

last_modified = os.path.getmtime(FILE_PATH)
last_updated_str = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M:%S")

df_customers, df_monthly = load_workbook_data(FILE_PATH, last_modified)

# --- HEADER & REFRESH CONTROLS ---
col_title, col_refresh = st.columns([4, 1])
with col_title:
    st.title("📡 SIM Connectivity Revenue Schedule (2026–2030)")
    st.caption(f"Live linked to `{FILE_PATH}` • Last file update: **{last_updated_str}**")
with col_refresh:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

if df_customers.empty:
    st.warning("No customer records found in the workbook.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
available_years = sorted(df_customers["Schedule Year"].unique())
selected_years = st.sidebar.multiselect(
    "Select Schedule Years", options=available_years, default=available_years
)

all_customers = sorted(df_customers["Customer Name"].unique())
selected_customers = st.sidebar.multiselect(
    "Filter by Customer (leave empty for all)", options=all_customers
)

filtered_cust = df_customers[df_customers["Schedule Year"].isin(selected_years)]
filtered_monthly = df_monthly[df_monthly["Schedule Year"].isin(selected_years)]

if selected_customers:
    filtered_cust = filtered_cust[filtered_cust["Customer Name"].isin(selected_customers)]
    filtered_monthly = filtered_monthly[
        filtered_monthly["Customer Name"].isin(selected_customers)
    ]

# --- TOP KPI METRICS ---
total_rev = filtered_cust["Total"].sum()
active_sims = int(filtered_cust["No. of SIM Cards"].sum())
unique_clients = filtered_cust["Customer Name"].nunique()
incomplete_rows = filtered_cust[filtered_cust["Total"] == 0]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Scheduled Revenue", f"${total_rev:,.0f}")
kpi2.metric("Scheduled SIM-Years", f"{active_sims:,}")
kpi3.metric("Active Customers", f"{unique_clients}")
kpi4.metric("Incomplete / $0 Rows", f"{len(incomplete_rows)}")

st.divider()

# --- CHARTS ---
chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    st.subheader("Monthly Recurring Revenue Trajectory")
    ts_data = (
        filtered_monthly.groupby(["Date", "Schedule Year"], as_index=False)["Revenue"]
        .sum()
        .sort_values("Date")
    )
    # Trim trailing zero-only years if no data is entered for 2028-2030 yet
    active_dates = ts_data[ts_data["Revenue"] > 0]
    if not active_dates.empty:
        ts_data = ts_data[ts_data["Date"] <= active_dates["Date"].max()]

    fig_trend = px.bar(
        ts_data,
        x="Date",
        y="Revenue",
        color=ts_data["Schedule Year"].astype(str),
        labels={"Revenue": "Revenue ($)", "color": "Year"},
        text_auto="$.0f",
    )
    fig_trend.update_layout(xaxis_tickformat="%b %Y", hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)

with chart_col2:
    st.subheader("Revenue by Customer")
    cust_summary = (
        filtered_cust.groupby("Customer Name", as_index=False)
        .agg({"Total": "sum", "No. of SIM Cards": "sum"})
        .sort_values("Total", ascending=True)
    )
    fig_cust = px.bar(
        cust_summary,
        x="Total",
        y="Customer Name",
        orientation="h",
        text="Total",
        hover_data=["No. of SIM Cards"],
        labels={"Total": "Total Revenue ($)", "Customer Name": ""},
    )
    fig_cust.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig_cust, use_container_width=True)

# --- DATA AUDIT & DETAIL TABLE ---
if not incomplete_rows.empty:
    with st.expander(f"⚠️ Data Audit: {len(incomplete_rows)} Customer Rows Have $0 Revenue"):
        st.dataframe(
            incomplete_rows[
                [
                    "Schedule Year",
                    "Customer Name",
                    "No. of SIM Cards",
                    "Connectivity Unit Price (per month)",
                    "Start Month",
                    "Months Paid (12 = 1 year)",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

st.subheader("Detailed Schedule Table")
st.dataframe(
    filtered_cust[
        [
            "Schedule Year",
            "Customer Name",
            "No. of SIM Cards",
            "Connectivity Unit Price (per month)",
            "Start Month",
            "Months Paid (12 = 1 year)",
            "Total",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
