# utils/data_utils.py
import pandas as pd
import streamlit as st
from ai_agent.ai_agent import AIAgent

def load_and_validate_data(uploaded_files, agent: AIAgent):
    if len(uploaded_files) < 2:
        st.error("Please upload both historical and simulated CSV files.")
        return None, None

    # Assume user uploads historical first, then simulated
    try:
        historical_df = pd.read_csv(uploaded_files[0])
        simulated_df = pd.read_csv(uploaded_files[1])
    except Exception as e:
        st.error(f"Error loading CSVs: {e}")
        return None, None

    if not agent.validate_csv_structure(historical_df) or not agent.validate_csv_structure(simulated_df):
        st.error("CSV structure validation failed.")
        return None, None

    return historical_df, simulated_df
