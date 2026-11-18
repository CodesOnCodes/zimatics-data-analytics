import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.config import COLORS, MONTHS, PALETTE
from modules.components import number, safe_html, style_figure


def build_revenue_trend_chart(filtered_monthly):
    ts_data = (
        filtered_monthly.groupby(["Date", "Schedule Year"], as_index=False)["Revenue"]
        .sum()
        .sort_values("Date")
    )
    fig = go.Figure()
    for i, year in enumerate(sorted(ts_data["Schedule Year"].unique())):
        year_data = ts_data[ts_data["Schedule Year"] == year]
        fig.add_trace(
            go.Scatter(
                x=year_data["Date"],
                y=year_data["Revenue"],
                name=str(year),
                mode="lines+markers",
                line=dict(color=PALETTE[i % len(PALETTE)], width=3, shape="spline"),
                marker=dict(size=6),
                fill="tozeroy",
                fillcolor="rgba(21,157,145,0.05)",
                hovertemplate="<b>%{x|%b %Y}</b><br>Revenue: GH₵ %{y:,.2f}<extra></extra>",
            )
        )
    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", y=1.15, x=0),
        yaxis_title="Revenue (GH₵)",
        xaxis_title="",
    )
    return style_figure(fig, 390)


def build_top_customers_chart(filtered_cust, top_n, show_data_labels):
    summary = (
        filtered_cust.groupby("Customer Name", as_index=False)
        .agg(Revenue=("Total", "sum"), SIMs=("No. of SIM Cards", "sum"))
        .sort_values("Revenue", ascending=False)
        .head(top_n)
        .sort_values("Revenue", ascending=True)
    )
    summary["Bold Name"] = summary["Customer Name"].apply(lambda n: f"<b>{safe_html(n)}</b>")

    fig = px.bar(
        summary,
        x="Revenue",
        y="Bold Name",
        orientation="h",
        text="Revenue" if show_data_labels else None,
        color="Revenue",
        color_continuous_scale=["#52B7AE", "#159D91", "#172B3A"],
        labels={"Revenue": "Revenue (GH₵)", "Bold Name": ""},
    )
    if show_data_labels:
        fig.update_traces(
            texttemplate="<b>GH₵ %{text:,.0f}</b>",
            textposition="outside",
            cliponaxis=False,
            textfont=dict(color="#172B3A", size=12),
        )
    max_rev = summary["Revenue"].max() if not summary.empty else 0
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis=dict(range=[0, max_rev * 1.25 if max_rev > 0 else 100]),
        yaxis=dict(automargin=True),
    )
    return style_figure(fig, max(380, len(summary) * 38))


