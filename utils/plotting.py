import plotly.express as px
import streamlit as st

def plot_threat_level_distribution(df):
    fig = px.histogram(df, x="Threat Level", color="Threat Level", title="Threat Level Distribution")
    st.plotly_chart(fig, use_container_width=True)

def plot_cost_by_department(df):
    fig = px.bar(df, x="Department Affected", y="Cost", color="Threat Level",
                 title="Cost Impact by Department", barmode="group")
    st.plotly_chart(fig, use_container_width=True)