import os
from datetime import datetime
import pandas as pd
import streamlit as st

from modules.config import FILE_PATH, inject_custom_css
from modules.data_loader import load_and_process_data, calculate_active_sims, make_excel_download
from modules.components import money, number, safe_html, section_heading, metric_card
from modules.charts import (
    build_revenue_trend_chart,
    build_top_customers_chart,
    build_fleet_donut_chart,
    build_scatter_chart,
    build_annual_charts,
    build_monthly_comparison_chart,
)
from modules.analytics import calculate_renewal_forecast, compute_business_diagnostics

st.set_page_config(
    page_title="Zimatics | SIM Revenue Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

if not os.path.exists(FILE_PATH):
    st.error(f"Workbook not found: {FILE_PATH}. Place the Excel workbook in the same directory as app.py.")
    st.stop()

last_modified = os.path.getmtime(FILE_PATH)
last_updated = datetime.fromtimestamp(last_modified).strftime("%d %b %Y, %I:%M %p")

try:
    df_customers, df_monthly = load_and_process_data(FILE_PATH, last_modified)
except Exception as error:
    st.error(f"Unable to process the workbook: {error}")
    st.stop()

if df_customers.empty:
    st.error("No valid customer records were found. Check your Excel sheet names and header positions.")
    st.stop()

# --- SIDEBAR WITH ZIMATICS BRANDING ---
with st.sidebar:
    logo_path = "assets/zimatics_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=165)
    else:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-logo-badge">Z</div>
                <div class="brand-name">ZIMATICS</div>
                <div class="brand-caption">Revenue Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sidebar-section">Dashboard Controls</div>', unsafe_allow_html=True)

    available_years = sorted(df_customers["Schedule Year"].unique().tolist())
    selected_years = st.multiselect(
        "Reporting Years",
        options=available_years,
        default=available_years,
        help="Choose the schedule years to include.",
    )

    all_customers = sorted(df_customers["Customer Name"].unique().tolist())
    selected_customers = st.multiselect(
        "Customers",
        options=all_customers,
        default=[],
        placeholder="All customers",
    )

    st.markdown('<div class="sidebar-section">Analysis Settings</div>', unsafe_allow_html=True)
    top_n = st.slider("Top Customers to Display", min_value=5, max_value=20, value=14, step=1)
    show_data_labels = st.toggle("Show chart data labels", value=True)

    st.divider()
    st.markdown('<div class="sidebar-section">Data Management</div>', unsafe_allow_html=True)

    if st.button("Refresh Workbook", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        f"""
        <div style="margin-top:22px; font-size:11px; color:#9DB2C0;">
            <div style="font-weight:700; color:#D9E6ED;">SOURCE WORKBOOK</div>
            <div style="margin-top:6px; word-break:break-word;">{safe_html(FILE_PATH)}</div>
            <div style="margin-top:13px;">Last updated</div>
            <div style="color:#FFFFFF; margin-top:3px;">{safe_html(last_updated)}</div>
            <div style="margin-top:20px; opacity:0.7;">Zimatics Analytics · 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- FILTER DATA ---
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
            <div class="header-title">SIM Revenue Intelligence</div>
            <div class="header-subtitle">
                Zimatics Connectivity Financial Performance &amp; Customer Analytics
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

# --- EXECUTIVE METRICS ---
total_revenue = filtered_cust["Total"].sum()
total_sims = calculate_active_sims(filtered_cust, selected_years)
unique_customers = filtered_cust["Customer Name"].nunique()
average_yield = total_revenue / total_sims if total_sims > 0 else 0
average_customer_revenue = total_revenue / unique_customers if unique_customers > 0 else 0

section_heading("Executive Overview", "A consolidated snapshot of your connectivity business performance.")
metric_cols = st.columns(4)
metrics = [
    ("Total Scheduled Revenue", money(total_revenue), "₵", "Combined scheduled revenue"),
    ("Active Billed SIM Fleet", number(total_sims), "▣", "Active billed SIMs (excludes carry-overs)"),
    ("Customer Accounts", number(unique_customers), "♙", "All registered customer accounts"),
    ("Average Yield per SIM", money(average_yield), "↗", "Average scheduled revenue per billed SIM"),
]
for i, (label, value, icon, footer) in enumerate(metrics):
    with metric_cols[i]:
        metric_card(label, value, icon, footer, delay=i * 0.1)

st.markdown("<br>", unsafe_allow_html=True)

# --- INTERACTIVE ANALYTICAL TABS ---
tab_overview, tab_renewals, tab_simulator = st.tabs([
    "Executive Overview & Charts",
    "Subscription & Renewal Radar",
    "What-If Scenario Simulator",
])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW & CHARTS
# ==========================================
with tab_overview:
    yearly_summary = (
        filtered_cust.groupby("Schedule Year", as_index=False)
        .agg(
            Revenue=("Total", "sum"),
            SIMs=("Billed Sheet SIMs", "sum"),
            Customers=("Customer Name", "nunique"),
        )
        .sort_values("Schedule Year")
    )

    latest_year = yearly_summary.iloc[-1]
    if len(yearly_summary) >= 2:
        previous_year = yearly_summary.iloc[-2]
        revenue_change = (
            (latest_year["Revenue"] - previous_year["Revenue"]) / abs(previous_year["Revenue"]) * 100
            if previous_year["Revenue"] != 0
            else None
        )
    else:
        revenue_change = None

    diagnostics = compute_business_diagnostics(filtered_cust, total_revenue)

    section_heading("Performance & Risk Diagnostics", "Automated momentum tracking and portfolio concentration metrics.")
    insight_cols = st.columns([1.4, 1, 1])

    with insight_cols[0]:
        if revenue_change is not None:
            change_description = f"{abs(revenue_change):,.1f}% " + ("higher" if revenue_change >= 0 else "lower")
        else:
            change_description = "Single-year view selected"

        st.markdown(
            f"""
            <div class="insight-panel">
                <div class="insight-title">Portfolio Momentum &amp; Concentration</div>
                <div class="insight-text">
                    Latest year (<span class="insight-highlight">{int(latest_year["Schedule Year"])}</span>) scheduled revenue:
                    <span class="insight-highlight">{money(latest_year["Revenue"])}</span> ({change_description}).
                    <br><br>
                    Top client <span class="insight-highlight">{safe_html(diagnostics["top_client_name"])}</span> represents
                    <span class="insight-highlight">{diagnostics["top_client_share"]:.1f}%</span> of revenue, while top 3 clients account for
                    <span class="insight-highlight">{diagnostics["top_3_share"]:.1f}%</span> ({safe_html(diagnostics["risk_level"])}).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight_cols[1]:
        st.markdown(
            f"""
            <div class="metric-card" style="min-height:165px;">
                <div class="metric-label">Average Customer Revenue</div>
                <div class="metric-value" style="font-size:23px;">{money(average_customer_revenue)}</div>
                <div class="metric-footer">Across all {unique_customers} customer accounts</div>
                <div class="metric-accent"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight_cols[2]:
        st.markdown(
            f"""
            <div class="metric-card" style="min-height:165px;">
                <div class="metric-label">Latest Year Billed Fleet</div>
                <div class="metric-value" style="font-size:23px;">{number(latest_year["SIMs"])}</div>
                <div class="metric-footer">Billed SIM cards in {int(latest_year["Schedule Year"])}</div>
                <div class="metric-accent"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- REVENUE ANALYTICS ---
    section_heading("Revenue Analytics", "Explore scheduled revenue trends and customer contributions.")
    chart1, chart2 = st.columns(2, gap="large")
    with chart1:
        st.markdown("**Monthly Revenue Trajectory**")
        st.plotly_chart(build_revenue_trend_chart(filtered_monthly), use_container_width=True, config={"displayModeBar": False})
    with chart2:
        st.markdown("**Top Revenue Contributors**")
        st.plotly_chart(build_top_customers_chart(filtered_cust, top_n, show_data_labels), use_container_width=True, config={"displayModeBar": False})

    # --- CUSTOMER & FLEET INTELLIGENCE ---
    section_heading("Customer & Fleet Intelligence", "Understand customer concentration, fleet distribution and unit pricing.")
    chart3, chart4 = st.columns(2, gap="large")
    with chart3:
        st.markdown("**Active Billed SIM Fleet Distribution**")
        fig_pie = build_fleet_donut_chart(filtered_cust, total_sims)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No billed SIM fleet data is available for this selection.")

    with chart4:
        st.markdown("**Unit Pricing vs SIM Volume**")
        fig_scatter = build_scatter_chart(filtered_cust)
        if fig_scatter:
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No SIM pricing data is available for this selection.")

    # --- ANNUAL FINANCIAL PERFORMANCE ---
    section_heading("Annual Financial Performance", "Compare scheduled revenue and billed SIM allocation across reporting years.")
    annual_col1, annual_col2 = st.columns([1.5, 1], gap="large")
    fig_annual, fig_sims = build_annual_charts(yearly_summary, show_data_labels)
    with annual_col1:
        st.plotly_chart(fig_annual, use_container_width=True, config={"displayModeBar": False})
    with annual_col2:
        st.plotly_chart(fig_sims, use_container_width=True, config={"displayModeBar": False})

    # --- MONTHLY BREAKDOWN ---
    section_heading("Monthly Revenue Breakdown", "Identify the strongest and weakest months across the selected schedule years.")
    st.plotly_chart(build_monthly_comparison_chart(filtered_monthly), use_container_width=True, config={"displayModeBar": False})

    # --- PENDING BILLING AUDIT CALLOUT ---
    pending_rows = filtered_cust[filtered_cust["Total"] == 0]
    if not pending_rows.empty:
        with st.expander(f"Pending Billing Notice: {len(pending_rows)} Schedule Entries Currently Have GH₵ 0.00 Revenue"):
            st.dataframe(
                pending_rows[
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

    # --- CUSTOMER LEADERBOARD ---
    section_heading("Customer Revenue Leaderboard", "Rank all registered customers by total scheduled revenue and SIM fleet size.")
    leaderboard = (
        filtered_cust.groupby("Customer Name", as_index=False)
        .agg(
            Revenue=("Total", "sum"),
            SIMs=("Active Cohort SIMs", "sum"),
            Unit_Price=("Connectivity Unit Price (per month)", "mean"),
        )
        .sort_values("Revenue", ascending=False)
        .reset_index(drop=True)
    )
    leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))
    leaderboard["Revenue Share (%)"] = leaderboard["Revenue"] / total_revenue * 100 if total_revenue != 0 else 0

    leaderboard_display = leaderboard.copy()
    leaderboard_display["Revenue"] = leaderboard_display["Revenue"].map(money)
    leaderboard_display["Unit_Price"] = leaderboard_display["Unit_Price"].map(money)
    leaderboard_display["SIMs"] = leaderboard_display["SIMs"].map(number)
    leaderboard_display["Revenue Share (%)"] = leaderboard_display["Revenue Share (%)"].map(lambda x: f"{x:.2f}%")
    leaderboard_display = leaderboard_display.rename(
        columns={
            "Unit_Price": "Avg. Unit Price / Month",
            "Revenue": "Total Revenue",
            "SIMs": "Billed SIM Cards",
        }
    )
    st.dataframe(leaderboard_display, use_container_width=True, hide_index=True, height=420)

    # --- DETAILED RECORDS ---
    st.divider()
    section_heading("Detailed Schedule Records", "Review, search and export individual customer schedule records.")
    search_term = st.text_input("Search customer records", placeholder="Type a customer name...")
    display_df = filtered_cust.copy()
    if search_term.strip():
        display_df = display_df[display_df["Customer Name"].str.contains(search_term.strip(), case=False, na=False)]

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
    available_columns = [col for col in preferred_columns if col in display_df.columns]
    table_df = display_df[available_columns].copy()

    st.caption(f"Showing {len(table_df):,} of {len(filtered_cust):,} filtered records.")
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Schedule Year": st.column_config.NumberColumn("Schedule Year", format="%d"),
            "Customer Name": st.column_config.TextColumn("Customer Name"),
            "No. of SIM Cards": st.column_config.NumberColumn("SIM Cards", format="%d"),
            "Connectivity Unit Price (per month)": st.column_config.NumberColumn("Unit Price / Month", format="GH₵ %.2f"),
            "Total": st.column_config.NumberColumn("Total Revenue", format="GH₵ %.2f"),
            "Months Paid (12 = 1 year)": st.column_config.NumberColumn("Months Paid", format="%d"),
        },
    )

    # --- EXPORT CENTRE ---
    st.divider()
    section_heading("Export Centre", "Download the filtered financial records for reporting and further analysis.")
    export_col1, export_col2, export_col3 = st.columns([1, 1, 2])
    with export_col1:
        st.download_button(
            label="Download Excel",
            data=make_excel_download(display_df),
            file_name="Zimatics_SIM_Revenue_Records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with export_col2:
        csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="Zimatics_SIM_Revenue_Records.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with export_col3:
        st.markdown(
            f"""
            <div style="padding:11px 14px; background:#E8F5F3; border-radius:10px; color:#267C72; font-size:12px;">
                <b>Export ready</b><br>
                {len(display_df):,} records · {len(selected_years)} selected years · Ghana cedi reporting
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# TAB 2: SUBSCRIPTION & RENEWAL RADAR
# ==========================================
with tab_renewals:
    section_heading(
        "Predictive Subscription & Renewal Radar",
        "Anticipate contract completion windows and next subscription purchase timelines by customer.",
    )
    renewal_df = calculate_renewal_forecast(filtered_cust)

    renewal_search = st.text_input("Filter renewal radar by customer", placeholder="Enter customer name...")
    if renewal_search.strip():
        renewal_df = renewal_df[renewal_df["Customer Name"].str.contains(renewal_search.strip(), case=False, na=False)]

    st.dataframe(
        renewal_df,
        use_container_width=True,
        hide_index=True,
        height=480,
        column_config={
            "Customer Name": st.column_config.TextColumn("Customer Name"),
            "Schedule Year": st.column_config.NumberColumn("Schedule Year", format="%d"),
            "SIMs": st.column_config.NumberColumn("SIM Cards", format="%d"),
            "Start": st.column_config.TextColumn("Contract Start"),
            "Duration (Mo.)": st.column_config.NumberColumn("Paid Duration (Months)", format="%d"),
            "Expected Renewal": st.column_config.TextColumn("Next Purchase / Renewal Window"),
            "Total Scheduled": st.column_config.NumberColumn("Scheduled Value", format="GH₵ %.2f"),
        },
    )

# ==========================================
# TAB 3: WHAT-IF SCENARIO SIMULATOR
# ==========================================
with tab_simulator:
    section_heading(
        "Interactive What-If Scenario Simulator",
        "Model financial adjustments to monthly SIM unit pricing and fleet expansion in real time.",
    )

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        price_adjustment_pct = st.slider(
            "Unit Price Adjustment (%)",
            min_value=-25,
            max_value=50,
            value=0,
            step=5,
            help="Simulate a percentage change in monthly SIM unit prices.",
        )
    with sim_col2:
        extra_sims_added = st.slider(
            "Additional SIM Fleet Expansion",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            help="Simulate onboarding additional active SIM cards.",
        )
    with sim_col3:
        new_sim_months = st.slider(
            "Contract Duration for New SIMs (Months)",
            min_value=1,
            max_value=24,
            value=12,
            step=1,
            help="Number of billed months for newly added SIM cards.",
        )

    avg_monthly_unit_price = (
        filtered_cust.loc[filtered_cust["Total"] > 0, "Connectivity Unit Price (per month)"].mean()
        if not filtered_cust[filtered_cust["Total"] > 0].empty
        else 15.0
    )
    adjusted_monthly_price = avg_monthly_unit_price * (1 + price_adjustment_pct / 100)

    baseline_adjusted = total_revenue * (1 + price_adjustment_pct / 100)
    expansion_revenue = extra_sims_added * adjusted_monthly_price * new_sim_months
    simulated_revenue = baseline_adjusted + expansion_revenue
    revenue_diff = simulated_revenue - total_revenue
    simulated_sims = total_sims + extra_sims_added

    sim_metric_cols = st.columns(4)
    with sim_metric_cols[0]:
        metric_card("Baseline Revenue", money(total_revenue), "₵", "Current scheduled total")
    with sim_metric_cols[1]:
        metric_card(
            "Simulated Revenue",
            money(simulated_revenue),
            "↗",
            f"{price_adjustment_pct:+d}% price · +{extra_sims_added} SIMs",
        )
    with sim_metric_cols[2]:
        metric_card("Projected Net Variance", money(revenue_diff), "+", "Incremental revenue impact")
    with sim_metric_cols[3]:
        metric_card("Simulated Fleet Size", number(simulated_sims), "▣", f"Avg. unit rate: {money(adjusted_monthly_price)}/mo")

    st.markdown(
        f"""
        <div class="insight-panel" style="margin-top:20px;">
            <div class="insight-title">Scenario Simulation Summary</div>
            <div class="insight-text">
                Applying a <span class="insight-highlight">{price_adjustment_pct:+d}%</span> unit price adjustment
                (shifting average monthly SIM pricing to <span class="insight-highlight">{money(adjusted_monthly_price)}</span>)
                and adding <span class="insight-highlight">{extra_sims_added} new SIM cards</span> billed for
                <span class="insight-highlight">{new_sim_months} months</span> moves total scheduled revenue from
                <span class="insight-highlight">{money(total_revenue)}</span> to
                <span class="insight-highlight">{money(simulated_revenue)}</span>
                (a net change of <span class="insight-highlight">{money(revenue_diff)}</span>).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- FOOTER ---
st.markdown(
    """
    <div style="text-align:center; padding:35px 10px 10px 10px; color:#94A2AE; font-size:11px;">
        <div style="width:45px; height:3px; background:linear-gradient(90deg,#159D91,#6AD6B9); margin:0 auto 13px auto; border-radius:10px;"></div>
        <b style="color:#526878;">ZIMATICS · SIM REVENUE INTELLIGENCE</b><br>
        Connectivity Analytics &amp; Financial Reporting Platform<br><br>
        © 2026 · All rights reserved.
    </div>
    """,
    unsafe_allow_html=True,
)
