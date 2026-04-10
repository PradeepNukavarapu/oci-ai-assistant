import streamlit as st
from groq import Groq
import os
import oci

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="OCI AI Assistant", layout="wide")
st.title("🤖 OCI AI Assistant")

# -----------------------------
# Load API Key
# -----------------------------
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("API key not found. Please set GROQ_API_KEY.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# OCI Config
# -----------------------------
def get_oci_config():
    return {
        "user": st.secrets["OCI"]["user"],
        "key_content": st.secrets["OCI"]["key_content"],
        "fingerprint": st.secrets["OCI"]["fingerprint"],
        "tenancy": st.secrets["OCI"]["tenancy"],
        "region": st.secrets["OCI"]["region"],
    }

# -----------------------------
# OCI Function - List Instances
# -----------------------------
def list_instances():
    try:
        config = get_oci_config()

        compute = oci.core.ComputeClient(config)
        identity = oci.identity.IdentityClient(config)

        instances = []

        # ✅ Include ROOT compartment
        root_compartment_id = config["tenancy"]

        res = compute.list_instances(root_compartment_id).data
        for inst in res:
            instances.append(f"🔹 {inst.display_name} | {inst.lifecycle_state}")

        # ✅ Also check sub-compartments
        compartments = identity.list_compartments(
            config["tenancy"],
            compartment_id_in_subtree=True
        ).data

        for comp in compartments:
            res = compute.list_instances(comp.id).data
            for inst in res:
                instances.append(f"🔹 {inst.display_name} | {inst.lifecycle_state}")

        return instances if instances else ["No instances found"]

    except Exception as e:
        return [f"Error fetching instances: {str(e)}"]

# -----------------------------
# Chat History
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# User Input
# -----------------------------
user_input = st.chat_input("Ask about OCI (e.g., 'Show my instances')...")

if user_input:
    user_input_lower = user_input.lower()

    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # -----------------------------
    # 🔥 ROUTING LOGIC (KEY PART)
    # -----------------------------
    if any(word in user_input_lower for word in ["instance", "instances", "compute", "vm"]):
        
        with st.chat_message("assistant"):
            with st.spinner("Fetching OCI instances..."):
                data = list_instances()

                reply = "\n".join(data)

                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

    else:
        # Default → LLM
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})