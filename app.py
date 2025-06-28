import streamlit as st
import pandas as pd

st.set_page_config(page_title="RERA Viewer", layout="wide")

# Initialize session state
for key in ["df", "filtered_df", "index", "search_rera", "selected_status", "selected_state", "selected_district"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["df", "filtered_df"] else 0 if key == "index" else ""

st.title("🏗️ RERA Data Viewer")

# Upload CSV
uploaded_file = st.file_uploader("Upload your RERA CSV file", type=["csv"])
if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file, low_memory=False)
    st.session_state.filtered_df = st.session_state.df.copy()
    st.session_state.index = 0

# Define filter function
def apply_filters():
    df = st.session_state.df.copy()
    if st.session_state.search_rera:
        df = df[df['reraNo'].astype(str).str.contains(st.session_state.search_rera, case=False, na=False)]
    if st.session_state.selected_status:
        df = df[df['projectStatus'] == st.session_state.selected_status]
    if st.session_state.selected_state:
        df = df[df['state'] == st.session_state.selected_state]
    if st.session_state.selected_district:
        df = df[df['district'] == st.session_state.selected_district]

    st.session_state.filtered_df = df
    st.session_state.index = 0

# Only show filters and data if CSV is loaded
if st.session_state.df is not None:
    df = st.session_state.df

    with st.sidebar:
        st.header("🔍 Filter Options")

        st.session_state.search_rera = st.text_input("Search RERA No", value=st.session_state.search_rera)

        if 'projectStatus' in df.columns:
            options = [""] + sorted(df['projectStatus'].dropna().astype(str).unique())
            st.session_state.selected_status = st.selectbox("Project Status", options, index=options.index(st.session_state.selected_status) if st.session_state.selected_status in options else 0)

        if 'state' in df.columns:
            options = [""] + sorted(df['state'].dropna().astype(str).unique())
            st.session_state.selected_state = st.selectbox("State", options, index=options.index(st.session_state.selected_state) if st.session_state.selected_state in options else 0)

        if 'district' in df.columns:
            options = [""] + sorted(df['district'].dropna().astype(str).unique())
            st.session_state.selected_district = st.selectbox("District", options, index=options.index(st.session_state.selected_district) if st.session_state.selected_district in options else 0)

        if st.button("Apply Filter"):
            apply_filters()

        if st.button("Clear Filters"):
            st.session_state.search_rera = ""
            st.session_state.selected_status = ""
            st.session_state.selected_state = ""
            st.session_state.selected_district = ""
            st.session_state.filtered_df = df.copy()
            st.session_state.index = 0

    # View records
    if st.session_state.filtered_df is not None and not st.session_state.filtered_df.empty:
        record = st.session_state.filtered_df.iloc[st.session_state.index]

        st.subheader(f"📄 Record {st.session_state.index + 1} of {len(st.session_state.filtered_df)}")
        for col, val in record.items():
            st.markdown(f"**{col}**: {val}")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Previous") and st.session_state.index > 0:
                st.session_state.index -= 1
                st.experimental_rerun()
        with col2:
            if st.button("➡️ Next") and st.session_state.index < len(st.session_state.filtered_df) - 1:
                st.session_state.index += 1
                st.experimental_rerun()
    else:
        st.warning("No records found with current filters.")
else:
    st.info("📤 Please upload a CSV file to get started.")
