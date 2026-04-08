import os
import streamlit as st

# streamlit-float
try:
    from streamlit_float import float_css_helper
    FLOAT_AVAILABLE = True
except Exception:
    FLOAT_AVAILABLE = False

# Groq LLM
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, AIMessage
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False


def _ask_groq(messages):
    if not GROQ_AVAILABLE:
        return "❌ Missing Groq libraries. Install: pip install langchain-groq langchain-core"

    # You can use env var OR secrets.toml
    key = os.getenv("GROQ_API_KEY", "")
    if not key.strip():
        # also try secrets
        try:
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            key = ""

    if not key.strip():
        return "❌ GROQ_API_KEY not set. Use: export GROQ_API_KEY='your_key' OR .streamlit/secrets.toml"

    chat = ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.3,
        groq_api_key=key
    )

    lc_msgs = []
    for m in messages:
        if m["role"] == "user":
            lc_msgs.append(HumanMessage(content=m["content"]))
        else:
            lc_msgs.append(AIMessage(content=m["content"]))

    return chat.invoke(lc_msgs).content.strip()


def _send_message():
    """
    Called when user presses Enter OR presses Send button.
    Important: Don't modify st.session_state["chatbot_draft"] after widget instantiation.
    """
    q = (st.session_state.get("chatbot_draft") or "").strip()
    if not q:
        return

    # Add user message
    st.session_state["chatbot_msgs"].append({"role": "user", "content": q})

    # Generate response
    try:
        reply = _ask_groq(st.session_state["chatbot_msgs"])
    except Exception as e:
        reply = f"❌ Error: {e}"

    # Add assistant message
    st.session_state["chatbot_msgs"].append({"role": "assistant", "content": reply})

    # Clear draft safely on next run
    st.session_state["clear_draft_next_run"] = True

    # Re-run to refresh UI
    st.rerun()


