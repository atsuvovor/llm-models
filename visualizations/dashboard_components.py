# dashboard_components.py

import os
import tempfile
import smtplib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF
from email.message import EmailMessage
from plotly.subplots import make_subplots


# -------------------------------------
# Helper Functions
# -------------------------------------

def map_severity_values(df, metrics, severity_mapping):
    return df.assign(**{
        metric: df[metric].map(severity_mapping) if metric in df.columns else df[metric]
        for metric in metrics
    })

def filter_dataframe(df, departments, severities):
    if departments:
        df = df[df["Department Affected"].isin(departments)]
    if severities:
        df = df[df["Severity"].isin(severities)]
    return df
    
def create_comparison_figures(df):
    box_fig = px.box(df, x="Source", y="Threat Score", color="Source", title="Threat Score Distribution")
    bar_fig = px.histogram(df, x="Threat Level", color="Source", barmode="group",
                           title="Threat Level Frequency: Individual vs Coordinated")
    return box_fig, bar_fig

def create_radar_and_heatmap_subplots(df):
    # Radar Chart Data
    metrics = ["Threat Score", "Severity", "Data Transfer MB", "Session Duration in Second"]
    severity_map = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    mapped_df = map_severity_values(df.copy(), metrics, severity_map)
    phase_means = mapped_df.groupby("Phase")[metrics].mean()

    # Heatmap Data
    heat_df = df.groupby(["Phase", "Threat Level"]).size().reset_index(name="Count")
    heat_pivot = heat_df.pivot(index="Threat Level", columns="Phase", values="Count").fillna(0)

    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "polar"}, {"type": "heatmap"}]],
        column_widths=[0.4, 0.6],
        horizontal_spacing=0.15,
        subplot_titles=("Average Threat Metrics by Phase", "Threat Intensity Heatmap")
    )

    # Radar Chart
    for phase in phase_means.index:
        fig.add_trace(go.Scatterpolar(
            r=phase_means.loc[phase].values,
            theta=metrics,
            fill='toself',
            name=phase.title()
        ), row=1, col=1)

    # Heatmap with visible gridlines
    fig.add_trace(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns,
        y=heat_pivot.index,
        colorscale='Viridis',
        showscale=True,
        xgap=1,  # Horizontal gap between cells
        ygap=1,  # Vertical gap between cells
        colorbar=dict(title="Count", x=1.05)  # Push colorbar to the right
    ), row=1, col=2)

    # Layout and margins
    fig.update_layout(
        height=600,
        margin=dict(t=60, b=50, l=40, r=60),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    return fig




# -------------------------------------
# Report Generator & Email
# -------------------------------------

def generate_pdf_report(filtered_df, top_issues, avg_response_time, tmpdir):
    charts = ["subplot_dashboard.png"]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 22)
    pdf.cell(0, 60, '', ln=True)
    pdf.cell(200, 10, txt="SimAlgo Executive Threat Report", ln=True, align='C')
    pdf.set_font("Arial", '', 14)
    pdf.cell(200, 10, txt="Cybersecurity Simulation & Impact Summary", ln=True, align='C')
    pdf.cell(0, 20, '', ln=True)
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(200, 10, txt="Generated via SimAlgo Cyber Attack Simulator", ln=True, align='C')

    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Executive Summary Report", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Threats: {len(filtered_df)}", ln=True)
    pdf.cell(200, 10, txt=f"Average Response Time (Days): {round(avg_response_time, 2)}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Top Threats:", ln=True)
    pdf.set_font("Arial", size=10)
    for _, row in top_issues.iterrows():
        pdf.multi_cell(0, 10, txt=f"#{row['Issue ID']} - {row['Threat Level']} | {row['Severity']} | Cost: ${row['Cost (M$)']}M\nDefense: {row['Defense Action']}")

    for chart_file in charts:
        pdf.add_page()
        pdf.image(os.path.join(tmpdir, chart_file), w=180)

    pdf_path = os.path.join(tmpdir, "executive_summary_report.pdf")
    pdf.output(pdf_path)
    return pdf_path

def send_email_with_attachment(pdf_path, sender, password, recipients, subject, body, smtp_server, smtp_port):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="executive_summary_report.pdf")

    if smtp_port == 587:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)

# -------------------------------------
# Main Dashboard Functions
# -------------------------------------

def render_comparative_dashboard(simulated_df, coordinated_df):
    st.subheader("📊 Comparative Threat Impact Dashboard")
    df = pd.concat([
        simulated_df.assign(Source="Individual"),
        coordinated_df.assign(Source="Coordinated")
    ])
    col1, col2 = st.columns(2)
    box_fig, bar_fig = create_comparison_figures(df)
    with col1:
        st.plotly_chart(box_fig, use_container_width=True, key="box_fig_chart")
    with col2:
        st.plotly_chart(bar_fig, use_container_width=True, key="bar_fig")
                        
def render_threat_charts(df):
    fig = create_radar_and_heatmap_subplots(df)
    st.plotly_chart(fig, use_container_width=True)


