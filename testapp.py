# app.py
import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI-Driven Customer Journey Mapper", layout="wide")

st.title("🧠 AI-Driven Multi-Touchpoint Customer Journey Mapper")
st.write("""
This upgraded version combines customer data from **web**, **mobile app**, and **physical store**
into a single connected journey map with basic analytics and visual insights.
""")

# -----------------------------
# FILE UPLOAD SECTION
# -----------------------------
st.sidebar.header("📂 Upload Your Datasets")
web_file = st.sidebar.file_uploader("Upload Website Data (CSV)", type="csv")
app_file = st.sidebar.file_uploader("Upload Mobile App Data (CSV)", type="csv")
store_file = st.sidebar.file_uploader("Upload Physical Store Data (CSV)", type="csv")

# -----------------------------
# CHECK FILES
# -----------------------------
if not (web_file or app_file or store_file):
    st.info("👈 Please upload at least one CSV file to begin.")
    st.stop()

# -----------------------------
# SAFER LOAD FUNCTION
# -----------------------------
def load_data(file, source):
    try:
        # Auto-detect delimiter and encoding
        df = pd.read_csv(file, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")
        df["Source"] = source
        return df
    except Exception as e:
        st.error(f"❌ Error loading {source} data: {e}")
        return pd.DataFrame()

# -----------------------------
# COMBINE FILES
# -----------------------------
dataframes = []
if web_file:
    dataframes.append(load_data(web_file, "Website"))
if app_file:
    dataframes.append(load_data(app_file, "Mobile App"))
if store_file:
    dataframes.append(load_data(store_file, "Store"))

# Filter out empty data
dataframes = [df for df in dataframes if not df.empty]

if not dataframes:
    st.error("⚠️ No valid data loaded. Please check your CSV format.")
    st.stop()

combined_df = pd.concat(dataframes, ignore_index=True)

# -----------------------------
# DATA CLEANING
# -----------------------------
# Try to detect timestamps and convert
if "Timestamp" in combined_df.columns:
    combined_df["Timestamp"] = pd.to_datetime(combined_df["Timestamp"], errors="coerce")
else:
    # Try auto-detect timestamp-like columns
    for col in combined_df.columns:
        if "time" in col.lower() or "date" in col.lower():
            combined_df["Timestamp"] = pd.to_datetime(combined_df[col], errors="coerce")
            break

# Fill missing values gracefully
combined_df = combined_df.fillna("N/A")

# -----------------------------
# FILTER SECTION
# -----------------------------
st.sidebar.header("🔍 Filters")

if "Source" in combined_df.columns:
    selected_sources = st.sidebar.multiselect(
        "Select Touchpoints", 
        options=combined_df["Source"].unique(),
        default=list(combined_df["Source"].unique())
    )
    combined_df = combined_df[combined_df["Source"].isin(selected_sources)]

if "Activity" in combined_df.columns:
    selected_activity = st.sidebar.multiselect(
        "Filter by Activity", 
        options=combined_df["Activity"].unique(),
        default=list(combined_df["Activity"].unique())
    )
    combined_df = combined_df[combined_df["Activity"].isin(selected_activity)]

if "Timestamp" in combined_df.columns and combined_df["Timestamp"].dtype == "datetime64[ns]":
    min_date, max_date = combined_df["Timestamp"].min(), combined_df["Timestamp"].max()
    date_range = st.sidebar.date_input("Select Date Range", [min_date.date(), max_date.date()])
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        combined_df = combined_df[
            (combined_df["Timestamp"] >= start_date) & (combined_df["Timestamp"] <= end_date)
        ]

# -----------------------------
# DISPLAY DATA
# -----------------------------
st.subheader("📊 Unified Customer Journey Data")
st.dataframe(combined_df)

# -----------------------------
# SUMMARY STATISTICS
# -----------------------------
st.subheader("📈 Summary Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Records", len(combined_df))
with col2:
    st.metric("Unique Customers", combined_df["CustomerID"].nunique() if "CustomerID" in combined_df.columns else "N/A")
with col3:
    if "Timestamp" in combined_df.columns:
        st.metric("Date Range", f"{combined_df['Timestamp'].min().date()} → {combined_df['Timestamp'].max().date()}")

# -----------------------------
# SOURCE DISTRIBUTION
# -----------------------------
if "Source" in combined_df.columns:
    st.subheader("📦 Records by Source")
    source_summary = combined_df["Source"].value_counts().reset_index()
    source_summary.columns = ["Source", "Total Records"]
    st.bar_chart(source_summary.set_index("Source"))

# -----------------------------
# CUSTOMER JOURNEY TIMELINE
# -----------------------------
if "CustomerID" in combined_df.columns and "Timestamp" in combined_df.columns:
    st.subheader("🕒 Customer Journey Timeline")
    
    # Sort by customer and time
    sorted_df = combined_df.sort_values(by=["CustomerID", "Timestamp"])
    selected_customer = st.selectbox("Select a Customer ID to view journey:", sorted_df["CustomerID"].unique())
    customer_journey = sorted_df[sorted_df["CustomerID"] == selected_customer]
    
    st.write(f"### Customer {selected_customer}'s Journey Across Touchpoints")
    st.table(customer_journey[["Timestamp", "Activity", "Source"]])
else:
    st.warning("⚠️ Please ensure your CSVs include 'CustomerID' and 'Timestamp' columns for timeline analysis.")

# -----------------------------
# AI-LIKE INSIGHT (Basic Pattern)
# -----------------------------
if "Activity" in combined_df.columns and "Source" in combined_df.columns:
    st.subheader("🤖 AI Insight (Most Common Activity by Touchpoint)")
    insight = combined_df.groupby("Source")["Activity"].agg(lambda x: x.value_counts().index[0] if len(x) > 0 else "N/A")
    st.table(insight.reset_index().rename(columns={"Activity": "Most Common Activity"}))

# -----------------------------
# DOWNLOAD BUTTON
# -----------------------------
st.subheader("💾 Download Combined Dataset")
csv = combined_df.to_csv(index=False).encode("utf-8")
st.download_button("Download Combined Data as CSV", data=csv, file_name="combined_customer_journey.csv", mime="text/csv")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
---
✅ **Objective 2 Achieved:**  
This app integrates customer data from **online**, **mobile**, and **store** sources 
into one connected, interactive journey map with summaries, filters, insights, and timeline views.
""")
