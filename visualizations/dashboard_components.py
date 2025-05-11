#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# visualizations/dashboard_components.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def render_radar_chart(coordinated_df: pd.DataFrame):
    st.subheader("🕸️ Phase-wise Threat Profile (Radar Chart)")

    radar_metrics = ["Threat Score", "Severity", "Data Transfer MB", "Session Duration in Second"]
    phase_means = coordinated_df.groupby("Phase")[radar_metrics].mean()

    fig_radar = go.Figure()
    for phase in phase_means.index:
        fig_radar.add_trace(go.Scatterpolar(
            r=phase_means.loc[phase].values,
            theta=radar_metrics,
            fill='toself',
            name=phase.title()
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title="Average Threat Metrics by Phase"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

def render_heatmap(coordinated_df: pd.DataFrame):
    st.subheader("🔥 Threat Intensity Heatmap by Phase")

    heat_df = coordinated_df.groupby(["Phase", "Threat Level"]).size().reset_index(name="Count")
    heat_pivot = heat_df.pivot(index="Threat Level", columns="Phase", values="Count").fillna(0)

    fig_heatmap = px.imshow(
        heat_pivot,
        labels=dict(x="Phase", y="Threat Level", color="Count"),
        x=heat_pivot.columns,
        y=heat_pivot.index,
        title="Threat Level Intensity Across Phases"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

def render_comparative_dashboard(simulated_df, coordinated_df):
    st.subheader("📊 Comparative Threat Impact Dashboard")

    comparison_df = pd.concat([
        simulated_df.assign(Source="Individual"),
        coordinated_df.assign(Source="Coordinated")
    ])

    col1, col2 = st.columns(2)

    with col1:
        box_fig = px.box(
            comparison_df,
            x="Source",
            y="Threat Score",
            color="Source",
            title="Threat Score Distribution"
        )
        st.plotly_chart(box_fig, use_container_width=True)

    with col2:
        bar_fig = px.histogram(
            comparison_df,
            x="Threat Level",
            color="Source",
            barmode="group",
            title="Threat Level Frequency: Individual vs Coordinated"
        )
        st.plotly_chart(bar_fig, use_container_width=True)

