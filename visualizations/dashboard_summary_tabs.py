# --- Imports ---
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots

# --- Data Loading ---
def load_data(filepath):
    df = pd.read_csv(filepath)
    df["Cost (M$)"] = df["Cost"] / 1_000_000
    return df

# --- Utilities ---
def get_dropdown_options(df):
    departments = sorted(df["Department Affected"].dropna().unique())
    return [{'label': 'All', 'value': 'All'}] + [{'label': dept, 'value': dept} for dept in departments]

def get_top_n_options(df, max_n=20):
    return [{'label': f'Top {i}', 'value': i} for i in range(1, min(len(df), max_n) + 1)]

# --- Data Extraction ---
def extract_core_metrics(df):
    return {
        "Total Issues": len(df),
        "Critical Issues": len(df[df["Severity"] == "Critical"]),
        "Resolved Issues": len(df[df["Status"].isin(["Resolved", "Closed"])]),
        "Unresolved Issues": len(df[df["Status"].isin(["Open", "In Progress"])]),
    }

def extract_attack_counts(df):
    return {
        "Phishing Attacks": len(df[df["Login Attempts"] > 10]),
        "Malware Attacks": len(df[df["Num Files Accessed"] > 50]),
        "DDOS Attacks": len(df[(df["Session Duration in Second"] > 7200) & (df["Data Transfer MB"] > 1000)]),
        "Data Leak Attacks": len(df[df["Data Transfer MB"] > 500]),
        "Insider Threats": len(df[df["Access Restricted Files"] == True]),
        "Ransomware Attacks": len(df[df["CPU Usage %"] > 70]),
    }

def get_attack_data_dict(df):
    return {
        "Phishing": df[df["Login Attempts"] > 10],
        "Malware": df[df["Num Files Accessed"] > 50],
        "DDOS": df[(df["Session Duration in Second"] > 7200) & (df["Data Transfer MB"] > 1000)],
        "Data Leak": df[df["Data Transfer MB"] > 500],
        "Insider Threats": df[df["Access Restricted Files"] == True],
        "Ransomware Attacks": df[df["CPU Usage %"] > 70],
    }

# --- Summary Builders ---
def build_summary_dict(df):
    return {
        "Total Attack": df.groupby("Threat Level").size(),
        "Attack Volume Severity": df.groupby("Severity").size(),
        "Impact in Cost(M$)": round(df.groupby("Severity")["Cost"].sum() / 1_000_000),
        "Resolved Issues": df[df["Status"].isin(["Resolved", "Closed"])].groupby("Threat Level").size(),
        "Outstanding Issues": df[df["Status"].isin(["Open", "In Progress"])].groupby("Threat Level").size(),
        "Avg Response Time(Outstanding Issues)": round(
            df[df["Status"].isin(["Open", "In Progress"])]
            .groupby("Threat Level")["Issue Response Time Days"].mean()),
        "Solved Issues Avg Response Time": round(
            df[df["Status"].isin(["Resolved", "Closed"])]
            .groupby("Threat Level")["Issue Response Time Days"].mean()),
    }

# --- Chart Builders ---
def build_bar_chart(summary_dic):
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
    bar_fig = make_subplots(rows=3, cols=3, subplot_titles=list(summary_dic.keys()))
    row, col = 1, 1
    for i, (title, data) in enumerate(summary_dic.items()):
        if data.empty: continue
        sorted_data = data.sort_values()
        bar_fig.add_trace(
            go.Bar(
                x=sorted_data.values, y=sorted_data.index.astype(str),
                orientation='h', text=sorted_data.values, textposition='auto',
                marker_color=colors[i % len(colors)]
            ), row=row, col=col)
        col += 1
        if col > 3: row += 1; col = 1
    bar_fig.update_layout(height=700, title_text="Executive Metrics (Bar Charts)", showlegend=False)
    bar_fig.update_xaxes(showgrid=False)
    bar_fig.update_yaxes(showgrid=False)
    bar_fig.update_xaxes(showticklabels=False)
    bar_fig.update_yaxes(
        showline=False,       
        ticks="",             
        showticklabels=True,  
    )
    
    return bar_fig

