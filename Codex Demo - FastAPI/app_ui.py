import streamlit as st
import httpx

# Configure page layout matrices and browser tab naming conventions
st.set_page_config(page_title="Dhaka CivicPulse Dashboard", page_icon="🏙️", layout="wide")

st.title("🏙️ Dhaka CivicPulse Management Dashboard")
st.markdown("### Real-Time AI-Native Urban Triage & Resource Optimization Platform")
st.write("---")

# Sidebar module managing OAuth2 authentication handshakes
st.sidebar.header("🔒 Municipal Security Gateway")
username = st.sidebar.text_input("Username", value="demo")
password = st.sidebar.text_input("Password", value="secret", type="password")

# Initialize isolated browser session memory slots for token caching
if "token" not in st.session_state:
    st.session_state.token = None

if st.sidebar.button("Login to Gateway"):
    try:
        resp = httpx.post("http://127.0.0.1:8000/token", data={"username": username, "password": password})
        if resp.status_code == 200:
            st.session_state.token = resp.json()["access_token"]
            st.sidebar.success("Secure Session Established!")
        else:
            st.sidebar.error("Invalid municipal credentials.")
    except Exception:
        st.sidebar.error("Could not connect to FastAPI backend server.")

# Main Dashboard View Logic
if not st.session_state.token:
    st.warning("⚠️ Please authenticate via the Municipal Security Gateway sidebar to unlock operational maps.")
else:
    # Split viewport evenly: input triage capture on left, live telemetry visualizer on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 Ingest Raw Citizen Reports")
        user_report = st.text_area(
            "Enter report string (Accepts English, Bangla, or Banglish text syntax):",
            placeholder="e.g., Mirpur 10 rasta dube gese flash flood er karone, bishal traffic jam..."
        )
        
        if st.button("Submit Report to AI Triage"):
            if not user_report.strip():
                st.error("Please enter a valid descriptive report payload.")
            else:
                with st.spinner("Agent parsing intent matrices..."):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        triage_resp = httpx.post(
                            "http://127.0.0.1:8000/civic/triage", 
                            json={"report": user_report}, 
                            headers=headers,
                            timeout=15.0
                        )
                        
                        if triage_resp.status_code == 200:
                            st.session_state.last_result = triage_resp.json()
                            st.success("AI Analysis Completed Successfully!")
                        else:
                            st.error(f"Backend Returned Fault Block: Code {triage_resp.status_code}")
                    except Exception as e:
                        st.error(f"Communication Framework Break: {str(e)}")

    with col2:
        st.subheader("📊 Live Agent Triage Visualizer")
        if "last_result" in st.session_state:
            result = st.session_state.last_result
            action_code = result.get("action_code")
            status_text = result.get("status")
            meta_data = result.get("meta", {})
            
            # Dynamic card colors and metric layouts reflecting backend agent tools
            if action_code == "ADD_ROUTE":
                st.error(f"🚨 ALERT STATUS: {status_text}")
                metric1, metric2 = st.columns(2)
                metric1.metric("Hazard Severity Score", f"{meta_data.get('hazard_index')}/10")
                metric2.metric("Vulnerability Index", f"{meta_data.get('vulnerability_weight')}/10")
                st.info(f"⚡ System Dispatch Sorting Key Generated: **{result.get('priority_key')}**")
                
            elif action_code == "FACTORIAL_ROUTE":
                st.warning(f"🔧 UTILITY LOG STATUS: {status_text}")
                st.metric("Target Ward Code Block", f"Zone {meta_data.get('block_identifier')}")
                st.success(f"🔀 Computed Deployment Routing Paths: **{result.get('routing_permutations')}**")
                
            else:
                st.info(f"📋 QUEUE STATUS: {status_text}")
                st.write(result.get("detail"))
                
            st.write("---")
            st.markdown("#### Raw Operational Telemetry Payload:")
            st.json(result)
        else:
            st.info("💡 Submit a local notification report to see live telemetry mapping layouts appear here.")
