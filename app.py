import streamlit as st
import pandas as pd

# Session state initialization
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.filtered_df = None
    st.session_state.index = 0

st.title("🏗️ RERA CSV Viewer with Dynamic Filters")

# Upload CSV
uploaded_file = st.file_uploader("Upload your RERA CSV file", type=["csv"])
if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file, low_memory=False)
    st.session_state.filtered_df = st.session_state.df.copy()
    st.session_state.index = 0

# Display filters and data if a CSV has been uploaded
if st.session_state.df is not None:
    df = st.session_state.df
    filtered_df = st.session_state.filtered_df

    with st.sidebar:
        st.header("🔍 Filter Options")

        search_rera = st.text_input("Search by RERA No")

        selected_status = st.selectbox(
            "Select Project Status",
            options=[""] + sorted(df['projectStatus'].dropna().unique().tolist())
            if 'projectStatus' in df.columns else [],
            key="status"
        )

        selected_state = st.selectbox(
            "Select State",
            options=[""] + sorted(df['state'].dropna().unique().tolist())
            if 'state' in df.columns else [],
            key="state"
        )

        selected_district = st.selectbox(
            "Select District",
            options=[""] + sorted(df['district'].dropna().unique().tolist())
            if 'district' in df.columns else [],
            key="district"
        )

        def apply_filters():
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

        def clear_filters():
            st.session_state.status = ""
            st.session_state.state = ""
            st.session_state.district = ""
            st.session_state.filtered_df = df.copy()
            st.session_state.index = 0

        st.button("Apply Filter", on_click=apply_filters)
        st.button("Clear Filters", on_click=clear_filters)

    # Record viewer
    if not st.session_state.filtered_df.empty:
        record = st.session_state.filtered_df.iloc[st.session_state.index]
        st.subheader(f"📄 Record {st.session_state.index + 1} of {len(st.session_state.filtered_df)}")

        for col, val in record.items():
            st.markdown(f"**{col}**: {val}")

        # Navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.index <= 0):
                st.session_state.index -= 1
        with col2:
            if st.button("➡️ Next", disabled=st.session_state.index >= len(st.session_state.filtered_df) - 1):
                st.session_state.index += 1
    else:
        st.warning("No records found for current filters.")
else:
    st.info("📤 Please upload a CSV file to begin.")
