import pandas as pd
import numpy as np

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

def calculate_renewal_forecast(filtered_cust):
    """Calculates contract duration and expected renewal/next purchase windows."""
    forecasts = []
    for _, row in filtered_cust.iterrows():
        start_month_str = str(row.get("Start Month", "January")).strip()
        start_m = MONTH_MAP.get(start_month_str, 1)
        start_y = int(row.get("Schedule Year", 2026))
        
        # Safely parse months paid
        try:
            months_paid = int(row.get("Months Paid (12 = 1 year)", 12))
            if months_paid <= 0:
                months_paid = 12
        except (ValueError, TypeError):
            months_paid = 12
            
        # Compute approximate end date
        total_start_months = (start_y * 12) + (start_m - 1)
        total_end_months = total_start_months + months_paid
        end_y = total_end_months // 12
        end_m = (total_end_months % 12) + 1
        
        month_names = ["", "January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        
        forecasts.append({
            "Customer Name": row.get("Customer Name", "Unknown"),
            "Schedule Year": start_y,
            "SIMs": row.get("No. of SIM Cards", 0),
            "Start": f"{start_month_str} {start_y}",
            "Duration (Mo.)": months_paid,
            "Expected Renewal": f"{month_names[end_m]} {end_y}",
            "Total Scheduled": row.get("Total", 0)
        })
    return pd.DataFrame(forecasts)

def compute_business_diagnostics(filtered_cust, total_revenue):
    """Computes concentration risk and growth indicators."""
    if filtered_cust.empty or total_revenue == 0:
        return {"top_client_share": 0, "top_client_name": "None", "concentration_risk": "Low"}
        
    cust_rev = filtered_cust.groupby("Customer Name")["Total"].sum().reset_index()
    cust_rev = cust_rev.sort_values("Total", ascending=False)
    
    top_client = cust_rev.iloc[0] if not cust_rev.empty else {"Customer Name": "None", "Total": 0}
    top_share = (top_client["Total"] / total_revenue) * 100
    
    top_3_share = (cust_rev.head(3)["Total"].sum() / total_revenue) * 100
    
    risk_level = "High Concentration" if top_3_share > 50 else ("Moderate" if top_3_share > 30 else "Well Diversified")
    
    return {
        "top_client_name": top_client["Customer Name"],
        "top_client_share": top_share,
        "top_3_share": top_3_share,
        "risk_level": risk_level
    }