def render_floating_chatbot():
    # ----------------- checks -----------------
    if not FLOAT_AVAILABLE:
        st.error("❌ streamlit-float not installed. Run: pip install streamlit-float")
        return

    # ----------------- state -----------------
    if "chatbot_open" not in st.session_state:
        st.session_state["chatbot_open"] = False

    if "chatbot_msgs" not in st.session_state:
        st.session_state["chatbot_msgs"] = [
            {
                "role": "assistant",
                "content": "Hi Pranay 👋 I’m FinSight AI. Ask me about stocks, mutual funds, commodities, risk metrics."
            }
        ]

    if "chatbot_draft" not in st.session_state:
        st.session_state["chatbot_draft"] = ""

    if "clear_draft_next_run" not in st.session_state:
        st.session_state["clear_draft_next_run"] = False

    # ✅ IMPORTANT: clear BEFORE widget creates
    if st.session_state["clear_draft_next_run"]:
        st.session_state["chatbot_draft"] = ""
        st.session_state["clear_draft_next_run"] = False

    # ----------------- floating styles -----------------
    btn_style = float_css_helper(
        position="fixed",
        bottom="18px",
        right="18px",
        z_index="10000",
        width="150px",
    )

    box_style = float_css_helper(
        position="fixed",
        bottom="80px",
        right="18px",
        z_index="9999",
        width="360px",
        height="540px",
        background="rgba(10, 15, 35, 0.98)",
        border="1px solid rgba(255,255,255,0.14)",
        border_radius="22px",
        padding="14px",
        box_shadow="0 25px 90px rgba(0,0,0,0.55)",
    )

    # ✅ FIX: Force chatbot colors (app.py CSS overrides were fading it)
    st.markdown("""
    <style>
    /* Chatbot Title */
    .finsight-chat-title h3{
        color:#ffffff !important;
        font-weight:900 !important;
        letter-spacing:-0.02em !important;
        margin-bottom:0.25rem !important;
    }
    .finsight-chat-title p{
        color:rgba(255,255,255,0.72) !important;
        font-weight:650 !important;
        margin-top:-6px !important;
    }

    /* Prevent fade / opacity from global page CSS */
    .finsight-chatbox *{
        opacity:1 !important;
        filter:none !important;
        color:inherit;
    }

    /* Chat bubbles */
    .finsight-chatbox [data-testid="stChatMessage"]{
        background:transparent !important;
    }

    /* USER bubble */
    .finsight-chatbox [data-testid="stChatMessage"][aria-label="chat message user"]{
        background:rgba(0,212,255,0.10) !important;
        border:1px solid rgba(0,212,255,0.28) !important;
        border-radius:16px !important;
        padding:12px 14px !important;
    }

    /* ASSISTANT bubble */
    .finsight-chatbox [data-testid="stChatMessage"][aria-label="chat message assistant"]{
        background:rgba(255,255,255,0.06) !important;
        border:1px solid rgba(255,255,255,0.10) !important;
        border-radius:16px !important;
        padding:12px 14px !important;
    }

    /* Text inside chat messages */
    .finsight-chatbox [data-testid="stChatMessage"] p,
    .finsight-chatbox [data-testid="stChatMessage"] span,
    .finsight-chatbox [data-testid="stChatMessage"] div{
        color:rgba(255,255,255,0.92) !important;
        font-weight:600 !important;
        line-height:1.55 !important;
    }

    /* Chat input */
    .finsight-chatbox div[data-testid="stTextInput"] input{
        background:rgba(255,255,255,0.06) !important;
        border:1px solid rgba(255,255,255,0.14) !important;
        color:#ffffff !important;
        border-radius:14px !important;
        padding:12px 14px !important;
    }
    .finsight-chatbox div[data-testid="stTextInput"] input::placeholder{
        color:rgba(255,255,255,0.55) !important;
    }

    /* Buttons in chatbot */
    .finsight-chatbox div.stButton > button{
        border-radius:14px !important;
        border:none !important;
        font-weight:800 !important;
        background:linear-gradient(135deg,#00d4ff 0%,#00ff88 100%) !important;
        color:#081018 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ----------------- floating button -----------------
    btn = st.container()
    btn.float(btn_style)

    if st.session_state["chatbot_open"]:
        if btn.button("✖ Close Chat", use_container_width=True):
            st.session_state["chatbot_open"] = False
            st.rerun()
    else:
        if btn.button("💬 Chat", use_container_width=True):
            st.session_state["chatbot_open"] = True
            st.rerun()

    # If chatbot closed, stop here
    if not st.session_state["chatbot_open"]:
        return

    # ----------------- floating chatbox -----------------
    box = st.container()
    box.float(box_style)

    with box:
        # ✅ wrapper so CSS applies ONLY inside chatbot
        st.markdown('<div class="finsight-chatbox">', unsafe_allow_html=True)

        st.markdown('<div class="finsight-chat-title">', unsafe_allow_html=True)
        st.markdown("### FinSight AI 🤖")
        st.caption("Ask about risk, returns, investing discipline")
        st.markdown("</div>", unsafe_allow_html=True)

        # Chat messages
        chat_area = st.container(height=320)
        with chat_area:
            for m in st.session_state["chatbot_msgs"]:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])

        # -------- Enter-to-send input --------
        # Enter triggers _send_message automatically
        st.text_input(
            "Message",
            key="chatbot_draft",
            label_visibility="collapsed",
            placeholder="Type a message and press Enter...",
            on_change=_send_message  # ✅ ENTER SEND
        )

        # Optional manual send/clear buttons
        c1, c2 = st.columns([1, 1])

        with c1:
            if st.button("Send ", use_container_width=True):
                _send_message()

        with c2:
            if st.button("🧹 Clear", use_container_width=True):
                st.session_state["chatbot_msgs"] = [
                    {"role": "assistant", "content": "✅ Chat cleared. Ask again!"}
                ]
                st.session_state["clear_draft_next_run"] = True
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
