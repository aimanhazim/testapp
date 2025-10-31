# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

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
# FILTERS (NEW)
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
# SUMMARY STATISTICS (ENHANCED)
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
# VISUALIZATIONS (NEW)
# -----------------------------
st.subheader("📊 Visual Insights")

# Bar chart by Source
if "Source" in combined_df.columns:
    source_summary = combined_df["Source"].value_counts().reset_index()
    source_summary.columns = ["Source", "Total Records"]
    fig_bar = px.bar(source_summary, x="Source", y="Total Records", color="Source", title="Records by Source")
    st.plotly_chart(fig_bar, use_container_width=True)

# Pie chart by Activity
if "Activity" in combined_df.columns:
    activity_summary = combined_df["Activity"].value_counts().reset_index()
    activity_summary.columns = ["Activity", "Count"]
    fig_pie = px.pie(activity_summary, names="Activity", values="Count", title="Activity Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

# Timeline chart
if "Timestamp" in combined_df.columns:
    combined_df["Date"] = combined_df["Timestamp"].dt.date
    trend_d_
