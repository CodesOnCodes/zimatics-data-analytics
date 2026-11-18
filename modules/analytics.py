# modules/analytics.py (Example snippet for predictive renewals)
import pandas as pd
from datetime import datetime

def calculate_renewal_forecast(filtered_cust):
    """Calculates estimated contract end dates and next purchase windows."""
    forecasts = []
    month_map = {"January": 1, "February": 2, "March": 3, "April": 4, 
                 "May": 5, "June": 6, "July": 7, "August": 8, 
                 "September": 9, "October": 10, "November": 11, "December": 12}
    
    for _, row in filtered_cust.iterrows():
        start_month_str = str(row.get("Start Month", "January")).strip()
        start_m = month_map.get(start_month_str, 1)
        start_y = int(row.get("Schedule Year", 2026))
        months_paid = int(row.get("Months Paid (12 = 1 year)", 12))
        
        # Approximate contract end calculation
        end_total_months = (start_m - 1) + months_paid
        end_y = start_y + (end_total_months // 12)
        end_m = (end_total_months % 12) + 1
        
        forecasts.append({
            "Customer Name": row["Customer Name"],
            "Schedule Year": start_y,
            "SIMs": row["No. of SIM Cards"],
            "Contract Duration (Months)": months_paid,
            "Renewal Window": f"{end_m:02d}/{end_y}"
        })
    return pd.DataFrame(forecasts)