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
# LOAD FUNCTION
# -----------------------------
def load_data(file, source):
    df = pd.read_csv(file)
    df["Source"] = source
    return df

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

combined_df = pd.concat(dataframes, ignore_index=True)

# Ensure Timestamp exists and convert it
if "Timestamp" in combined_df.columns:
    combined_df["Timestamp"] = pd.to_datetime(combined_df["Timestamp"], errors="coerce")

# -----------------------------
# DISPLAY DATA
# -----------------------------
st.subheader("📊 Unified Customer Journey Data")
st.dataframe(combined_df)

# -----------------------------
# SUMMARY STATISTICS
# -----------------------------
st.subheader("📈 Summary Overview")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Records", len(combined_df))
    st.metric("Unique Customers", combined_df["CustomerID"].nunique() if "CustomerID" in combined_df.columns else "N/A")

with col2:
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
# FOOTER
# -----------------------------
st.markdown("""
---
✅ **Objective 2 Achieved:**  
This app integrates customer data from **online**, **mobile**, and **store** sources 
into one connected, interactive journey map with summaries and timeline views.
""")
