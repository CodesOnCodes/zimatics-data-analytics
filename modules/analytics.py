import pandas as pd
from modules.config import MONTHS

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}


def calculate_renewal_forecast(filtered_cust):
    """Calculates contract duration, exact expiry dates, and expected renewal windows."""
    forecasts = []
    month_names = [""] + MONTHS

    for _, row in filtered_cust.iterrows():
        start_month_str = str(row.get("Start Month", "January")).strip()
        start_m = MONTH_MAP.get(start_month_str, 1)
        start_y = int(row.get("Schedule Year", 2026))

        try:
            months_paid = int(row.get("Months Paid (12 = 1 year)", 12))
            if months_paid <= 0:
                months_paid = 12
        except (ValueError, TypeError):
            months_paid = 12

        total_start_months = (start_y * 12) + (start_m - 1)
        total_end_months = total_start_months + months_paid
        end_y = total_end_months // 12
        end_m = (total_end_months % 12) + 1

        start_dt = pd.Timestamp(year=start_y, month=start_m, day=1)
        end_dt = pd.Timestamp(year=end_y, month=end_m, day=1)

        forecasts.append({
            "Customer Name": row.get("Customer Name", "Unknown"),
            "Schedule Year": start_y,
            "SIMs": int(row.get("No. of SIM Cards", 0)),
            "Start": f"{start_month_str} {start_y}",
            "Start Date": start_dt,
            "End Date": end_dt,
            "Duration (Mo.)": months_paid,
            "Expected Renewal": f"{month_names[end_m]} {end_y}",
            "Total Scheduled": float(row.get("Total", 0)),
        })
    return pd.DataFrame(forecasts)


def compute_business_diagnostics(filtered_cust, total_revenue):
    """Computes concentration risk and growth indicators."""
    if filtered_cust.empty or total_revenue == 0:
        return {
            "top_client_share": 0.0,
            "top_client_name": "None",
            "top_3_share": 0.0,
            "risk_level": "Low",
        }

    cust_rev = (
        filtered_cust.groupby("Customer Name")["Total"]
        .sum()
        .reset_index()
        .sort_values("Total", ascending=False)
    )

    top_client = cust_rev.iloc[0]
    top_share = (top_client["Total"] / total_revenue) * 100
    top_3_share = (cust_rev.head(3)["Total"].sum() / total_revenue) * 100
    risk_level = (
        "High Concentration"
        if top_3_share > 50
        else ("Moderate" if top_3_share > 30 else "Well Diversified")
    )

    return {
        "top_client_name": top_client["Customer Name"],
        "top_client_share": top_share,
        "top_3_share": top_3_share,
        "risk_level": risk_level,
    }


def build_cashflow_matrix(filtered_monthly):
    """Builds a Customer x Month billing matrix with an annual row total."""
    if filtered_monthly.empty:
        return pd.DataFrame()

    matrix = (
        filtered_monthly.pivot_table(
            index="Customer Name",
            columns="Month",
            values="Revenue",
            aggfunc="sum",
            fill_value=0,
        )
        .reindex(columns=MONTHS, fill_value=0)
    )
    matrix["Annual Total"] = matrix.sum(axis=1)
    matrix = matrix.sort_values("Annual Total", ascending=False).reset_index()
    return matrix


def generate_executive_briefing(
    selected_years,
    total_revenue,
    total_sims,
    unique_customers,
    average_yield,
    diagnostics,
    pending_count,
    renewal_df,
):
    """Generates a ready-to-copy management briefing summary."""
    period_label = (
        f"{min(selected_years)} - {max(selected_years)}"
        if len(selected_years) > 1
        else str(selected_years[0])
    )
    next_renewal_line = "No active renewal windows scheduled."
    active_renewals = renewal_df[renewal_df["Total Scheduled"] > 0].sort_values("End Date")
    if not active_renewals.empty:
        first_due = active_renewals.iloc[0]
        next_renewal_line = (
            f"Earliest upcoming contract renewal is {first_due['Customer Name']} "
            f"({first_due['SIMs']} SIMs) in {first_due['Expected Renewal']}."
        )

    return (
        f"ZIMATICS CONNECTIVITY REVENUE BRIEFING ({period_label})\n"
        f"------------------------------------------------------------\n"
        f"- Total Scheduled Revenue: GH₵ {total_revenue:,.2f}\n"
        f"- Active Billed SIM Fleet: {total_sims:,} units across {unique_customers} registered accounts\n"
        f"- Average Yield per Billed SIM: GH₵ {average_yield:,.2f}\n"
        f"- Top Revenue Contributor: {diagnostics['top_client_name']} "
        f"({diagnostics['top_client_share']:.1f}% of revenue; Top 3 accounts = {diagnostics['top_3_share']:.1f}%)\n"
        f"- Renewal Outlook: {next_renewal_line}\n"
        f"- Billing Audit Note: {pending_count} schedule entries currently carry GH₵ 0.00 pending pricing/duration input."
    )
