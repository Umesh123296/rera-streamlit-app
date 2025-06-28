import streamlit as st
import pandas as pd

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.filtered_df = None
    st.session_state.index = 0

st.title("🏗️ RERA CSV Viewer with Dynamic Filters")

# Upload CSV
uploaded_file = st.file_uploader("Upload your RERA CSV file", type=["csv"])
if uploaded_file:
    st.session_state.df = pd.read_csv(uploaded_file, low_memory=False)
    st.session_state.filtered_df = st.session_state.df.copy()
    st.session_state.index = 0

# If CSV is uploaded
if st.session_state.df is not None:
    df = st.session_state.df
    filtered_df = st.session_state.filtered_df

    # Dynamic Filters
    with st.sidebar:
        st.header("🔍 Filter Options")
        search_rera = st.text_input("Search RERA No")

        filters = {}
        for col in ['projectStatus', 'state', 'district']:
            if col in df.columns:
                options = df[col].dropna().unique()
                filters[col] = st.selectbox(f"Select {col}", [""] + sorted(options), key=col)

        # Filter logic
        def apply_filters():
            fdf = df.copy()
            if search_rera:
                fdf = fdf[fdf['reraNo'].astype(str).str.contains(search_rera, case=False, na=False)]
            for col, val in filters.items():
                if val:
                    fdf = fdf[fdf[col] == val]
            st.session_state.filtered_df = fdf
            st.session_state.index = 0

        def clear_filters():
            for col in filters:
                st.session_state[col] = ""
            st.session_state.index = 0
            st.session_state.filtered_df = df.copy()

        st.button("Apply Filter", on_click=apply_filters)
        st.button("Clear Filters", on_click=clear_filters)

    # Record Viewer
    if not filtered_df.empty:
        record = filtered_df.iloc[st.session_state.index]

        st.subheader(f"📄 Record {st.session_state.index + 1} of {len(filtered_df)}")
        for col, val in record.items():
            st.markdown(f"**{col}:** {val}")

        # Navigation Buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.index <= 0):
                st.session_state.index -= 1
        with col2:
            if st.button("➡️ Next", disabled=st.session_state.index >= len(filtered_df) - 1):
                st.session_state.index += 1
    else:
        st.warning("No records found.")
else:
    st.info("Please upload a CSV file to get started.")
