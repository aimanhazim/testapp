# app.py
import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------------------------------
# APP CONFIG
# -------------------------------------------------
st.set_page_config(page_title="AI-Driven Customer Journey Dashboard", layout="wide")
st.title("🧠 Smart AI-Driven Customer Journey Dashboard")
st.write("""
Upload data from **Website**, **Mobile App**, and **Physical Store**.  
The app will automatically clean, merge, and analyze customer journeys across all touchpoints.
""")

# -------------------------------------------------
# FUNCTIONS
# -------------------------------------------------
def read_data(file, source):
    try:
        if file.name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file, encoding="utf-8", sep=None, engine="python")
        df["Source"] = source
        return df
    except Exception as e:
        st.error(f"❌ Error reading {source} data: {e}")
        return pd.DataFrame()

def detect_columns(df):
    cols = [c.lower() for c in df.columns]
    mapping = {}
    for col in df.columns:
        l = col.lower()
        if any(x in l for x in ["cust", "id", "user"]):
            mapping["CustomerID"] = col
        elif any(x in l for x in ["time", "date"]):
            mapping["Timestamp"] = col
        elif any(x in l for x in ["activity", "action", "event"]):
            mapping["Activity"] = col
    return mapping

def clean_and_standardize(df, mapping):
    df = df.rename(columns=mapping)
    for col in ["CustomerID", "Timestamp", "Activity"]:
        if col not in df.columns:
            df[col] = None
    df["CustomerID"] = df["CustomerID"].astype(str).str.strip()
    df["Activity"] = df["Activity"].astype(str).str.strip()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    return df.dropna(subset=["CustomerID"])

# -------------------------------------------------
# UPLOAD FILES
# -------------------------------------------------
st.sidebar.header("📂 Upload Files")
web = st.sidebar.file_uploader("Upload Website Data", type=["csv", "xls", "xlsx"])
app = st.sidebar.file_uploader("Upload Mobile App Data", type=["csv", "xls", "xlsx"])
store = st.sidebar.file_uploader("Upload Store Data", type=["csv", "xls", "xlsx"])

if not (web or app or store):
    st.info("👈 Upload at least one CSV or Excel file to begin.")
    st.stop()

# -------------------------------------------------
# LOAD & CLEAN DATA
# -------------------------------------------------
dfs = []
for f, name in [(web, "Website"), (app, "Mobile App"), (store, "Store")]:
    if f:
        raw_df = read_data(f, name)
        if not raw_df.empty:
            mapping = detect_columns(raw_df)
            cleaned = clean_and_standardize(raw_df, mapping)
            dfs.append(cleaned)

if not dfs:
    st.error("No valid files could be read.")
    st.stop()

combined = pd.concat(dfs, ignore_index=True)
combined = combined.drop_duplicates()

# -------------------------------------------------
# FILTERS
# -------------------------------------------------
st.sidebar.header("🔎 Filters")
if "Timestamp" in combined.columns and combined["Timestamp"].notna().any():
    min_date, max_date = combined["Timestamp"].min(), combined["Timestamp"].max()
    date_range = st.sidebar.date_input("Date range", [min_date.date(), max_date.date()])
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        combined = combined[(combined["Timestamp"] >= start) & (combined["Timestamp"] <= end)]

sources = sorted(combined["Source"].unique())
selected_sources = st.sidebar.multiselect("Select Touchpoints", sources, default=sources)
combined = combined[combined["Source"].isin(selected_sources)]

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
st.subheader("📊 Combined Customer Journey Data")
st.dataframe(combined)

col1, col2, col3 = st.columns(3)
col1.metric("🧍 Unique Customers", combined["CustomerID"].nunique())
col2.metric("📋 Total Records", len(combined))
if "Timestamp" in combined.columns and combined["Timestamp"].notna().any():
    col3.metric("🕒 Time Range", f"{combined['Timestamp'].min().date()} → {combined['Timestamp'].max().date()}")

st.markdown("---")
st.subheader("📈 Touchpoint Summary")
source_counts = combined["Source"].value_counts()
st.bar_chart(source_counts)

# -------------------------------------------------
# CUSTOMER JOURNEY VIEW
# -------------------------------------------------
st.markdown("---")
st.subheader("🕵️ View Individual Customer Journey")

if "CustomerID" in combined.columns:
    customers = sorted(combined["CustomerID"].unique())
    selected_customer = st.selectbox("Select Customer ID", customers)
    journey = combined[combined["CustomerID"] == selected_customer].sort_values("Timestamp")
    st.write(f"### Journey for Customer {selected_customer}")
    st.table(journey[["Timestamp", "Activity", "Source"]])
else:
    st.warning("No CustomerID column detected.")

# -------------------------------------------------
# SIMPLE AI INSIGHT (Simulated)
# -------------------------------------------------
st.markdown("---")
st.subheader("🤖 AI Insight Simulation")
if "Activity" in combined.columns:
    most_common = combined.groupby("Source")["Activity"].agg(lambda x: x.value_counts().index[0] if not x.empty else "N/A")
    st.write("**Most Common Activity per Touchpoint:**")
    st.table(most_common.reset_index().rename(columns={"Activity": "Most Common Activity"}))

    st.info("🧠 Insight: The most frequent activities help identify where customers spend most time or attention.")
else:
    st.warning("No 'Activity' column found to analyze patterns.")

# -------------------------------------------------
# DOWNLOAD
# -------------------------------------------------
st.markdown("---")
st.subheader("💾 Download Cleaned Combined Data")
csv = combined.to_csv(index=False).encode("utf-8")
st.download_button("Download Combined CSV", csv, "cleaned_customer_journey.csv", "text/csv")

st.markdown("""
---
✅ **Objective 2 Achieved (Upgraded Version):**
- Automatic data cleaning and merging  
- Interactive filters and analytics  
- Per-customer journey exploration  
- Basic AI insights for marketing decisions  
""")
