import pandas as pd

class AIAgent:
    def __init__(self, reference_columns):
        self.reference_columns = reference_columns

    def validate_csv_structure(self, df: pd.DataFrame) -> dict:
        missing_columns = [col for col in self.reference_columns if col not in df.columns]
        extra_columns = [col for col in df.columns if col not in self.reference_columns]
        is_valid = not missing_columns and not extra_columns
        return {
            "is_valid": is_valid,
            "missing_columns": missing_columns,
            "extra_columns": extra_columns
        }

    def generate_analysis_summary(self, df: pd.DataFrame) -> str:
        critical_issues = df[df["Threat Level"] == "Critical"]
        total_cost = df["Cost"].sum()
        avg_response_time = df["Issue Response Time Days"].mean()

        return f"""AI Summary:

- Total Issues: {len(df)}
- Critical Threats: {len(critical_issues)}
- Total Estimated Cost: ${total_cost:,.2f}
- Average Response Time: {avg_response_time:.2f} days
"""

    @staticmethod
    def summarize_attack_effects(df: pd.DataFrame) -> str:
        """
        Generate an AI-style summary of the impact of the attack simulation.
        Assumes the DataFrame contains `Threat Score`, `Threat Level`, `Cost`, and `is_anomaly`.
        """
        try:
            total_issues = len(df)
            anomaly_count = df["is_anomaly"].sum()
            avg_threat_score = df["Threat Score"].mean()
            total_cost = df["Cost"].sum()

            critical_issues = df[df["Threat Level"] == "Critical"]
            critical_count = len(critical_issues)
            high_cost_critical = critical_issues["Cost"].sum()

            summary = f"""
🛡️ **Executive Summary of Simulated Attack Effects:**

- Total records analyzed: **{total_issues}**
- Anomalies detected: **{anomaly_count}** ({anomaly_count / total_issues:.1%})
- Average threat score: **{avg_threat_score:.2f}**
- Total estimated impact cost: **${total_cost:,.2f}**

🚨 **Critical Threats:**
- Count: **{critical_count}**
- Combined cost: **${high_cost_critical:,.2f}**

💡 **Insight:**
- The system shows an increase in anomalies and critical issues post-attack simulation.
- Investigate departments with high `Threat Score` and `Cost`.
- Cross-reference `User Location` and `Activity Type` for threat origin patterns.
"""
            return summary
        except Exception as e:
            return f"⚠️ Unable to generate summary due to error: {e}"
