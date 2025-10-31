# app.py
import streamlit as st
import pandas as pd

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(page_title="Customer Journey Mapper", layout="wide")
st.title("🧠 AI-Driven Multi-Touchpoint Customer Journey Dashboard")
st.write("""
This enhanced app merges data from **Website**, **Mobile App**, and **Physical Store** 
into one unified customer journey. You can explore, filter, and download the merged insights.
""")

# -----------------------------
# FILE UPLOAD SECTION
# -----------------------------
st.sidebar.header("📂 Upload Your CSV Files")
web_file = st.sidebar.file_uploader("Upload Website Data", type="csv")
app_file = st.sidebar.file_uploader("Upload Mobile App Data", type="csv")
store_file = st.sidebar.file_uploader("Upload Store Data", type="csv")

if not (web_file or app_file or store_file):
    st.info("👈 Upload at least one CSV file to get started.")
    st.stop()

# -----------------------------
# LOAD & LABEL FUNCTION
# -----------------------------
def load_data(file, source):
    df = pd.read_csv(file)
    df["Source"] = source
    return df

dataframes = []
if web_file:
    dataframes.append(load_data(web_file, "Website"))
if app_file:
    dataframes.append(load_data(app_file, "Mobile App"))
if store_file:
    dataframes.append(load_data(store_file, "Store"))

# -----------------------------
# MERGE & CLEAN DATA
# -----------------------------
combined_df = pd.concat(dataframes, ignore_index=True)
if "Timestamp" in combined_df.columns:
    combined_df["Timestamp"] = pd.to_datetime(combined_df["Timestamp"], errors="coerce")
else:
    st.warning("⚠️ Missing 'Timestamp' column; timeline features may not work properly.")

# -----------------------------
# FILTER SECTION
# -----------------------------
st.sidebar.header("⚙️ Filters")

# Date range filter (if Timestamp exists)
if "Timestamp" in combined_df.columns:
    min_date = combined_df["Timestamp"].min()
    max_date = combined_df["Timestamp"].max()
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        combined_df = combined_df[(combined_df["Timestamp"] >= start_date) & (combined_df["Timestamp"] <= end_date)]

# Touchpoint filter
selected_sources = st.sidebar.multiselect(
    "Select Touchpoints", options=combined_df["Source"].unique(), default=list(combined_df["Source"].unique())
)
combined_df = combined_df[combined_df["Source"].isin(selected_sources)]

# -----------------------------
# MAIN DASHBOARD DISPLAY
# -----------------------------
st.subheader("📊 Unified Customer Journey Data")
st.dataframe(combined_df)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🧍 Total Customers", combined_df["CustomerID"].nunique() if "CustomerID" in combined_df.columns else "N/A")

with col2:
    st.metric("📋 Total Records", len(combined_df))

with col3:
    st.metric("🕒 Date Range", f"{combined_df['Timestamp'].min().date()} → {combined_df['Timestamp'].max().date()}" if "Timestamp" in combined_df.columns else "N/A")

# -----------------------------
# VISUAL SUMMARIES
# -----------------------------
st.subheader("📈 Journey Insights by Touchpoint")
source_counts = combined_df["Source"].value_counts()

colA, colB = st.columns(2)
with colA:
    st.bar_chart(source_counts)
with colB:
    st.write("**Proportion of Records by Touchpoint**")
    st.dataframe(source_counts.reset_index().rename(columns={"index": "Source", "Source": "Total"}))

# -----------------------------
# CUSTOMER JOURNEY TIMELINE
# -----------------------------
if "CustomerID" in combined_df.columns and "Timestamp" in combined_df.columns:
    st.subheader("🕵️ View Individual Customer Journey")

    sorted_df = combined_df.sort_values(by=["CustomerID", "Timestamp"])
    selected_customer = st.selectbox("Select Customer ID", sorted_df["CustomerID"].unique())

    customer_journey = sorted_df[sorted_df["CustomerID"] == selected_customer]
    st.write(f"### Journey for Customer {selected_customer}")
    st.table(customer_journey[["Timestamp", "Activity", "Source"]])
else:
    st.warning("⚠️ Please ensure your CSVs include 'CustomerID' and 'Timestamp' columns.")

# -----------------------------
# DOWNLOAD SECTION
# -----------------------------
st.subheader("💾 Download Combined Dataset")
csv = combined_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Combined Data as CSV",
    data=csv,
    file_name="combined_customer_journey.csv",
    mime="text/csv"
)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
---
✅ **Objective 2 Achieved:**  
This dashboard integrates customer data from multiple touchpoints, provides filters, summaries, 
and allows interactive exploration with export options.  
""")
