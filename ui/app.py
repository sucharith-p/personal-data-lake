import streamlit as st
import pandas as pd
import requests
import io

def convert_df(df, fmt):
    if fmt == "CSV":
        return df.to_csv(index=False).encode("utf-8")
    elif fmt == "Parquet":
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        return buffer.getvalue()
    elif fmt == "JSON":
        return df.to_json(orient="records", indent=2).encode("utf-8")

def get_mime_type(fmt):
    return {
        "CSV": "text/csv",
        "Parquet": "application/octet-stream",
        "JSON": "application/json"
    }[fmt]

BASE_URL = "http://localhost:8000"

# --- Page Config ---
st.set_page_config(
    page_title="Personal Data Lake",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- Session state ---
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

# --- App Title ---
st.markdown("## 🧊 Personal Data Lake-as-a-Service")
st.markdown("Lightweight backend to store, manage, and query structured data files.")

st.markdown("---")

# === Upload Section ===
st.markdown("### 📤 Upload a File")
st.caption("Choose a CSV, JSON, or Parquet file (limit: 200MB)")

upload_col1, upload_col2 = st.columns([6, 1])
with upload_col1:
    uploaded_file = st.file_uploader(
        "Drag and drop file here", 
        type=["csv", "json", "parquet"], 
        label_visibility="collapsed"
    )
with upload_col2:
    st.write("")  # Spacer
    st.write("")  # Spacer
    upload_clicked = st.button("Upload File", use_container_width=False)

if uploaded_file and upload_clicked:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    if response.status_code == 200:
        st.success("✅ File uploaded successfully!")
    else:
        st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")


st.markdown("---")

# === Dataset Listing Section ===
st.markdown("### 📁 Uploaded Datasets")
flush_col, table_col = st.columns([1, 9])

try:
    response = requests.get(f"{BASE_URL}/datasets")
    response.raise_for_status()
    datasets = response.json()
except Exception as e:
    st.error("Failed to load datasets.")
    datasets = []
with flush_col:
    if st.button("Flush Metadata", help="Remove metadata entries for missing files"):
        response = requests.delete(f"{BASE_URL}/datasets/cleanup")
        if response.status_code == 200:
            result = response.json()
            print(f"[Flush Metadata] Deleted {result['deleted_count']} entries: {result['deleted_datasets']}")
        else:
            print("⚠️ Flush failed:", response.text)
with table_col:           
    if datasets:
        df = pd.DataFrame(datasets)
        st.dataframe(df[["dataset_name", "upload_time", "file_size_kb"]], use_container_width=True)
        dataset_names = df["dataset_name"].tolist()
    else:
        st.warning("📭 No datasets found in your bucket. Upload a file to get started.")
        selected = None

st.markdown("---")

# === Query Section ===
st.markdown("### 🔍 Run a SQL Query")
st.caption("💡 Use table names based on uploaded file names (e.g., `Iris`, `demo`)")


sql = st.text_area("Enter SQL", value="", height=200)

if st.button("Run Query"):
    payload = {"sql": sql}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    if response.status_code == 200:
        result_df = pd.DataFrame(response.json()["rows"])
        if result_df.empty:
            st.info("⚠️ Query returned no results.")
        else:
            st.success("✅ Query succeeded.")
            st.dataframe(result_df, use_container_width=True)
    else:
        st.error(f"❌ Query failed: {response.json().get('detail', 'Unknown error')}")
    if response.status_code == 200:
        rows = response.json().get("rows", [])
        if rows:
            df = pd.DataFrame(rows)

            # Export options
            export_format = st.selectbox("Export format", ["CSV", "Parquet", "JSON"])
            if st.download_button(
                label="⬇️ Download Query Results",
                data=convert_df(df, export_format),
                file_name=f"query_results.{export_format.lower()}",
                mime=get_mime_type(export_format)
            ):
                st.success("File downloaded!")
    else:
        st.warning("Query returned no results.")
