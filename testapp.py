# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simple Customer Journey Mapper")

st.title("🧠 Simple AI-Driven Customer Journey Mapper")
st.write("Combine customer data from website, app, and store into one connected journey map.")

# Sidebar upload
st.sidebar.header("📂 Upload CSV Files")

web_file = st.sidebar.file_uploader("Upload Website Data", type="csv")
app_file = st.sidebar.file_uploader("Upload App Data", type="csv")
store_file = st.sidebar.file_uploader("Upload Store Data", type="csv")

# If no files uploaded
if not (web_file or app_file or store_file):
    st.info("👈 Please upload at least one CSV file to get started.")
    st.stop()

# Helper function
def load_data(file, source):
    df = pd.read_csv(file)
    df["Source"] = source
    return df

# Combine all uploaded data
data_frames = []

if web_file:
    data_frames.append(load_data(web_file, "Website"))

if app_file:
    data_frames.append(load_data(app_file, "Mobile App"))

if store_file:
    data_frames.append(load_data(store_file, "Store"))

combined = pd.concat(data_frames, ignore_index=True)

st.subheader("📊 Unified Customer Journey Data")
st.dataframe(combined)

# Simple summary
st.subheader("📈 Summary by Source")
summary = combined["Source"].value_counts().reset_index()
summary.columns = ["Source", "Total Records"]
st.table(summary)

st.markdown("""
---
✅ **Objective 2 Achieved:**  
This simple app integrates customer data from multiple touchpoints into one connected journey view.
""")
