import streamlit as st
from groq import Groq
import os
import oci
from pathlib import Path

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="OCI AI Assistant", layout="wide")

# -----------------------------
# Brand + UI Styling
# -----------------------------
logo_candidates = [
    Path(__file__).parent / "assets" / "infolob-logo.png",
    Path(
        r"C:\Users\Pradeep\.cursor\projects\e-Onedrive-OneDrive-INFOLOB-Global-Inc-Infolob-AI-use-cases-Sushma-Usecase-3-OCI-AI-Assistant-oci-ai-assistant\assets\c__Users_Pradeep_AppData_Roaming_Cursor_User_workspaceStorage_526de99ca74ad46c3c3ad68fac7aa53c_images_image-db67df60-3265-43b5-b453-f7506ac1617c.png"
    ),
    Path(
        r"C:\Users\Pradeep\.cursor\projects\e-Onedrive-OneDrive-INFOLOB-Global-Inc-Infolob-AI-use-cases-Sushma-Usecase-3-OCI-AI-Assistant-oci-ai-assistant\assets\c__Users_Pradeep_AppData_Roaming_Cursor_User_workspaceStorage_526de99ca74ad46c3c3ad68fac7aa53c_images_image-1c42517d-030b-4623-8dba-f4e646129f17.png"
    ),
]

logo_path = next((p for p in logo_candidates if p.exists()), None)

st.markdown(
    """
    <style>
    /* Hide default Streamlit chrome (top-right share/git menu etc.) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}
    button[title="Manage app"] {display: none !important;}
    [aria-label="Manage app"] {display: none !important;}

    /* Soft app background */
    .stApp {
        background: linear-gradient(145deg, #f4f7fb 0%, #edf4f7 40%, #f7f2f5 100%);
    }
    .main .block-container {
        max-width: 1250px;
        padding-top: 0.55rem;
        padding-bottom: 1rem;
    }

    /* Sticky top section */
    .sticky-shell {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(244, 247, 251, 0.93);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        padding: 0.25rem 0 0.45rem 0;
        margin-bottom: 0.55rem;
    }

    .brand-line {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin: 0 0 0.42rem 0;
        color: #7d0000;
        font-size: 0.86rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* Top hero block */
    .assistant-hero {
        background: linear-gradient(120deg, #7d0000 0%, #9c1111 55%, #c33939 100%);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 10px 24px rgba(125, 0, 0, 0.22);
        color: #ffffff;
    }
    .assistant-hero h1 {
        margin: 0;
        font-size: 1.9rem;
        line-height: 1.2;
    }
    .assistant-hero p {
        margin: 0.35rem 0 0;
        color: #ffe8e8;
        font-size: 0.98rem;
    }
    .helper-chip {
        display: inline-block;
        margin-top: 0.65rem;
        padding: 0.25rem 0.55rem;
        border: 1px solid rgba(255, 255, 255, 0.45);
        border-radius: 16px;
        font-size: 0.8rem;
    }

    /* Soothing chat cards */
    [data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 0.48rem 0.65rem;
        margin-bottom: 0.25rem;
        border: 1px solid rgba(130, 155, 176, 0.22);
        background: #f8fbff;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #eff6f8;
        border-color: rgba(112, 158, 156, 0.3);
    }
    [data-testid="stChatInput"] {
        background: rgba(250, 252, 255, 0.96);
        border-top: 1px solid #d6e1eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="sticky-shell">', unsafe_allow_html=True)
top_left, top_right = st.columns([5.1, 1.1])
with top_left:
    st.markdown(
        """
        <div class="brand-line">INF OLOB | Cloud & AI Solutions</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="assistant-hero">
            <h1>OCI AI Assistant</h1>
            <p>Ask about compute, compartments, databases and storage with a cleaner chat experience.</p>
            <span class="helper-chip">INF OLOB Cloud Assistant</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with top_right:
    if logo_path:
        st.image(str(logo_path), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

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
        seen = set()

        def add_dbs(dbs):
            for db in dbs:
                if db.id not in seen:
                    seen.add(db.id)
                    dbs_list.append(
                        {
                            "name": db.db_name,
                            "state": db.lifecycle_state,
                            "id": db.id,
                        }
                    )

        root_compartment_id = config["tenancy"]

        dbs = database.list_autonomous_databases(
            compartment_id=root_compartment_id
        ).data
        add_dbs(dbs)

        compartments = identity.list_compartments(
            config["tenancy"],
            compartment_id_in_subtree=True
        ).data

        for comp in compartments:
            dbs = database.list_autonomous_databases(
                compartment_id=comp.id
            ).data
            add_dbs(dbs)

        return dbs_list if dbs_list else ["No databases found"]

    except Exception as e:
        return [f"Error fetching databases: {str(e)}"]


def start_database(db_id):
    try:
        config = get_oci_config()
        database = oci.database.DatabaseClient(config)

        database.start_autonomous_database(db_id)

        return "✅ Database start initiated successfully."

    except Exception as e:
        return f"Error starting database: {str(e)}"


def stop_database(db_id):
    try:
        config = get_oci_config()
        database = oci.database.DatabaseClient(config)

        database.stop_autonomous_database(db_id)

        return "🛑 Database stop initiated successfully."

    except Exception as e:
        return f"Error stopping database: {str(e)}"


# -----------------------------
# Chat History
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_intent" not in st.session_state:
    st.session_state.last_intent = None

if "last_db" not in st.session_state:
    st.session_state.last_db = None

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

    # Action detection
    if any(word in user_input_lower for word in ["start", "restart"]):
        st.session_state.last_intent = "start_db"

    elif any(word in user_input_lower for word in ["stop", "shutdown"]):
        st.session_state.last_intent = "stop_db"

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
                elif data and isinstance(data[0], str):
                    reply = "\n".join(data)
                else:
                    st.session_state.last_db = data[0]
                    lines = [
                        f"🔹 {d['name']} | {d['state']}\n   `{d['id']}`"
                        for d in data
                    ]
                    reply = f"🗄️ Found {len(data)} database(s):\n\n" + "\n".join(lines)

            elif intent == "start_db":
                if st.session_state.last_db:
                    with st.spinner("Starting database..."):
                        reply = start_database(st.session_state.last_db["id"])
                else:
                    reply = "⚠️ Please select a database first."

            elif intent == "stop_db":
                if st.session_state.last_db:
                    with st.spinner("Stopping database..."):
                        reply = stop_database(st.session_state.last_db["id"])
                else:
                    reply = "⚠️ Please select a database first."

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