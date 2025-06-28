import streamlit as st
import pandas as pd

st.title("🏗️ RERA Project Data Viewer")

# Upload JSON or CSV
uploaded_file = st.file_uploader("Upload your JSON/CSV file", type=["json", "csv"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]

    if file_type == 'json':
        df = pd.read_json(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.success("File uploaded and parsed successfully.")
    st.dataframe(df.head())

    # Dynamic Filter
    column = st.selectbox("Choose a column to filter", df.columns)

    if df[column].dtype == 'object':
        unique_vals = df[column].dropna().unique()
        filter_val = st.selectbox(f"Filter {column}", unique_vals)
        filtered_df = df[df[column] == filter_val]
    else:
        min_val, max_val = float(df[column].min()), float(df[column].max())
        range_val = st.slider(f"Filter {column} range", min_val, max_val, (min_val, max_val))
        filtered_df = df[df[column].between(range_val[0], range_val[1])]

    st.write("🔍 Filtered Data")
    st.dataframe(filtered_df)

# Export option
if 'filtered_df' in locals():
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", csv, "filtered_data.csv", "text/csv")