def build_fleet_donut_chart(filtered_cust, total_sims):
    sim_col = (
        "Active Cohort SIMs"
        if "Active Cohort SIMs" in filtered_cust.columns and filtered_cust["Schedule Year"].nunique() > 1
        else "Billed Sheet SIMs"
    )
    fleet_data = filtered_cust.groupby("Customer Name", as_index=False)[sim_col].sum()
    fleet_data = fleet_data.rename(columns={sim_col: "No. of SIM Cards"})
    fleet_data = fleet_data[fleet_data["No. of SIM Cards"] > 0].sort_values("No. of SIM Cards", ascending=False)

    if fleet_data.empty:
        return None

    if len(fleet_data) > 8:
        top_fleet = fleet_data.head(7)
        others = pd.DataFrame({
            "Customer Name": ["Others"],
            "No. of SIM Cards": [fleet_data.iloc[7:]["No. of SIM Cards"].sum()],
        })
        fleet_display = pd.concat([top_fleet, others], ignore_index=True)
    else:
        fleet_display = fleet_data

    fig = px.pie(
        fleet_display,
        names="Customer Name",
        values="No. of SIM Cards",
        hole=0.63,
        color_discrete_sequence=["#159D91", "#4786C6", "#E9B949", "#9368C8", "#E17C70", "#4CA6A8", "#6C8799", "#C1CDD5"],
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        texttemplate="<b>%{percent}</b>",
        textfont=dict(color="#FFFFFF", size=12),
        insidetextorientation="horizontal",
        hole=0.63,
        hovertemplate="<b>%{label}</b><br>SIM Cards: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )
    fig.add_annotation(
        text=f"<b>{number(total_sims)}</b><br><span style='font-size:11px'>ACTIVE SIMS</span>",
        showarrow=False,
        font=dict(size=18, color=COLORS["navy"]),
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center"),
    )
    return style_figure(fig, 390)


def build_scatter_chart(filtered_cust):
    scatter_data = filtered_cust[filtered_cust["Total"] > 0].copy()
    if scatter_data.empty:
        return None

    fig = px.scatter(
        scatter_data,
        x="No. of SIM Cards",
        y="Connectivity Unit Price (per month)",
        size="Total",
        color="Schedule Year",
        hover_name="Customer Name",
        size_max=35,
        color_discrete_sequence=PALETTE,
        labels={
            "No. of SIM Cards": "SIM Cards",
            "Connectivity Unit Price (per month)": "Unit Price (GH₵)",
            "Schedule Year": "Year",
        },
    )
    fig.update_traces(
        marker=dict(opacity=0.82, line=dict(width=1.5, color="#172B3A")),
        hovertemplate="<b>%{hovertext}</b><br>SIM Cards: %{x:,.0f}<br>Unit Price: GH₵ %{y:,.2f}<extra></extra>",
    )
    fig.update_layout(legend=dict(orientation="h", y=1.12, x=0))
    return style_figure(fig, 390)


def build_annual_charts(yearly_summary, show_data_labels):
    fig_annual = go.Figure()
    fig_annual.add_trace(
        go.Bar(
            x=yearly_summary["Schedule Year"].astype(str),
            y=yearly_summary["Revenue"],
            name="Revenue",
            marker=dict(color="#159D91"),
            text=[f"<b>GH₵ {v:,.0f}</b>" for v in yearly_summary["Revenue"]] if show_data_labels else None,
            textposition="outside",
            cliponaxis=False,
            textfont=dict(color="#172B3A", size=12),
            hovertemplate="<b>%{x}</b><br>Revenue: GH₵ %{y:,.2f}<extra></extra>",
        )
    )
    max_rev = yearly_summary["Revenue"].max() if not yearly_summary.empty else 0
    fig_annual.update_layout(
        title="Revenue by Schedule Year",
        xaxis_title="Schedule Year",
        yaxis_title="Revenue (GH₵)",
        yaxis=dict(range=[0, max_rev * 1.2 if max_rev > 0 else 100]),
        showlegend=False,
    )

    fig_sims = px.bar(
        yearly_summary,
        x="Schedule Year",
        y="SIMs",
        color="SIMs",
        color_continuous_scale=["#52B7AE", "#159D91", "#172B3A"],
        text="SIMs" if show_data_labels else None,
        labels={"Schedule Year": "Year", "SIMs": "Billed SIM Cards"},
    )
    if show_data_labels:
        fig_sims.update_traces(
            texttemplate="<b>%{text:,.0f}</b>",
            textposition="outside",
            cliponaxis=False,
            textfont=dict(color="#172B3A", size=12),
        )
    max_sims = yearly_summary["SIMs"].max() if not yearly_summary.empty else 0
    fig_sims.update_layout(
        title="Billed SIM Allocation by Year",
        coloraxis_showscale=False,
        yaxis=dict(range=[0, max_sims * 1.2 if max_sims > 0 else 10]),
        showlegend=False,
    )
    return style_figure(fig_annual, 360), style_figure(fig_sims, 360)


def build_monthly_comparison_chart(filtered_monthly):
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
    fig = go.Figure()
    for i, year in enumerate(monthly_pivot.columns):
        fig.add_trace(
            go.Bar(
                x=monthly_pivot.index,
                y=monthly_pivot[year],
                name=str(year),
                marker_color=PALETTE[i % len(PALETTE)],
                hovertemplate=f"<b>%{{x}}</b><br>Year: {year}<br>Revenue: GH₵ %{{y:,.2f}}<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="group",
        xaxis_title="Month",
        yaxis_title="Revenue (GH₵)",
        legend=dict(orientation="h", y=1.12, x=0),
    )
    return style_figure(fig, 400)
