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
into a single connected journey map with enhanced analytics, interactive filters, and visual insights.
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
# LOAD FUNCTION (KEEPED SAME)
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

# Ensure Timestamp exists and convert