def render_executive_summary_dashboard(df: pd.DataFrame):
    st.markdown("### 🔍 Filter Options")

    # Create columns for filters to align horizontally
    col1, col2, col3 = st.columns([3, 3, 2])

    departments = df["Department Affected"].dropna().unique().tolist()
    severities = df["Severity"].dropna().unique().tolist()

    with col1:
        selected_dept = st.multiselect("Filter by Department", options=departments, default=departments)

    with col2:
        selected_sev = st.multiselect("Filter by Severity", options=severities, default=severities)

    with col3:
        top_n = st.slider("Top N Threats", min_value=3, max_value=20, value=5)

    # Filter the dataframe
    filtered_df = filter_dataframe(df.copy(), selected_dept, selected_sev)

    # Calculate metrics
    total_threats = filtered_df.groupby("Threat Level").size()
    severity_stats = filtered_df.groupby("Severity").size()
    impact_cost_stats = filtered_df.groupby("Severity")["Cost"].sum().div(1_000_000)
    resolved_stats = filtered_df[filtered_df["Status"].isin(["Resolved", "Closed"])].groupby("Threat Level").size()
    outstanding_stats = filtered_df[filtered_df["Status"].isin(["Open", "In Progress"])].groupby("Threat Level").size()

    # Create 2x2 subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "xy"}, {"type": "domain"}],
               [{"type": "xy"}, {"type": "xy"}]],
        subplot_titles=(
            "Total Threats by Level", "Threat Severity Distribution",
            "Estimated Cost Impact by Severity", "Issue Resolution Status by Threat Level"
        )
    )

    fig.add_trace(go.Bar(
        x=total_threats.index, y=total_threats.values, marker_color="blue", name="Threat Count"
    ), row=1, col=1)

    fig.add_trace(go.Pie(
        labels=severity_stats.index, values=severity_stats.values, hole=0.4,
        name="Severity"
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        x=impact_cost_stats.index, y=impact_cost_stats.values, marker_color="orange", name="Cost"
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=resolved_stats.index, y=resolved_stats.values, name="Resolved", marker_color="green"
    ), row=2, col=2)

    fig.add_trace(go.Bar(
        x=outstanding_stats.index, y=outstanding_stats.values, name="Outstanding", marker_color="red"
    ), row=2, col=2)

    fig.update_layout(height=800, showlegend=True, barmode='stack')
    st.plotly_chart(fig, use_container_width=True)

    # Top N Issues
    top_issues = filtered_df.nlargest(top_n, "Threat Score")[[
        "Issue ID", "Threat Level", "Severity", "Issue Response Time Days", "Department Affected", "Cost", "Defense Action"
    ]].copy()
    top_issues["Cost (M$)"] = top_issues["Cost"].div(1_000_000).round(2)
    st.markdown(f"### 🏆 Top {top_n} Issues by Threat Score")
    st.dataframe(top_issues.drop(columns="Cost"))

    # Avg Response Time
    avg_response_time = filtered_df["Issue Response Time Days"].mean()
    st.markdown("### ⏱️ Average Response Time Summary")
    st.table(pd.DataFrame({
        "Metric": ["Avg Days", "Hours", "Minutes"],
        "Value": [round(avg_response_time, 2), round(avg_response_time * 24, 2), round(avg_response_time * 1440, 2)]
    }))

    # --- PDF + EMAIL ---
    with tempfile.TemporaryDirectory() as tmpdir:
        fig.write_image(os.path.join(tmpdir, "subplot_dashboard.png"))

        pdf_path = generate_pdf_report(filtered_df, top_issues, avg_response_time, tmpdir)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="executive_summary_report.pdf")

        with st.expander("📧 Email Executive Report"):
            email_cfg = st.secrets.get("email", {})
            sender = st.text_input("Sender Email", value=email_cfg.get("sender", ""))
            password = st.text_input("Email Password", type="password", value=email_cfg.get("password", ""))
            provider = st.selectbox("SMTP Provider", ["Gmail", "Outlook", "Yahoo", "Custom"],
                                    index=["Gmail", "Outlook", "Yahoo", "Custom"].index(email_cfg.get("smtp_provider", "Gmail").title()))
            smtp_server = st.text_input("Custom SMTP Server") if provider == "Custom" else {
                "Gmail": "smtp.gmail.com",
                "Outlook": "smtp.office365.com",
                "Yahoo": "smtp.mail.yahoo.com"
            }.get(provider, "smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=465 if provider != "Outlook" else 587)
            recipients = st.text_input("Recipients (comma-separated)").split(",")
            subject = st.text_input("Subject", "SimAlgo Cybersecurity Executive Summary")
            body = st.text_area("Email Body", "Please find attached the latest executive summary report.")

            if st.button("Send Email"):
                try:
                    send_email_with_attachment(pdf_path, sender, password, recipients, subject, body, smtp_server, int(smtp_port))
                    st.success("✅ Email sent successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to send email: {e}")

    return filtered_df
