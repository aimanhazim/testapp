# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(page_title="AI-Driven Customer Journey Mapper", layout="wide")

st.title("🧠 AI-Driven Multi-Touchpoint Customer Journey Mapper")
st.write("""
This demo application integrates data from **online browsing**, **mobile app usage**, 
and **physical store visits** into a unified view of the customer journey.
""")

# -----------------------------
# DATA INPUT SECTION
# -----------------------------
st.sidebar.header("📂 Upload or Input Data")

uploaded_web = st.sidebar.file_uploader("Upload Website Data (CSV)", type="csv")
uploaded_app = st.sidebar.file_uploader("Upload Mobile App Data (CSV)", type="csv")
uploaded_store = st.sidebar.file_uploader("Upload Physical Store Data (CSV)", type="csv")

# If no files uploaded, show a message
if not uploaded_web and not uploaded_app and not uploaded_store:
    st.info("👈 Please upload at least one dataset to begin.")
    st.stop()

# -----------------------------
# READ AND LABEL DATA
# -----------------------------
def load_and_label(data, source_name):
    df = pd.read_csv(data)
    df["Source"] = source_name
    return df

dataframes = []

if uploaded_web:
    web_df = load_and_label(uploaded_web, "Website")
    dataframes.append(web_df)

if uploaded_app:
    app_df = load_and_label(uploaded_app, "Mobile App")
    dataframes.append(app_df)

if uploaded_store:
    store_df = load_and_label(uploaded_store, "Store")
    dataframes.append(store_df)

# -----------------------------
# MERGE ALL DATA
# -----------------------------
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)

    st.subheader("📊 Unified Customer Journey Data")
    st.dataframe(combined_df.head())

    # -----------------------------
    # SIMPLE VISUALIZATION
    # -----------------------------
    if "CustomerID" in combined_df.columns and "Timestamp" in combined_df.columns:
        st.subheader("🔍 Customer Journey Overview")

        # Sort data for timeline visualization
        combined_df["Timestamp"] = pd.to_datetime(combined_df["Timestamp"], errors="coerce")
        combined_df = combined_df.sort_values(by=["CustomerID", "Timestamp"])

        fig = px.scatter(
            combined_df,
            x="Timestamp",
            y="CustomerID",
            color="Source",
            title="Customer Journey Across Touchpoints",
            labels={"Source": "Touchpoint", "CustomerID": "Customer ID"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Please ensure your CSV files include 'CustomerID' and 'Timestamp' columns for visualization.")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
---
✅ **Objective 2 Achieved:**  
This simple app demonstrates how customer data from **web**, **mobile**, and **store** sources 
can be integrated into one connected customer journey map through an interactive interface.
""")
