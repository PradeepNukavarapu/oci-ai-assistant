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


def list_compartments():
    try:
        config = get_oci_config()
        identity = oci.identity.IdentityClient(config)

        compartments = identity.list_compartments(
            config["tenancy"],
            compartment_id_in_subtree=True
        ).data

        return [f"🔹 {c.name}" for c in compartments] or ["No compartments found"]
    except Exception as e:
        return [f"Error fetching compartments: {str(e)}"]


def list_buckets():
    try:
        config = get_oci_config()
        object_storage = oci.object_storage.ObjectStorageClient(config)

        namespace = object_storage.get_namespace().data

        buckets = object_storage.list_buckets(
            namespace_name=namespace,
            compartment_id=config["tenancy"]
        ).data

        return [f"🔹 {b.name}" for b in buckets] or ["No buckets found"]
    except Exception as e:
        return [f"Error fetching buckets: {str(e)}"]


def list_databases():
    try:
        config = get_oci_config()
        database = oci.database.DatabaseClient(config)
        identity = oci.identity.IdentityClient(config)

        dbs_list = []

        # ✅ Include ROOT
        root_compartment_id = config["tenancy"]

        dbs = database.list_autonomous_databases(
            compartment_id=root_compartment_id
        ).data

        for db in dbs:
            dbs_list.append(
                f"🔹 {db.db_name} | {db.lifecycle_state}"
            )

        # ✅ Include sub-compartments
        compartments = identity.list_compartments(
            config["tenancy"],
            compartment_id_in_subtree=True
        ).data

        for comp in compartments:
            dbs = database.list_autonomous_databases(
                compartment_id=comp.id
            ).data

            for db in dbs:
                dbs_list.append(
                    f"🔹 {db.db_name} | {db.lifecycle_state}"
                )

        return dbs_list if dbs_list else ["No databases found"]

    except Exception as e:
        return [f"Error fetching databases: {str(e)}"]

# -----------------------------
# Chat History
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_intent" not in st.session_state:
    st.session_state.last_intent = None

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
    # 🔥 SMART INTENT DETECTION
    # -----------------------------
    intent_map = {
        "instances": ["instance", "instances", "vm", "compute"],
        "compartments": ["compartment", "compartments"],
        "databases": ["database", "databases", "adb"],
        "buckets": ["bucket", "buckets", "object storage", "storage"],
    }

    detected_intent = None

    for intent, keywords in intent_map.items():
        if any(word in user_input_lower for word in keywords):
            detected_intent = intent
            break

    # Update intent ONLY if detected
    if detected_intent:
        st.session_state.last_intent = detected_intent

    # If user asks generic question, let LLM handle
    if any(word in user_input_lower for word in ["why", "what", "explain", "how"]):
        st.session_state.last_intent = None

    # -----------------------------
    # 🔥 ROUTING WITH FALLBACK
    # -----------------------------
    with st.chat_message("assistant"):
        if st.session_state.last_intent:

            intent = st.session_state.last_intent

            if intent == "instances":
                with st.spinner("Fetching OCI instances..."):
                    data = list_instances()

                if data == ["No instances found"]:
                    reply = (
                        "❌ I checked your OCI tenancy and couldn’t find any compute instances. "
                        "It looks like no VMs are currently created."
                    )
                else:
                    reply = (
                        f"✅ I found {len(data)} VM(s) in your tenancy:\n\n"
                        + "\n".join(data)
                    )

            elif intent == "compartments":
                with st.spinner("Fetching compartments..."):
                    data = list_compartments()
                reply = (
                    "📁 Here are the compartments available in your tenancy:\n\n"
                    + "\n".join(data)
                )

            elif intent == "databases":
                with st.spinner("Fetching databases..."):
                    data = list_databases()

                if data == ["No databases found"]:
                    reply = (
                        "❌ I couldn’t find any Autonomous Databases in your tenancy. If you expected "
                        "one (even inactive), it might be in a different compartment or not "
                        "accessible with current permissions."
                    )
                else:
                    reply = f"🗄️ Found {len(data)} database(s):\n\n" + "\n".join(data)

            elif intent == "buckets":
                with st.spinner("Fetching buckets..."):
                    data = list_buckets()

                if data == ["No buckets found"]:
                    reply = (
                        "❌ No Object Storage buckets found in the root compartment. "
                        "You might have buckets in other compartments."
                    )
                else:
                    reply = f"🪣 Found {len(data)} bucket(s):\n\n" + "\n".join(data)

            else:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=st.session_state.messages
                )
                reply = response.choices[0].message.content

        else:
            # fallback to LLM
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})