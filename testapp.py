# app.py
import streamlit as st
import pandas as pd
import io
import csv
from datetime import datetime

st.set_page_config(page_title="Robust Customer Journey Mapper", layout="wide")
st.title("🧰 Robust Customer Journey Mapper (Upload + Map Columns)")

st.write("""
Upload CSV or Excel files from Website, Mobile App, and Store.
This app will try to read different encodings/delimiters and lets you map columns if headers differ.
""")

# -------------------------
# Helpers: Robust CSV/Excel reader
# -------------------------
def detect_delimiter(sample_bytes):
    """
    Use csv.Sniffer to guess delimiter from sample bytes (decoded to text).
    """
    try:
        text = sample_bytes.decode("utf-8")
    except Exception:
        try:
            text = sample_bytes.decode("latin1")
        except Exception:
            return ","
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(text[:4096])
        return dialect.delimiter
    except Exception:
        # fallback try common delimiters
        for d in [",", ";", "\t", "|"]:
            if d in text:
                return d
        return ","

def try_read_table(uploaded_file):
    """
    Try reading uploaded file robustly. Returns DataFrame or (None, error_msg).
    """
    name = uploaded_file.name.lower()
    data_bytes = uploaded_file.read()
    uploaded_file.seek(0)  # reset for further reads by streamlit

    # If Excel
    if name.endswith((".xls", ".xlsx")):
        try:
            df = pd.read_excel(io.BytesIO(data_bytes))
            return df, None
        except Exception as e:
            return None, f"Excel read error: {e}"

    # Otherwise assume text (CSV-like). Try detection and multiple encodings.
    # Detect delimiter using a sample
    delim = detect_delimiter(data_bytes[:10000])
    # Try encodings
    for enc in ("utf-8", "latin1", "cp1252"):
        try:
            text_io = io.StringIO(data_bytes.decode(enc))
            df = pd.read_csv(text_io, sep=delim, engine="python")
            return df, None
        except Exception as e:
            # try pandas auto-detect separators as last resort
            try:
                df = pd.read_csv(io.StringIO(data_bytes.decode(enc)))
                return df, None
            except Exception:
                last_err = e
                continue
    return None, f"Failed to parse file. Last error: {last_err}"

# -------------------------
# Upload UI
# -------------------------
st.sidebar.header("Upload files")
web_file = st.sidebar.file_uploader("Website data (CSV / XLSX)", type=["csv", "xls", "xlsx"])
app_file = st.sidebar.file_uploader("Mobile app data (CSV / XLSX)", type=["csv", "xls", "xlsx"])
store_file = st.sidebar.file_uploader("Store data (CSV / XLSX)", type=["csv", "xls", "xlsx"])

if not (web_file or app_file or store_file):
    st.info("Please upload at least one file (website / app / store).")
    st.stop()

# -------------------------
# Read each uploaded file and preview
# -------------------------
uploaded_items = []
for f, label in [(web_file, "Website"), (app_file, "Mobile App"), (store_file, "Store")]:
    if f:
        with st.expander(f"Preview: {label} - {f.name}", expanded=True):
            df, err = try_read_table(f)
            if err:
                st.error(f"Could not read {f.name}: {err}")
                st.write("Try opening the file in Excel and saving as CSV (comma) with UTF-8 encoding.")
                st.stop()
            else:
                st.success(f"Successfully read {f.name} (rows: {len(df)})")
                st.dataframe(df.head(10))
                uploaded_items.append((label, df.copy(), f.name))

# -------------------------
# Column mapping UI (for each uploaded dataset)
# -------------------------
st.sidebar.header("Column mapping (required)")
mapped_frames = []
required_cols = {"CustomerID": None, "Timestamp": None, "Activity": None}
for (label, df, fname) in uploaded_items:
    st.sidebar.subheader(f"Map columns for: {label} ({fname})")
    cols = list(df.columns)
    # lower-case display but store original names
    cust = st.sidebar.selectbox(f"{label}: Customer ID column", ["--Select--"] + cols, key=f"{label}_cust")
    ts = st.sidebar.selectbox(f"{label}: Timestamp column", ["--Select--"] + cols, key=f"{label}_ts")
    act = st.sidebar.selectbox(f"{label}: Activity column", ["--Select--"] + cols, key=f"{label}_act")
    # Validation
    if cust == "--Select--" or ts == "--Select--" or act == "--Select--":
        st.sidebar.warning(f"Please map all three columns for {label}.")
        st.stop()
    # Rename columns in a copy
    df2 = df.rename(columns={cust: "CustomerID", ts: "Timestamp", act: "Activity"})
    mapped_frames.append((label, df2))

# -------------------------
# Standardize and merge
# -------------------------
def standardize_df(df, source_label):
    # ensure columns exist
    if "CustomerID" not in df.columns or "Timestamp" not in df.columns or "Activity" not in df.columns:
        raise ValueError("Required columns missing after mapping.")
    # convert Timestamp
    df["Source"] = source_label
    # Try to parse timestamp to datetime
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    # Trim whitespace from CustomerID and Activity
    df["CustomerID"] = df["CustomerID"].astype(str).str.strip()
    df["Activity"] = df["Activity"].astype(str).str.strip()
    return df

clean_frames = []
for label, df in mapped_frames:
    try:
        dfc = standardize_df(df, label)
        clean_frames.append(dfc)
    except Exception as e:
        st.error(f"Error standardizing {label}: {e}")
        st.stop()

if not clean_frames:
    st.error("No valid dataframes after mapping.")
    st.stop()

combined = pd.concat(clean_frames, ignore_index=True)

st.subheader("🔗 Combined Data (first 50 rows)")
st.dataframe(combined.head(50))

# -------------------------
# Quick validation & helpful warnings
# -------------------------
if combined["Timestamp"].isna().all():
    st.warning("All timestamps failed to parse into datetime. Check formats (e.g., 'YYYY-MM-DD HH:MM').")
else:
    n_na = combined["Timestamp"].isna().sum()
    if n_na > 0:
        st.warning(f"{n_na} rows have missing/unparsed Timestamps.")

# -------------------------
# Simple interactive exploration
# -------------------------
st.subheader("🔎 Explore")

# Filters
unique_customers = combined["CustomerID"].unique().tolist()
selected_customer = st.selectbox("Select CustomerID (or All)", ["All"] + unique_customers)

min_ts = combined["Timestamp"].min()
max_ts = combined["Timestamp"].max()
if pd.notna(min_ts) and pd.notna(max_ts):
    date_range = st.date_input("Date range", [min_ts.date(), max_ts.date()])
else:
    date_range = None

df_view = combined.copy()
if selected_customer != "All":
    df_view = df_view[df_view["CustomerID"] == selected_customer]
if date_range and len(date_range) == 2 and pd.notna(min_ts):
    start = pd.to_datetime(date_range[0])
    end = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    df_view = df_view[(df_view["Timestamp"] >= start) & (df_view["Timestamp"] <= end)]

st.write(f"Showing {len(df_view)} records")
st.dataframe(df_view.sort_values(by=["CustomerID", "Timestamp"]).reset_index(drop=True))

# -------------------------
# Simple stats
# -------------------------
st.subheader("📈 Summary")
col_count = df_view["Source"].value_counts().reset_index().rename(columns={"index": "Source", "Source": "Count"})
st.table(col_count)

st.markdown("---")
st.write("✅ You can now download the cleaned combined dataset below.")
csv = combined.to_csv(index=False).encode("utf-8")
st.download_button("Download combined CSV", csv, "combined_customer_journey.csv", "text/csv")
