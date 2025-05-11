import streamlit as st
import pandas as pd
import plotly.express as px
from attack_simulator import BaseAttackSimulator
from coordinated_attack import simulate_coordinated_attack
from ai_agent.ai_agent import AIAgent  
from AIAgent import alidate_csv_structure, generate_ai_summary, generate_analysis_summary, summarize_attack_effects
from visualizations.dashboard_components import (
    render_radar_chart,
    render_heatmap,
    render_comparative_dashboard
)
import os

# Paths
DEFAULT_DATA_PATH = "data/normal_and_anomalous_flaged_df.csv"
REQUIRED_COLUMNS = 36

# Load default or user-uploaded CSV
st.set_page_config(page_title="Cyber Attack Simulator", layout="wide")
st.title("🛡️ Cyber Attack Simulator & AI Threat Insights")

st.sidebar.header("⚙️ Attack Configuration")
use_default = st.sidebar.radio("Select Data Source", ["Use Default CSV", "Upload Your Own CSV"])

# Load data
if use_default == "Use Default CSV":
    try:
        data = pd.read_csv(DEFAULT_DATA_PATH)
        st.success("✅ Default CSV loaded successfully.")
    except Exception as e:
        st.error(f"Failed to load default CSV: {e}")
        st.stop()
else:
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file:
        try:
            data = pd.read_csv(uploaded_file)
            st.success("✅ File uploaded successfully.")
        except Exception as e:
            st.error(f"❌ Failed to read file: {e}")
            st.stop()
    else:
        st.warning("⚠️ Please upload a file to continue.")
        st.stop()

# --- AI Validation ---
if not validate_csv_structure(data):
    st.error("❌ CSV validation failed. Please upload a file with correct structure (36 columns).")
    st.stop()
else:
    st.success("✅ CSV structure validated by AI agent.")

# --- Select attack(s) ---
attack_options = [
    "phishing",
    "malware",
    "ddos",
    "data_leak",
    "insider",
    "ransomware"
]
attack_selection = st.sidebar.multiselect("Choose Attack Types to Simulate", attack_options)

anomaly_magnitude = st.sidebar.slider("Anomaly Magnitude", 1.0, 5.0, 2.0, 0.1)
phase = st.sidebar.selectbox("Attack Phase", ["initial", "escalation", "exfiltration"])

run_button = st.sidebar.button("🚨 Run Simulation")

if run_button:
    if not attack_selection:
        st.warning("⚠️ Please select at least one attack.")
        st.stop()

    st.subheader("🔄 Running Individual Attack Simulation...")
    simulator = BaseAttackSimulator(data, anomaly_magnitude=anomaly_magnitude, phase=phase)
    simulated_df = simulator.run_multiple_attacks(attack_selection)
    st.success("✅ Individual Attack Simulation Completed!")

    st.subheader("🔄 Running Coordinated Attack Simulation...")
    coordinated_df, attack_log = simulate_coordinated_attack(
        base_data=data,
        anomaly_magnitude=anomaly_magnitude
    )
    st.success("✅ Coordinated Attack Simulation Completed!")

    # Save CSV for coordinated attack
    coordinated_df.to_csv("data/simulated_attack_data.csv", index=False)
    
    # Display raw table
    st.subheader("Simulation Results")
    st.dataframe(coordinated_df)

    # --- Visual Summary Components ---
    render_radar_chart(coordinated_df)
    render_heatmap(coordinated_df)

    if "simulated_df" in locals():
        render_comparative_dashboard(simulated_df, coordinated_df)
        
    # --- Animated Progression ---
    st.subheader("🎞️ Animated Threat Progression")
    fig = px.scatter(
        coordinated_df,
        x="Threat Score",
        y="Severity",
        animation_frame="Phase",
        color="Threat Level",
        size="Cost" if "Cost" in coordinated_df.columns else None,
        hover_name="Category" if "Category" in coordinated_df.columns else None,
        title="Threat Score vs Severity Over Phases"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Comparative Dashboard ---
    st.subheader("📊 Comparative Threat Impact Dashboard")
    combined_comparison_df = pd.concat([
        simulated_df.assign(Source="Individual"),
        coordinated_df.assign(Source="Coordinated")
    ])

    col1, col2 = st.columns(2)
    with col1:
        box_fig = px.box(
            combined_comparison_df,
            x="Source",
            y="Threat Score",
            color="Source",
            title="Threat Score Distribution"
        )
        st.plotly_chart(box_fig, use_container_width=True)

    with col2:
        bar_fig = px.histogram(
            combined_comparison_df,
            x="Threat Level",
            color="Source",
            barmode="group",
            title="Threat Level Frequency: Individual vs Coordinated"
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    # --- AI Executive Summary ---
    st.subheader("🧠 AI Executive Summary")
    ai_summary = generate_ai_summary(coordinated_df)
    st.markdown(ai_summary)

    # --- Download ---
    st.download_button("💾 Download Coordinated Attack Data as CSV",
                       coordinated_df.to_csv(index=False),
                       file_name="simulated_attack_data.csv")
