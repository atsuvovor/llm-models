def expected_columns(df_name):
      
    csv_data_columns =  [
        "Issue ID", "Issue Key", "Issue Name", "Issue Volume", "Category", "Severity", "Status", 
        "Reporters", "Assignees", "Date Reported", "Date Resolved", "Issue Response Time Days", 
        "Impact Score", "Risk Level", "Department Affected", "Remediation Steps", "Cost", "KPI/KRI", 
        "User ID", "Timestamps", "Activity Type", "User Location", "IP Location", 
        "Session Duration in Second", "Num Files Accessed", "Login Attempts", "Data Transfer MB", 
        "CPU Usage %", "Memory Usage MB", "Threat Score", "Threat Level", "Defense Action", "Color", 
        "Pred Threat", "anomaly_score", "is_anomaly"
    ]

    combined_df_columns = [
        "Issue ID", "Issue Key", "Issue Name", "Issue Volume", "Category", "Severity", "Status", 
        "Reporters", "Assignees", "Date Reported", "Date Resolved", "Issue Response Time Days", 
        "Impact Score", "Risk Level", "Department Affected", "Remediation Steps", "Cost", "KPI/KRI", 
        "User ID", "Timestamps", "Activity Type", "User Location", "IP Location", 
        "Session Duration in Second", "Num Files Accessed", "Login Attempts", "Data Transfer MB", 
        "CPU Usage %", "Memory Usage MB", "Threat Score", "Threat Level", "Defense Action", "Color", 
        "Pred Threat", "anomaly_score", "is_anomaly", "Actual Anomaly", "Attack Type", "Phase"
    ]
    
    if df_name == "csv" :
        return csv_data_columns
    else:
        return combined_df_column

