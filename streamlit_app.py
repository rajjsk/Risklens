import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from main import process_contract_score   # adjust if filename differs


# ---------------- Page Config ----------------
st.set_page_config(
    page_title="RiskLens - Contract Risk Analyzer",
    layout="wide"
)

st.title("📄 RiskLens – AI Contract Risk Analyzer")


# ---------------- File Upload ----------------
uploaded_file = st.file_uploader(
    "Upload Contract PDF",
    type=["pdf"]
)

if uploaded_file:
    with open("temp_contract.pdf", "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("🔍 Analyzing contract..."):
        party_1_df,party_2_df, final_risk_score, risk_level, risky_clause_table = process_contract_score(
            "temp_contract.pdf"
        )

    st.success("✅ Analysis completed!")


    # ---------------- Parties Section ----------------
    st.subheader("👥 Contract Parties")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧑 Party 1")
        if party_1_df is not None and not party_1_df.empty:
            st.dataframe(pd.DataFrame(party_1_df), use_container_width=True)
        else:
            st.warning("⚠️ Party 1 not detected")

    with col2:
        st.markdown("### 🧑 Party 2")
        if party_2_df is not None and not party_2_df.empty:
            st.dataframe(pd.DataFrame(party_2_df), use_container_width=True)
        else:
            st.warning("⚠️ Party 2 not detected")


    # ---------------- Risk Meter ----------------
    st.subheader("⚠️ Contract Risk Assessment")

    def risk_color(level):
        if level.lower() == "low":
            return "green"
        elif level.lower() == "medium":
            return "orange"
        return "red"

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=final_risk_score,
        number={"suffix": " / 10"},
        gauge={
            "axis": {"range": [1, 10]},
            "bar": {"color": risk_color(risk_level)},
            "steps": [
                {"range": [1, 3.9], "color": "lightgreen"},
                {"range": [4, 6.9], "color": "orange"},
                {"range": [7, 10], "color": "lightcoral"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": final_risk_score,
            },
        },
        title={"text": "Overall Contract Risk"}
    ))

    st.plotly_chart(gauge, use_container_width=True)

    st.markdown(
        f"### Risk Level: "
        f"<span style='color:{risk_color(risk_level)}; font-weight:bold;'>"
        f"{risk_level.upper()}</span>",
        unsafe_allow_html=True
    )


    # ---------------- Risky Clauses ----------------
    st.subheader("🚨 Risky Clauses")

    if risky_clause_table is not None and not risky_clause_table.empty:
        st.dataframe(risky_clause_table, use_container_width=True)
    else:
        st.info("✅ No risky clauses found")


else:
    st.info("📂 Please upload a contract PDF to begin analysis.")
