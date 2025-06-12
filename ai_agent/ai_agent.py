# ai_agent/ai_agent.py
import os
import sys
import io
import streamlit as st
import pandas as pd
from typing import List, Optional
from langchain_core.documents import Document
from ai_agent.config import Settings
from ai_agent.rag_utils import prepare_rag_documents
from models.llm_loader import load_llm

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA

@st.cache_resource(show_spinner="Loading language model...")
def load_cached_llm():
    return load_llm()


class AIAgent:
    def __init__(
        self,
        reference_columns: List[str] = None,
        df: pd.DataFrame = None,
        historical_df: pd.DataFrame = None,
        use_rag: bool = True,
        group_by: str = "Department"
    ):
        self.reference_columns = reference_columns or []
        self.df = df
        self.history = st.session_state.get("chat_history", [])
        self.llm = load_cached_llm()
        self.rag_chain = None

        self.rag_docs = prepare_rag_documents(
            simulated_df=self.df,
            historical_df=historical_df if historical_df is not None else pd.DataFrame(),
            group_by=group_by,
            chunk_size=10
        )

        if use_rag and self.rag_docs and FAISS:
            self._setup_rag_chain(self.rag_docs)

    def _setup_rag_chain(self, docs: List[str]):
        documents = [Document(page_content=doc) for doc in docs]
        embedder = (
            OpenAIEmbeddings() if Settings.llm_backend == "openai"
            else HuggingFaceEmbeddings(model_name=Settings.embedding_model)
        )
        vectorstore = FAISS.from_documents(documents, embedder)
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=vectorstore.as_retriever(),
            return_source_documents=False,
        )

    def _run_llm(self, prompt: str) -> str:
        try:
            if hasattr(self.llm, "predict"):
                response = self.llm.predict(prompt)
            else:
                response = self.llm(prompt)

            entry = [{"role": "user", "content": prompt},
                     {"role": "assistant", "content": response.strip()}]
            self.history.extend(entry)
            st.session_state["chat_history"] = self.history
            return response.strip()

        except Exception as e:
            return f"⚠️LLM generation failed: {e}"

    def print_df_info(self, historical_df):
        st.markdown("**📝 CSV Data Frame Structure**")
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        historical_df.info()
        sys.stdout = old_stdout
        st.code(captured_output.getvalue(), language='text')

        st.markdown("**📊 Summary Statistics**")
        st.dataframe(historical_df.describe().transpose())
        st.markdown("**🔍 Data Preview (df.head())**")
        st.dataframe(historical_df.head())

    def validate_csv_structure(self, historical_df: pd.DataFrame) -> dict:
        missing_columns = [col for col in self.reference_columns if col not in historical_df.columns]
        extra_columns = [col for col in historical_df.columns if col not in self.reference_columns]
        is_valid = not missing_columns and not extra_columns

        return {
            "is_valid": is_valid,
            "missing_columns": missing_columns,
            "extra_columns": extra_columns
        }

    def generate_analysis_summary(self, df: pd.DataFrame) -> str:
        try:
            critical_issues = df[df["Threat Level"] == "Critical"]
            total_cost = df["Cost"].sum()
            avg_response_time = df["Issue Response Time Days"].mean()
            defense_counts = df["Defense Action"].dropna().value_counts().to_dict()

            prompt = f"""
Given:
- {len(df)} total issues
- {len(critical_issues)} critical threats
- ${total_cost:,.2f} total cost
- {avg_response_time:.2f} days avg response time
- Defense actions: {defense_counts}
Generate SOC/Executive-level insights and recommendations.
"""

            base_summary = f"""**AI Summary:**
- Total Issues: **{len(df)}**
- Critical Threats: **{len(critical_issues)}**
- Total Cost: **${total_cost:,.2f}**
- Avg Response Time: **{avg_response_time:.2f} days**
- Common Defenses: {defense_counts}
"""
            return base_summary + "\n**LLM Insight:**\n" + self._run_llm(prompt)
        except Exception as e:
            return f"\u26a0\ufe0f Failed to generate summary: {e}"

    def summarize_attack_effects(self, df: pd.DataFrame) -> str:
        try:
            total_issues = len(df)
            anomaly_count = df["is_anomaly"].sum()
            avg_threat_score = df["Threat Score"].mean()
            total_cost = df["Cost"].sum()
            critical_issues = df[df["Threat Level"] == "Critical"]
            critical_count = len(critical_issues)
            high_cost_critical = critical_issues["Cost"].sum()
            defense_counts = df["Defense Action"].dropna().value_counts().to_dict()

            base_summary = f"""
🛡️ **Executive Summary of Simulated Attack Effects:**

- Total records analyzed: **{total_issues}**
- Anomalies detected: **{anomaly_count}** ({anomaly_count / total_issues:.1%})
- Avg threat score: **{avg_threat_score:.2f}**
- Total impact cost: **${total_cost:,.2f}**

🚨 **Critical Threats:**
- Count: **{critical_count}**
- Combined cost: **${high_cost_critical:,.2f}**

🛡️ **Defense Actions Taken:**
- {defense_counts}
"""

            rag_insight = ""
            if self.rag_chain:
                query = f"Given {critical_count} critical threats and ${high_cost_critical:,.2f} cost, with defenses {defense_counts}, provide SOC guidance."
                rag_result = self.rag_chain.run(query)
                rag_insight = f"\n📚 **Augmented Insight (RAG):**\n{rag_result.strip()}"

            llm_prompt = (
                f"Given {critical_count} critical threats, ${high_cost_critical:,.2f} damages, "
                f"and defenses: {defense_counts}, summarize effects and recommend strategy."
            )
            llm_response = self._run_llm(llm_prompt)
            return base_summary + f"\n💡 **LLM Insight:**\n{llm_response}" + rag_insight

        except Exception as e:
            return f"⚠️ Failed to generate attack summary: {e}"


