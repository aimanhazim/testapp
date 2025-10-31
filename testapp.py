# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
# LOAD FUNCTION (UNCHANGED)
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
# FILTERS
# -----------------------------
st.sidebar.header("🔍 Data Filters")

if "Source" in combined_df.columns:
    selected_sources = st.sidebar.multiselect(
        "Filter by Source",
        options=combined_df["Source"].unique(),
        default=list(combined_df["Source"].unique())
    )
    combined_df = combined_df[combined_df["Source"].isin(selected_sources)]

if "Activity" in combined_df.columns:
    selected_activities = st.sidebar.multiselect(
        "Filter by Activity",
        options=combined_df["Activity"].unique(),
        default=list(combined_df["Activity"].unique())
    )
    combined_df = combined_df[combined_df["Activity"].isin(selected_activities)]

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
    st.metric("Total Touchpoints", combined_df["Source"].nunique())

# -----------------------------
# BAR CHART: RECORDS BY SOURCE
# -----------------------------
st.subheader("📦 Records by Source")
if "Source" in combined_df.columns:
    source_summary = combined_df["Source"].value_counts().reset_index()
    source_summary.columns = ["Source", "Total Records"]
    st.bar_chart(source_summary.set_index("Source"))

# -----------------------------
# PIE CHART (Matplotlib)
# -----------------------------
if "Activity" in combined_df.columns:
    st.subheader("🎯 Activity Distribution")
    activity_summary = combined_df["Activity"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(activity_summary, labels=activity_summary.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

# -----------------------------
# LINE CHART: INTERACTIONS OVER TIME
# -----------------------------
if "Timestamp" in combined_df.columns:
    st.subheader("📅 Customer Interactions Over Time")
    combined_df["Date"] = combined_df["Timestamp"].dt.date
    trend = combined_df.groupby(["Date", "Source"]).size().unstack(fill_value=0)
    st.line_chart(trend)

# -----------------------------
# CUSTOMER JOURNEY TIMELINE (ORIGINAL)
# -----------------------------
if "CustomerID" in combined_df.columns and "Timestamp" in combined_df.columns:
    st.subheader("🕒 Customer Journey Timeline")
    sorted_df = combined_df.sort_values(by=["CustomerID", "Timestamp"])
    selected_customer = st.selectbox("Select a Customer ID to view journey:", sorted_df["CustomerID"].unique())
    customer_journey = sorted_df[sorted_df["CustomerID"] == selected_customer]
    st.write(f"### Customer {selected_customer}'s Journey Across Touchpoints")
    st.table(customer_journey[["Timestamp", "Activity", "Source"]])
else:
    st.warning("⚠️ Please ensure your CSVs include 'CustomerID' and 'Timestamp' columns for timeline analysis.")

# -----------------------------
# AI-LIKE INSIGHT
# -----------------------------
if "Activity" in combined_df.columns and "Source" in combined_df.columns:
    st.subheader("🤖 AI-Like Insight: Most Common Activity per Touchpoint")
    insight = combined_df.groupby("Source")["Activity"].agg(lambda x: x.value_counts().index[0])
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
into one connected, interactive journey map with summaries, charts, and timeline views.
""")
