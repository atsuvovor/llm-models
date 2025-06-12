#app.py
import os
import threading
import streamlit as st
import pandas as pd
import plotly.express as px

from simulation.attack_simulator import BaseAttackSimulator
from simulation.coordinated_attack import simulate_coordinated_attack
from ai_agent.ai_agent import AIAgent
from ai_agent import validator
from models.llm_loader import load_llm
from utils.chat_utils import init_chat, render_chat_interface
from visualizations.dashboard_components import (
    render_threat_charts,
    render_executive_summary_dashboard,
    render_comparative_dashboard,
)
from visualizations.dashboard_summary_tabs import launch_attacks_charts_dashboard
from ui.gguf_downloader import render_gguf_model_downloader
from ai_agent.config import Settings


def launch_dashboard_summary_tabs(df):
    def run_dash_app(df):
        dash_app = launch_attacks_charts_dashboard(df)
        dash_app.run_server(debug=False, port=8050, use_reloader=False)

    threading.Thread(target=run_dash_app, args=(df,), daemon=True).start()
    st.subheader("📊 Embedded Dash Dashboard")
    st.components.v1.iframe("http://localhost:8050", height=1000, scrolling=True)


def load_data(use_default, uploaded_file):
    DEFAULT_DATA_PATH = "data/normal_and_anomalous_flaged_df.csv"
    if use_default:
        path = DEFAULT_DATA_PATH
    else:
        if not uploaded_file:
            st.warning("⚠️ Please upload a file to continue.")
            st.stop()
        path = uploaded_file

    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"❌ Failed to load CSV: {e}")
        st.stop()


def configure_sidebar():
    st.sidebar.header("⚙️ Data Source")
    use_default = st.sidebar.radio("Select Data Source", ["Use Default CSV", "Upload Your Own CSV"]) == "Use Default CSV"
    uploaded_file = None if use_default else st.sidebar.file_uploader("Upload CSV", type=["csv"])

    st.sidebar.header("🧠 LLM Configuration")
    render_gguf_model_downloader(Settings)
    Settings.model_list = Settings._get_model_list()

    if not Settings.model_list:
        st.error("❌ No GGUF models found in 'models/gguf'. Please add at least one.")
        st.stop()

    selected_model = st.sidebar.selectbox("Choose a GGUF Model", Settings.model_list)
    Settings.update_selected_model(selected_model)

    rag_enabled = st.sidebar.toggle("Enable RAG", value=True)
    chat_on = st.sidebar.toggle("💬 Enable Chat", value=True)
    clear_chat = st.sidebar.button("Clear Chat History")

    return use_default, uploaded_file, rag_enabled, chat_on, clear_chat


def run_attack_simulation(df, selected_attacks, anomaly_magnitude, selected_phases):
    if len(selected_phases) > 1:
        st.subheader("🔄 Running Coordinated Attack...")
        attack_seq = {phase: selected_attacks for phase in selected_phases}
        simulated_df, attack_log = simulate_coordinated_attack(
            base_data=df,
            phases=selected_phases,
            attack_sequence=attack_seq,
            anomaly_magnitude=anomaly_magnitude
        )
    else:
        st.subheader("🔄 Running Single-Phase Attack...")
        simulator = BaseAttackSimulator(df, anomaly_magnitude=anomaly_magnitude, phase=selected_phases[0])
        simulated_df = simulator.run_multiple_attacks(selected_attacks)
        simulated_df["Phase"] = selected_phases[0]
        attack_log = [(selected_phases[0], selected_attacks)]

    return simulated_df, attack_log


def render_attack_analysis(agent, df, simulated_df, attack_log):
    st.success("✅ Attack Simulation Completed!")
    st.subheader("📝 Coordinated Attack Summary")
    st.dataframe(simulated_df)
    for phase, attacks in attack_log:
        st.markdown(f"- **{phase.title()} Phase**: {', '.join(attacks)}")

    st.session_state.simulated_df = simulated_df

    st.subheader("🧠 Executive Summary")
    st.markdown(agent.generate_analysis_summary(simulated_df))
    st.markdown(agent.summarize_attack_effects(simulated_df))
    render_threat_charts(simulated_df)

    st.subheader("🎞️ Animated Threat Progression")
    fig = px.scatter(
        simulated_df, x="Threat Score", y="Severity",
        animation_frame="Phase", color="Threat Level",
        size="Cost" if "Cost" in simulated_df.columns else None,
        hover_name="Category" if "Category" in simulated_df.columns else None,
        title="Threat Score vs Severity Over Phases"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_dashboard(df, simulated_df, chat_on, agent):
    missing_cols = [col for col in simulated_df.columns if col not in df.columns]
    for col in missing_cols:
        df[col] = ""
    combined_df = pd.concat([df, simulated_df], ignore_index=True)
    '''
    st.sidebar.header("📂 Executive Dashboard Filters")
    departments = combined_df["Department Affected"].dropna().unique()
    selected_depts = st.sidebar.multiselect("Filter by Department", departments, default=list(departments))
    severities = combined_df['Severity'].dropna().unique()
    selected_severities = st.sidebar.multiselect("Filter by Severity", severities, default=list(severities))

    filtered_df = combined_df[
        (combined_df["Department Affected"].isin(selected_depts)) &
        (combined_df["Severity"].isin(selected_severities))
    ]
    '''
    st.subheader("📈 Executive Summary Dashboard")
    filtered_dfn
    filtered_df = render_executive_summary_dashboard(combined_df)
    #render_executive_summary_dashboard(filtered_df)
    #launch_dashboard_summary_tabs(filtered_df)
    launch_dashboard_summary_tabs(combined_df)

    st.download_button("💾 Download Coordinated Attack CSV",
                       simulated_df.to_csv(index=False),
                       file_name="simulated_attack_data.csv")

    if chat_on:
        st.divider()
        render_chat_interface(agent, filtered_df)


def main():
    st.set_page_config(page_title="Cyber Attack Simulator", layout="wide")
    st.title("🛡️ Cyber Attack Simulator & AI Threat Insights")

    use_default, uploaded_file, rag_enabled, chat_on, clear_chat = configure_sidebar()

    if chat_on:
        init_chat(clear=clear_chat)

    df = load_data(use_default, uploaded_file)

    agent = AIAgent(validator.expected_columns("csv"), df, use_rag=rag_enabled)
    if not agent.validate_csv_structure(df):
        st.error("❌ CSV structure validation failed.")
        st.stop()

    st.success("✅ CSV structure validated by AI agent.")
    agent.print_df_info(df)

    attack_options = ["phishing", "malware", "ddos", "data_leak", "insider", "ransomware"]
    selected_attacks = st.sidebar.multiselect("Choose Attack Types", attack_options)
    anomaly_magnitude = st.sidebar.slider("Anomaly Magnitude", 1.0, 5.0, 2.0, 0.1)
    run_all_phases = st.sidebar.checkbox("Run Full Multi-Phase Coordinated Attack", value=False)
    selected_phases = ["initial", "escalation", "critical"] if run_all_phases else [st.sidebar.selectbox("Select Phase", ["initial", "escalation", "critical"])]
    run_button = st.sidebar.button("🚨 Run Simulation")

    if run_button:
        if not selected_attacks:
            st.warning("⚠️ Select at least one attack.")
            st.stop()

        simulated_df, attack_log = run_attack_simulation(df, selected_attacks, anomaly_magnitude, selected_phases)
        render_attack_analysis(agent, df, simulated_df, attack_log)

    if "simulated_df" in st.session_state:
        render_dashboard(df, st.session_state.simulated_df, chat_on, agent)


if __name__ == "__main__":
    main()