def build_donut_chart(summary_dic):
    donut_fig = make_subplots(rows=3, cols=3, specs=[[{'type': 'domain'}] * 3] * 3,
                              subplot_titles=list(summary_dic.keys()))
    row, col = 1, 1
    color_map = {"Critical": "darkred", "High": "red", "Medium": "orange", "Low": "green"}
    for i, (title, data) in enumerate(summary_dic.items()):
        if data.empty: continue
        labels = data.index.astype(str)
        values = data.values
        colors_donut = [color_map.get(label, 'lightgray') for label in labels]
        pull = [0.03] * len(labels) # slight pull for all slices
        donut_fig.add_trace(
            go.Pie(labels=labels, values=values, hole=0.4,
                   marker=dict(colors=colors_donut),
                   #textinfo='label+percent+value',
                   textinfo='none',
                   textposition='outside',
                   texttemplate=["<br>%{label}<br>%{percent} (%{value})"] * len(labels),
                   pull=pull,
                   insidetextfont=dict(size=10),
                    outsidetextfont=dict(size=10),),
            row=row, col=col)
        col += 1
        if col > 3: row += 1; col = 1
    donut_fig.update_layout(height=1000, title_text="Executive Metrics (Donut Charts)", showlegend=False,
                            margin=dict(t=100, l=20, r=20, b=20),)
    return donut_fig

def create_summary_bar(df, title, y_col, color_list, label):
    df_sorted = df.sort_values(by=y_col, ascending=False)
    fig = px.bar(df_sorted, x=df_sorted.index, y=y_col, title=title, labels={"index": label})
    fig.update_traces(marker_color=color_list)
    fig.update_layout(xaxis_title=label,
                      yaxis_title=y_col,
                      bargap=0.2,
                      height=400,
                      showlegend=False,
                       
                      xaxis=dict(
                      #tickangle=45,  # Rotate x-axis labels by 45 degrees for better readability
                      automargin=True # Automatically adjust margin for x-axis labels if needed
                      ),
                      yaxis=dict(
                      automargin=True # Automatically adjust margin for y-axis labels if needed
                      ),
                      margin=dict(
                      b=150,  # Increase bottom margin to create more space for x-axis labels and title
                      l=100   # Increase left margin to ensure y-axis labels don't get cut off
        ),
        xaxis_title_standoff=20, # Increase space between x-axis title and labels
        yaxis_title_standoff=20  # Increase space between y-axis title and labels
        
    )

    return fig

def create_bar_plot(df, title, x_col="Department Affected", y_col="Cost", top_n=None, bar_colors=None):
    if df.empty:
        return px.bar(title=f"{title}: No Data Available")
    df = df.sort_values(by=y_col, ascending=False)
    if top_n:
        df = df.head(top_n)
    if bar_colors:
        colors_to_use = [bar_colors] if isinstance(bar_colors, str) else bar_colors
        fig = px.bar(df, x=x_col, y=y_col, title=title, color_discrete_sequence=colors_to_use)
    else:
        fig = px.bar(df, x=x_col, y=y_col, color=x_col, title=title)
    fig.update_layout(bargap=0.2, 
                      height=400, 
                      showlegend=False,
                      xaxis=dict(
                      #tickangle=45,  
                      automargin=True 
                      ),
                      yaxis=dict(
                      automargin=True 
                      ),
                      margin=dict(
                      b=150,  
                      l=100   
        ),
        xaxis_title_standoff=20, 
        yaxis_title_standoff=20  
        
    )

    return fig

#--------tables-----------------------------

def get_department_filtered_df(df, selected_dept):
    if selected_dept != "All":
        return df[df["Department Affected"] == selected_dept]
    return df

def get_top_n_issues(df, top_n):
    return df.nlargest(top_n, "Threat Score")

def get_summary_statistics(df):
    summary_dict = build_summary_dict(df)
    return pd.DataFrame(summary_dict).apply(lambda x: round(x) if x.dtype.kind in 'biufc' else x)

def get_average_response_time(df):
    avg_days = round(df["Issue Response Time Days"].fillna(0).mean())
    return pd.DataFrame([{
        "Average Response Time (Days)": avg_days,
        "Average Response Time (Hours)": avg_days * 24,
        "Average Response Time (Minutes)": avg_days * 1440
    }])


def extract_issues_top_tables(df, top_n):
    # round df column "Issue Response Time Days" value to zero decimal
    df["Issue Response Time Days"] = df["Issue Response Time Days"].round(0)
    top_base_df_ = get_top_n_issues(df, top_n)
    top_base_df = top_base_df_[[
        "Issue ID", "Threat Level", "Severity", "Issue Response Time Days",
        "Department Affected", "Cost", "Defense Action", "Status"
    ]].copy()

    top_critical_df = top_base_df[top_base_df["Severity"] == "Critical"]
    top_resolved_df = top_base_df[top_base_df["Status"].isin(["Resolved", "Closed"])]
    top_outstanding_df = top_base_df[top_base_df["Status"].isin(["In Progress", "Open"])]

    return top_base_df, top_critical_df, top_resolved_df, top_outstanding_df

