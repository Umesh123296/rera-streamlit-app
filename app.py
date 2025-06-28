import streamlit as st
import pandas as pd

st.set_page_config(page_title="RERA Viewer", layout="wide")

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None
if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None
if "index" not in st.session_state:
    st.session_state.index = 0
if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False

st.title("🏗️ RERA CSV Viewer with Dynamic Filters")

# Upload CSV
uploaded_file = st.file_uploader("Upload your RERA CSV file", type=["csv"])
if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file, low_memory=False)
    st.session_state.filtered_df = st.session_state.df.copy()
    st.session_state.index = 0
    st.session_state.filters_applied = False

# Only show filters and data if CSV is loaded
if st.session_state.df is not None:
    df = st.session_state.df

    with st.sidebar:
        st.header("🔍 Filter Options")

        search_rera = st.text_input("Search RERA No")

        selected_status = ""
        selected_state = ""
        selected_district = ""

        if 'projectStatus' in df.columns:
            selected_status = st.selectbox("Project Status", [""] + sorted(df['projectStatus'].dropna().unique().astype(str)))

        if 'state' in df.columns:
            selected_state = st.selectbox("State", [""] + sorted(df['state'].dropna().unique().astype(str)))

        if 'district' in df.columns:
            selected_district = st.selectbox("District", [""] + sorted(df['district'].dropna().unique().astype(str)))

        if st.button("Apply Filter"):
            fdf = df.copy()

            if search_rera:
                fdf = fdf[fdf['reraNo'].astype(str).str.contains(search_rera, case=False, na=False)]

            if selected_status:
                fdf = fdf[fdf['projectStatus'] == selected_status]

            if selected_state:
                fdf = fdf[fdf['state'] == selected_state]

            if selected_district:
                fdf = fdf[fdf['district'] == selected_district]

            st.session_state.filtered_df = fdf
            st.session_state.index = 0
            st.session_state.filters_applied = True

        if st.button("Clear Filters"):
            st.session_state.filtered_df = df.copy()
            st.session_state.index = 0
            st.session_state.filters_applied = False

    # Show filtered results
    filtered_df = st.session_state.filtered_df

    if filtered_df is not None and not filtered_df.empty:
        record = filtered_df.iloc[st.session_state.index]
        st.subheader(f"📄 Record {st.session_state.index + 1} of {len(filtered_df)}")

        for col, val in record.items():
            st.markdown(f"**{col}**: {val}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Previous") and st.session_state.index > 0:
                st.session_state.index -= 1
        with col2:
            if st.button("➡️ Next") and st.session_state.index < len(filtered_df) - 1:
                st.session_state.index += 1
    else:
        st.warning("No records found for current filters.")
else:
    st.info("📤 Please upload a CSV file to begin.")
