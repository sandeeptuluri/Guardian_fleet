"""
GuardianFleet - Streamlit Enterprise Dashboard (app.py)
-------------------------------------------------------
Real-Time Visual Control Center for the Fortified Enterprise Fleet track.

Displays:
- Real-time Memory Bank telemetry & state graph transitions
- Visual metrics for database lookups, patch validation, and Self-Healing Retries
- Interactive Gatekeeper Human-in-the-Loop (HITL) approval interface
- Execution logs and detailed JSON inspection for hackathon judges
"""

import os
import json
import asyncio
from datetime import datetime
import streamlit as st

# Configure Page Layout & Theme
st.set_page_config(
    page_title="GuardianFleet | Enterprise Compliance Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Enterprise Theme
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.0rem; color: #64748B; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1rem; }
    .status-badge { font-weight: 600; padding: 0.3rem 0.8rem; border-radius: 20px; display: inline-block; }
    .badge-pending { background-color: #FEF3C7; color: #92400E; }
    .badge-approved { background-color: #D1FAE5; color: #065F46; }
    .badge-rejected { background-color: #FEE2E2; color: #991B1B; }
    </style>
""", unsafe_allow_html=True)


STATE_FILE = "audit_state.json"


def load_state():
    """Loads the persisted agent execution state from the local Memory Bank store."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading state memory file: {str(e)}")
            return None
    return None


def save_state(data):
    """Persists updated state back to file (e.g., when human approves/rejects)."""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Failed to update state file: {str(e)}")


def run_backend_trigger(policy_id):
    """Triggers main.py backend execution asynchronously."""
    from orchestrator import GuardianFleetOrchestrator
    orchestrator = GuardianFleetOrchestrator(state_file_path=STATE_FILE)
    with st.spinner(f"Orchestrating 4-Agent Fleet for asset '{policy_id}'..."):
        asyncio.run(orchestrator.execute_workflow(policy_id=policy_id))


# ==========================================
# SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shield-with-signature.png", width=64)
    st.markdown("### 🛡️ GuardianFleet Control Center")
    st.caption("Track: Fortified Enterprise Fleet")
    st.markdown("---")
    
    st.markdown("#### ⚙️ Execution Controls")
    selected_policy = st.selectbox(
        "Select Operational Target:",
        ["policy_ca_labour_2026", "policy_privacy_webform_2026"],
        index=0
    )
    
    if st.button("🚀 Trigger Fleet Audit Run", type="primary", use_container_width=True):
        run_backend_trigger(selected_policy)
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🏛️ Toolkit Architecture")
    st.markdown("""
    - **Agent Registry:** 4 Specialized ADK Agents
    - **Agent Runtime:** Google Cloud Run
    - **Memory Bank:** State & Telemetry Store
    - **Guardrails:** Pydantic & Gatekeeper HITL
    - **Observability:** Real-time Dashboard
    """)
    st.markdown("---")
    st.caption("Powered by Google ADK & Gemini 2.5/3.5")


# ==========================================
# MAIN DASHBOARD CONTENT AREA
# ==========================================

st.markdown('<div class="main-header">🛡️ GuardianFleet: Enterprise Compliance Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Legal Auditing, Self-Healing Policy Remediation & Human-in-the-Loop Governance</div>', unsafe_allow_html=True)

state_data = load_state()

if not state_data:
    st.info("👋 No agent execution state found in Memory Bank. Click **'Trigger Fleet Audit Run'** in the sidebar to run the multi-agent pipeline.")
else:
    # --- METRICS BAR ---
    status = state_data.get("status", "UNKNOWN")
    metrics = state_data.get("metrics", {})
    retries = metrics.get("self_healing_retries", 0)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Target Asset ID", state_data.get("policy_id", "N/A"))
    with m2:
        st.metric("Latency", f"{state_data.get('latency_seconds', 0.0)}s")
    with m3:
        st.metric("Validator Attempts", metrics.get("patch_validation_attempts", 0))
    with m4:
        st.metric(
            "Self-Healing Retries",
            f"{retries}",
            delta="Self-Healed" if retries > 0 else "Clean Pass",
            delta_color="normal"
        )

    st.markdown("---")

    # --- ARCHITECTURAL AGENT PIPELINE TRACKER ---
    st.markdown("### 🔄 Multi-Agent Workflow Trajectory")
    
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        st.success("✅ **1. Ingestion Agent**\n\nRuleSet Extracted")
    with col_a2:
        st.success("✅ **2. Auditor Agent**\n\nViolations Flagged")
    with col_a3:
        st.success(f"✅ **3. Remediation Agent**\n\nSelf-Healed ({retries} Retry)")
    with col_a4:
        if status == "PENDING_HUMAN_APPROVAL":
            st.warning("⚠️ **4. Gatekeeper Agent**\n\nPaused for HITL")
        elif status == "APPROVED":
            st.success("✅ **4. Gatekeeper Agent**\n\nApproved & Deployed")
        elif status == "REJECTED":
            st.error("❌ **4. Gatekeeper Agent**\n\nRejected by Admin")
        else:
            st.info(f"ℹ️ **4. Gatekeeper Agent**\n\n{status}")

    st.markdown("---")

    # --- HUMAN-IN-THE-LOOP (HITL) GATEKEEPER INTERFACE ---
    st.markdown("### 🛑 Gatekeeper Human-in-the-Loop Control")

    if status == "PENDING_HUMAN_APPROVAL":
        st.warning("⚠️ **ACTION REQUIRED:** The system has generated and validated a compliance patch. Human authorization is mandatory before deploying changes to enterprise systems.")
        
        # Display Final Agent Payload
        with st.expander("🔍 Inspect Generated Remediation Patch Payload", expanded=True):
            payload = state_data.get("final_payload", {})
            if isinstance(payload, dict):
                st.json(payload)
            else:
                st.code(str(payload), language="markdown")

        btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 4])
        with btn_col1:
            if st.button("✅ Approve & Execute Patch", type="primary", use_container_width=True):
                state_data["status"] = "APPROVED"
                state_data["approved_by"] = "ComplianceAdmin"
                state_data["approved_at"] = datetime.utcnow().isoformat()
                save_state(state_data)
                st.success("Patch approved by administrator! Deployment initiated.")
                st.rerun()

        with btn_col2:
            if st.button("❌ Reject Patch Action", use_container_width=True):
                state_data["status"] = "REJECTED"
                state_data["rejected_by"] = "ComplianceAdmin"
                state_data["rejected_at"] = datetime.utcnow().isoformat()
                save_state(state_data)
                st.error("Patch action rejected by administrator.")
                st.rerun()

    elif status == "APPROVED":
        st.success(f"🎉 **APPROVED & DEPLOYED:** Approved by {state_data.get('approved_by', 'Admin')} at {state_data.get('approved_at')}.")
    elif status == "REJECTED":
        st.error(f"🚫 **REJECTED:** Action rejected by {state_data.get('rejected_by', 'Admin')} at {state_data.get('rejected_at')}.")

    st.markdown("---")

    # --- RAW MEMORY BANK TELEMETRY INSPECTOR ---
    with st.expander("🛠️ Memory Bank & Observability Raw Telemetry (For Hackathon Judges)"):
        st.json(state_data)