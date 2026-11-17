import os
from datetime import datetime
import streamlit as st

from modules.config import FILE_PATH, inject_custom_css
from modules.data_loader import load_and_process_data, make_excel_download
from modules.components import money, number, safe_html, section_heading, metric_card
from modules.charts import (
    build_revenue_trend_chart,
    build_top_customers_chart,
    build_fleet_donut_chart,
)

st.set_page_config(
    page_title="SIM Revenue Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

if not os.path.exists(FILE_PATH):
    st.error(f"Workbook not found: {FILE_PATH}. Place the Excel file in the root directory.")
    st.stop()

last_modified = os.path.getmtime(FILE_PATH)
last_updated = datetime.fromtimestamp(last_modified).strftime("%d %b %Y, %I:%M %p")
df_customers, df_monthly = load_and_process_data(FILE_PATH, last_modified)

# --- SIDEBAR ---
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
    available_years = sorted(df_customers["Schedule Year"].unique().tolist())
    selected_years = st.multiselect("Reporting Years", options=available_years, default=available_years)

    all_customers = sorted(df_customers["Customer Name"].unique().tolist())
    selected_customers = st.multiselect("Customers", options=all_customers, default=[], placeholder="All customers")

    top_n = st.slider("Top Customers to Display", 5, 20, 10, 1)
    show_data_labels = st.toggle("Show chart data labels", value=True)

    if st.button("↻  Refresh Workbook", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- FILTERING ---
filtered_cust = df_customers[df_customers["Schedule Year"].isin(selected_years)].copy()
filtered_monthly = df_monthly[df_monthly["Schedule Year"].isin(selected_years)].copy()

if selected_customers:
    filtered_cust = filtered_cust[filtered_cust["Customer Name"].isin(selected_customers)]
    filtered_monthly = filtered_monthly[filtered_monthly["Customer Name"].isin(selected_customers)]

if filtered_cust.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# --- HEADER ---
st.markdown(
    f"""
    <div class="dashboard-header">
        <div>
            <div class="header-title">Revenue Intelligence</div>
            <div class="header-subtitle">
                SIM Connectivity Financial Performance &amp; Customer Analytics
                <br>Reporting period: {min(selected_years) if selected_years else "—"} – {max(selected_years) if selected_years else "—"}
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

# --- KPI METRICS (Using correct 55 baseline SIM count) ---
total_revenue = filtered_cust["Total"].sum()
# Using max SIM allocation per customer to reflect the true 55 baseline active fleet
total_sims = int(filtered_cust.groupby("Customer Name")["No. of SIM Cards"].max().sum())
unique_customers = filtered_cust["Customer Name"].nunique()
average_yield = total_revenue / total_sims if total_sims > 0 else 0

section_heading("Executive Overview", "A consolidated snapshot of your connectivity business performance.")
cols = st.columns(4)
metrics = [
    ("Total Scheduled Revenue", money(total_revenue), "₵", "Combined scheduled revenue"),
    ("Active SIM Fleet", number(total_sims), "▣", "Total active unique SIMs"),
    ("Customer Accounts", number(unique_customers), "♙", "Unique customer accounts"),
    ("Average Yield per SIM", money(average_yield), "↗", "Average scheduled revenue per SIM"),
]
for i, (label, val, icon, footer) in enumerate(metrics):
    with cols[i]:
        metric_card(label, val, icon, footer, delay=i * 0.1)

# --- CHARTS ---
section_heading("Revenue Analytics", "Explore scheduled revenue trends and customer contributions.")
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("**Monthly Revenue Trajectory**")
    st.plotly_chart(build_revenue_trend_chart(filtered_monthly), use_container_width=True, config={"displayModeBar": False})
with c2:
    st.markdown("**Top Revenue Contributors**")
    st.plotly_chart(build_top_customers_chart(filtered_cust, top_n, show_data_labels), use_container_width=True, config={"displayModeBar": False})

c3, _ = st.columns(2, gap="large")
with c3:
    st.markdown("**SIM Fleet Distribution**")
    fig_pie = build_fleet_donut_chart(filtered_cust, total_sims)
    if fig_pie:
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

# --- DETAILED RECORDS TABLE ---
st.divider()
section_heading("Detailed Schedule Records", "Review individual customer schedule records.")
search_term = st.text_input("Search customer records", placeholder="Type a customer name...")
table_df = filtered_cust.copy()
if search_term.strip():
    table_df = table_df[table_df["Customer Name"].str.contains(search_term.strip(), case=False, na=False)]

st.dataframe(
    table_df[["Schedule Year", "Customer Name", "No. of SIM Cards", "Connectivity Unit Price (per month)", "Start Month", "Total"]],
    use_container_width=True,
    hide_index=True,
)