# app.py
import streamlit as st
import pandas as pd
import io
import chardet
import csv

st.set_page_config(page_title="Universal Customer Journey Reader", layout="wide")
st.title("🧠 Universal CSV Reader – Customer Journey Mapper")

st.write("""
This version automatically detects **encoding**, **delimiter**, and **headers**.  
Upload any CSV file (even messy ones), and it will read it correctly.
""")

# ---------------------------
# Auto CSV reader
# ---------------------------
def smart_read_csv(uploaded_file):
    try:
        # Read first few bytes to detect encoding
        rawdata = uploaded_file.read()
        uploaded_file.seek(0)
        detected = chardet.detect(rawdata)
        encoding = detected["encoding"] or "utf-8"

        # Detect delimiter
        sample = rawdata[:10000].decode(encoding, errors="ignore")
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
        except Exception:
            delimiter = ','  # fallback

        # Load CSV into pandas
        df = pd.read_csv(io.BytesIO(rawdata), encoding=encoding, sep=delimiter, engine="python")
        uploaded_file.seek(0)
        return df, None
    except Exception as e:
        return None, str(e)

# ---------------------------
# Upload section
# ---------------------------
st.sidebar.header("📂 Upload CSV Files")
web_file = st.sidebar.file_uploader("Upload Website Data", type="csv")
app_file = st.sidebar.file_uploader("Upload Mobile App Data", type="csv")
store_file = st.sidebar.file_uploader("Upload Store Data", type="csv")

if not (web_file or app_file or store_file):
    st.info("👈 Please upload at least one CSV file to begin.")
    st.stop()

# ---------------------------
# Process uploaded files
# ---------------------------
dataframes = []
for file, label in [(web_file, "Website"), (app_file, "Mobile App"), (store_file, "Store")]:
    if file:
        df, err = smart_read_csv(file)
        if err:
            st.error(f"❌ Error reading {label}: {err}")
        else:
            df["Source"] = label
            st.success(f"✅ Successfully loaded {label} ({len(df)} rows)")
            st.write(df.head())
            dataframes.append(df)

if not dataframes:
    st.error("No readable CSV files uploaded. Please re-save them as CSV (Comma delimited).")
    st.stop()

# ---------------------------
# Merge data
# ---------------------------
combined = pd.concat(dataframes, ignore_index=True)

st.subheader("📊 Combined Dataset Preview")
st.dataframe(combined.head(50))

st.write(f"**Total Records:** {len(combined)}")
st.write(f"**Sources Loaded:** {', '.join(combined['Source'].unique())}")

# ---------------------------
# Try to identify useful columns
# ---------------------------
possible_cols = [c.lower() for c in combined.columns]
id_col = next((c for c in combined.columns if "id" in c.lower()), None)
time_col = next((c for c in combined.columns if "time" in c.lower() or "date" in c.lower()), None)
act_col = next((c for c in combined.columns if "activity" in c.lower() or "action" in c.lower()), None)

if id_col and time_col and act_col:
    st.success(f"✅ Detected columns: ID → {id_col}, Time → {time_col}, Activity → {act_col}")
    combined["Timestamp"] = pd.to_datetime(combined[time_col], errors="coerce")
    combined["CustomerID"] = combined[id_col].astype(str)
    combined["Activity"] = combined[act_col].astype(str)
else:
    st.warning("⚠️ Could not detect all key columns. Please check your headers manually.")

# ---------------------------
# Download option
# ---------------------------
st.subheader("💾 Download Combined Data")
csv_data = combined.to_csv(index=False).encode("utf-8")
st.download_button("Download Combined CSV", data=csv_data, file_name="combined_data.csv", mime="text/csv")

st.markdown("""
---
✅ **Tip:**  
If it still fails, open your file in Excel and click **Save As → CSV (UTF-8)** before uploading.
""")