def create_table(df, title):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns), fill_color='lightblue', align='left'),
        cells=dict(values=[df[col] for col in df.columns], fill_color='white', align='left')
    )])
    fig.update_layout(title=title, title_x=0.5)
    return fig

#-----------------------------------------
# --- App Layout Builder ---
#--------------------------------------------
def build_layout(df, metrics_df, attacks_df, attack_data_dict):
    return html.Div([
        html.H1("Cyber Attacks  Executive Dashboard", style={"textAlign": "center"}),
        dcc.Tabs([
            dcc.Tab(label='Metrics Charts', children=[
                html.Div([
                    html.Div([
                        html.Label("Department Filter"),
                        dcc.Dropdown(id='exec-dept', options=get_dropdown_options(df), value='All')
                    ], style={"width": "48%", "display": "inline-block"}),

                    html.Div([
                        html.Label("Top N Issues"),
                        dcc.Dropdown(id='exec-top-n', options=get_top_n_options(df), value=5)
                    ], style={"width": "48%", "display": "inline-block", "float": "right"}),

                    dcc.Graph(id="bar-chart"),
                    dcc.Graph(id="donut-chart")
                ])
            ]),
            dcc.Tab(label='Attack Summary', children=[
                html.Div([
                    html.Div([
                        html.Label("Attack Type"),
                        dcc.Dropdown(
                            id="attack-type",
                            options=[{"label": "All", "value": "All"}] + [{"label": k, "value": k} for k in attack_data_dict],
                            value="All"
                        )
                    ], style={"width": "30%", "display": "inline-block", "marginRight": "5%"}),

                    html.Div([
                        html.Label("Department"),
                        dcc.Dropdown(
                            id="attack-dept",
                            options=[{"label": "All", "value": "All"}] + [{"label": d, "value": d} for d in sorted(df["Department Affected"].dropna().unique())],
                            value="All"
                        )
                    ], style={"width": "30%", "display": "inline-block", "marginRight": "5%"}),

                    html.Div([
                        html.Label("Top N Issues"),
                        dcc.Dropdown(id="attack-top-n", options=get_top_n_options(df), value=5)
                    ], style={"width": "28%", "display": "inline-block", "float": "right"}),

                    html.Div([
                        html.Div([dcc.Graph(id="attack-cost")], style={"width": "50%", "padding": "0 10px", "display": "inline-block"}),
                        html.Div([dcc.Graph(id="incident-summary")], style={"width": "50%", "padding": "0 10px", "display": "inline-block"}),
                        html.Div([dcc.Graph(id="attack-scenarios")], style={"width": "50%", "padding": "0 10px", "display": "inline-block"}),
                    ], style={"display": "flex", "flexDirection": "row", "justifyContent": "space-between"})
                ])
            ]),
            #----tables----
            dcc.Tab(label='Tables', children=[
                html.Div([
                    html.Label("Select Department Affected:"),
                    dcc.Dropdown(
                        id='department-dropdown',
                        options=get_dropdown_options(df),
                        value='All',
                        clearable=False
                    ),
                ], style={'width': '48%', 'display': 'inline-block'}),

                html.Div([
                    html.Label("Select Top N Issues by Cost:"),
                    dcc.Dropdown(
                        id='top-n-dropdown',
                        options=get_top_n_options(df),
                        value=5,
                        clearable=False
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),

                #html.Br(), html.Br(),
                #---from here dcc instesd of dbc
               html.Div([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='summary-table'), width=12),
                    ])
                ], style={'width': '100%', 'display': 'inline-block'}),

                 html.Div([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='average-response-table'), width=12)
                    ])
                ]),

                
                
                html.Div([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='top-issues-table'), width=12)
                    ])
                ]),

            html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='top-critical-issues-table'), width=12)
                ])
            ]),

            html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='resolved-issues-table'), width=12)
                ])
            ]),

            html.Div([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='outstanding-issues-table'), width=12)
                    ])
                ])

            #---------
            ])
        ])
    ])
