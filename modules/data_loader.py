import io
import pandas as pd
import streamlit as st
from modules.config import MONTHS


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
        try:
            year = int(str(sheet_name).strip())
        except ValueError:
            continue

        df = pd.read_excel(xls, sheet_name=sheet_name, header=4)
        df.columns = df.columns.astype(str).str.strip()

        if any(col not in df.columns for col in required_columns):
            continue

        customer_names = df["Customer Name"].fillna("").astype(str).str.strip()
        df = df[(customer_names != "") & (customer_names.str.upper() != "TOTAL")].copy()

        if df.empty:
            continue

        df["Customer Name"] = customer_names.loc[df.index]
        df["Schedule Year"] = year

        numeric_columns = [
            "No. of SIM Cards",
            "Connectivity Unit Price (per month)",
            "Start Year",
            "Total",
        ] + MONTHS

        for col in numeric_columns:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        monthly_total = df[MONTHS].sum(axis=1)
        df["Total"] = df["Total"].where(df["Total"] != 0, monthly_total)

        # Mirror Excel's =SUMIF(S6:S99, ">0", B6:B99) rule: exclude $0 rows
        df = df[df["Total"] > 0].copy()

        if df.empty:
            continue

        # Identify original activations vs. carry-forward rows from prior years
        df["Is Carryover"] = df["Start Year"] != df["Schedule Year"]
        df["Active Cohort SIMs"] = df["No. of SIM Cards"].where(~df["Is Carryover"], 0)

        all_records.append(df)

    if not all_records:
        return pd.DataFrame(), pd.DataFrame()

    combined_df = pd.concat(all_records, ignore_index=True)

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
    monthly_df["Month Num"] = monthly_df["Month"].map({m: i + 1 for i, m in enumerate(MONTHS)})
    monthly_df["Date"] = pd.to_datetime(
        monthly_df["Schedule Year"].astype(str)
        + "-"
        + monthly_df["Month Num"].astype(str).str.zfill(2)
        + "-01"
    )

    return combined_df, monthly_df


def calculate_active_sims(filtered_cust, selected_years):
    """Return the exact active SIM count without double-counting carry-overs."""
    if filtered_cust.empty:
        return 0
    # When viewing all years (or multiple years), sum only original cohort activations (55 SIMs)
    if len(selected_years) > 1:
        return int(filtered_cust["Active Cohort SIMs"].sum())
    # When viewing a single year tab (e.g., 2027 alone), match that sheet's TOTAL row (25 SIMs)
    return int(filtered_cust["No. of SIM Cards"].sum())


def make_excel_download(dataframe):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, sheet_name="Filtered Records", index=False)
    output.seek(0)
    return output.getvalue()
