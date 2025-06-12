# ai_agent/rag_utils.py

import pandas as pd
from typing import List


def align_columns(historical_df: pd.DataFrame, simulated_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds any columns present in simulated_df but missing in historical_df.
    Fills missing columns with None or default values.
    """
    for col in simulated_df.columns:
        if col not in historical_df.columns:
            historical_df[col] = None
    return historical_df


def combine_dataframes(simulated_df: pd.DataFrame, historical_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combines simulated and historical data after aligning schema.
    """
    historical_df = align_columns(historical_df, simulated_df)
    combined_df = pd.concat([historical_df, simulated_df], ignore_index=True)
    return combined_df.drop_duplicates().reset_index(drop=True)


def create_flat_rag_docs(df: pd.DataFrame, chunk_size: int = 10) -> List[str]:
    """
    Converts rows of a DataFrame into RAG-ready plain-text documents in fixed-size chunks,
    applying appropriate formatting by column type.
    """
    cost_cols = ["Cost"]
    date_cols = ["Date Reported", "Date Resolved", "Timestamps"]
    numeric_cols = [
        "Session Duration in Second", "Num Files Accessed", "Login Attempts",
        "Data Transfer MB", "Memory Usage MB", "Threat Score"
    ]
    percent_cols = ["CPU Usage %"]
    defense_col = "Defense Action"
    dept_col = "Department Affected"

    all_columns = expected_columns()

    rag_docs = []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]

        text_chunk = "\n".join([
            ", ".join([
                (
                    f"{col}: ${row.get(col, 0):,.2f}" if col in cost_cols else
                    f"{col}: {row.get(col, 0)}" if col in numeric_cols else
                    f"{col}: {row.get(col, 'N/A')}" if col in date_cols else
                    f"{col}: {row.get(col, 'General')}" if col == defense_col else
                    f"{col}: {row.get(col, 'None')}" if col == dept_col else
                    f"{col}: {row.get(col, 'N/A')}"
                )
                for col in all_columns if col in row
            ])
            for _, row in chunk.iterrows()
        ])
        rag_docs.append(text_chunk)

    return rag_docs

def create_grouped_rag_docs(df: pd.DataFrame, group_by: str = "Department Affected", top_k: int = 3) -> List[str]:
    """
    Summarizes threats, cost, defense actions, and all numerical/categorical/date/percentage columns per group.
    Supports group_by = "Department Affected", "Attack Type", "Phase", etc.
    """
    numerical_columns = [
        "Session Duration in Second", "Num Files Accessed", "Login Attempts",
        "Data Transfer MB", "Memory Usage MB", "Threat Score"
    ]
    percentage_columns = ["CPU Usage %"]
    cost_column = "Cost"
    date_columns = ["Date Reported", "Date Resolved", "Timestamps"]
    categorical_columns = [
        "Severity", "Category", "Status", "KPI/KRI", "Activity Type",
        "Threat Level", "Attack Type", "Phase"
    ]

    if group_by not in df.columns:
        group_by = "Department Affected"

    rag_docs = []
    grouped = df.groupby(group_by)

    for group_name, group_df in grouped:
        doc = [f"{group_by}: {group_name}"]
        doc.append(f"- Total Issues: {len(group_df)}")

        # Critical issues
        critical_issues = group_df[group_df["Threat Level"] == "Critical"]
        doc.append(f"- Critical Issues: {len(critical_issues)}")

        # Cost stats
        total_cost = group_df[cost_column].sum()
        avg_cost = group_df[cost_column].mean()
        min_cost = group_df[cost_column].min()
        max_cost = group_df[cost_column].max()
        doc.append(f"- Total Cost: ${total_cost:,.2f}")
        doc.append(f"- Cost (Avg): ${avg_cost:,.2f}, Min: ${min_cost:,.2f}, Max: ${max_cost:,.2f}")

        # Defense Actions
        defense_counts = group_df["Defense Action"].dropna().value_counts().to_dict()
        doc.append(f"- Defense Actions: {defense_counts}")

        # Numerical summaries
        for col in numerical_columns:
            if col in group_df.columns:
                total = group_df[col].sum()
                avg = group_df[col].mean()
                min_val = group_df[col].min()
                max_val = group_df[col].max()
                doc.append(f"- {col}: Total={total:.2f}, Avg={avg:.2f}, Min={min_val:.2f}, Max={max_val:.2f}")

        # Percentage columns
        for col in percentage_columns:
            if col in group_df.columns:
                avg = group_df[col].mean()
                max_val = group_df[col].max()
                doc.append(f"- {col}: Avg={avg:.2f}%, Max={max_val:.2f}%")

        # Date columns
        for col in date_columns:
            if col in group_df.columns:
                try:
                    earliest = group_df[col].min()
                    latest = group_df[col].max()
                    doc.append(f"- {col}: Earliest={earliest}, Latest={latest}")
                except Exception:
                    pass  # in case of parse errors

        # Categorical distributions
        for col in categorical_columns:
            if col in group_df.columns:
                counts = group_df[col].value_counts().nlargest(top_k).to_dict()
                doc.append(f"- {col} Top-{top_k}: {counts}")

        rag_docs.append("\n".join(doc))

    return rag_docs



def prepare_rag_documents(
    simulated_df: pd.DataFrame,
    historical_df: pd.DataFrame,
    group_by: str = None,
    chunk_size: int = 10
) -> List[str]:
    combined_df = combine_dataframes(simulated_df, historical_df)

    if group_by:
        return create_grouped_rag_docs(combined_df, group_by=group_by)
    else:
        return create_flat_rag_docs(combined_df, chunk_size=chunk_size)