# --- Callback Registration ---
def register_callbacks(app, df, attack_data_dict):
    @app.callback(
        Output("bar-chart", "figure"),
        Output("donut-chart", "figure"),
        Input("exec-dept", "value"),
        Input("exec-top-n", "value")
    )
    def update_exec_charts(dept, top_n):
        dff = df.copy()
        if dept != "All":
            dff = dff[dff["Department Affected"] == dept]
        dff = dff.nlargest(top_n, "Threat Score")
        summary = build_summary_dict(dff)
        return build_bar_chart(summary), build_donut_chart(summary)

    @app.callback(
        Output("attack-cost", "figure"),
        Output("incident-summary", "figure"),
        Output("attack-scenarios", "figure"),
        Input("attack-type", "value"),
        Input("attack-dept", "value"),
        Input("attack-top-n", "value")
    )
    def update_attack_charts(atype, dept, top_n, bar_colors='#FF5733'):
        if atype == "All":
            dff = pd.concat(attack_data_dict.values(), ignore_index=True)
        else:
            dff = attack_data_dict.get(atype, pd.DataFrame()).copy()

        if dept != "All":
            dff = dff[dff["Department Affected"] == dept]

        # Dynamically determine bar_colors based on attack type or a default
        if atype == "Phishing":
            bar_colors = '#FF5733'
        elif atype == "Malware":
            bar_colors = '#33FF57'
        elif atype == "DDOS":
            bar_colors = '#3357FF'
        elif atype == "Data Leak":
            bar_colors = '#FF33A1'
        elif atype == "Insider Threats":
            bar_colors = '#A133FF'
        elif atype == "Ransomware Attacks":
            bar_colors = '#FFFF33'
        else: # Default for "All" or other types
            bar_colors = '#5733FF'


        # Rebuild incident and attack scenarios summaries based on the filtered dff
        incident_summary_df_filtered = pd.DataFrame(extract_core_metrics(dff), index=["Value"]).T
        attack_scenarios_df_filtered = pd.DataFrame(extract_attack_counts(dff), index=["Value"]).T.dropna()

        return ( create_bar_plot(dff, f"{atype} - Department vs Cost", top_n=top_n, bar_colors=bar_colors),
                 create_summary_bar(incident_summary_df_filtered, "Incident Summary", "Value", ['#636EFA']*len(incident_summary_df_filtered), "Metric"), # Adjust colors based on filtered data size
                 create_summary_bar(attack_scenarios_df_filtered, "Attack Scenarios", "Value", ['#FFA15A']*len(attack_scenarios_df_filtered), "Scenario") # Adjust colors based on filtered data size
        )


    #----table------
    @app.callback(
        Output('summary-table', 'figure'),
        Output('average-response-table', 'figure'),
        Output('top-issues-table', 'figure'),
        Output('top-critical-issues-table', 'figure'),
        Output('resolved-issues-table', 'figure'),
        Output('outstanding-issues-table', 'figure'),
        Input('department-dropdown', 'value'),
        Input('top-n-dropdown', 'value')
    )
    def update_tables(selected_dept, top_n):
        dept_df = get_department_filtered_df(df, selected_dept)
        top_n_df = get_top_n_issues(dept_df, top_n)

        summary_df = get_summary_statistics(dept_df)
        avg_time_df = get_average_response_time(dept_df)

        top_issues_df, top_critical_df, top_resolved_df, top_outstanding_df = extract_issues_top_tables(dept_df, top_n)

        return (
            create_table(summary_df.reset_index(), f"Executive Summary  (Dept: {selected_dept})"),
            create_table(avg_time_df, "Average Response Time (All Units)"),
            create_table(top_issues_df, f"Top {top_n} Issues with Adaptive Defense (Dept: {selected_dept}"),
            create_table(top_critical_df, f"Top {top_n} Critical Issues (Dept: {selected_dept})"),
            create_table(top_resolved_df, f"Top {top_n} Resolved Issues (Dept: {selected_dept})"),
            create_table(top_outstanding_df, f"Top {top_n} Outstanding Issues (Dept: {selected_dept})")
        )

# --- Launcher ---
def launch_attacks_charts_dashboard(df):
    #file_path = "/content/drive/My Drive/Cybersecurity Data/combined_normal_and_simulated_attacks_class_df.csv"
    #df = load_data(file_path)
    attack_data_dict = get_attack_data_dict(df)

    metrics_df = pd.DataFrame.from_dict(extract_core_metrics(df), orient='index', columns=['Value'])
    attacks_df = pd.DataFrame.from_dict(extract_attack_counts(df), orient='index', columns=['Value'])

    #app = Dash(__name__)
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = "Cyber Attack Summary Dashboard"
    app.layout = build_layout(df, metrics_df, attacks_df, attack_data_dict)
    register_callbacks(app, df, attack_data_dict)

    #app.run(debug=True, port=8051)
    
    return app

 