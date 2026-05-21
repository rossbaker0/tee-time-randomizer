# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd

# Imports optimization script
from generate_optimal_pairings import generate_optimal_pairings

st.title("Tee Time Randomizer")

# User uploads file
uploaded_file = st.file_uploader("Upload your roster file (Excel or CSV)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df, hide_index=True)

    # Filter for active players based on the uploaded data
    active_df = df[df['Playing'] == 1]

    st.divider() 

    if st.button("Generate Tee Times"):

        try:
            with st.spinner("Calculating optimal pairings..."):
                final_groups, score = generate_optimal_pairings(active_df, prioritize_tees=True)

            st.success("Groups generated successfully!")
            st.write(f"**Optimization Score:** {score}")

            for i, group in enumerate(final_groups, 1):
                group_with_tees = [f"{p} ({df.loc[df['Player']==p, 'Tee'].values[0]})" for p in group]

                st.info(f"**Group {i}:** {', '.join(group_with_tees)}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
