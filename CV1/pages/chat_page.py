"""
pages/chat_page.py
Chat support interface with English/Arabic support.
"""
import streamlit as st
from utils.ai_engine import chat_with_gpt, detect_language
from utils.database import create_session, save_message, get_session_messages
from utils.sheets import append_single_message
from utils.database import get_connection
from datetime import datetime

LABELS = {
    "en": {
        "title": "💬 Chat Support",
        "subtitle": "Hi! How can we help you today?",
        "placeholder": "Type your message here...",
        "send": "Send",
        "thinking": "Assistant is thinking...",
        "feedback_title": "Rate this conversation",
        "feedback_thanks": "Thank you for your feedback!",
        "sync": "Sync to Google Sheets",
        "sync_success": "✅ Synced successfully!",
        "sync_fail": "❌ Sync failed: "
    },
    "ar": {
        "title": "💬 دعم المحادثة",
        "subtitle": "مرحبًا! كيف يمكننا مساعدتك اليوم؟",
        "placeholder": "اكتب رسالتك هنا...",
        "send": "إرسال",
        "thinking": "المساعد يفكر...",
        "feedback_title": "قيّم هذه المحادثة",
        "feedback_thanks": "شكرًا على ملاحظاتك!",
        "sync": "مزامنة مع Google Sheets",
        "sync_success": "✅ تمت المزامنة بنجاح!",
        "sync_fail": "❌ فشلت المزامنة: "
    }
}

def get_last_message_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM messages")
    result = cursor.fetchone()
    conn.close()
    return result[0] or 0

def render_chat(language: str, session_id: str):
    lbl = LABELS[language]

    # RTL support for Arabic
    if language == "ar":
        st.markdown("""
        <style>
        .stChatMessage { direction: rtl; text-align: right; }
        .stTextInput input { direction: rtl; }
        </style>""", unsafe_allow_html=True)

    st.title(lbl["title"])
    st.caption(lbl["subtitle"])
    st.markdown("---")

    # Init session
    create_session(session_id, language, "chat")

    # Load existing messages
    if "messages" not in st.session_state:
        stored = get_session_messages(session_id)
        st.session_state.messages = [
            {"role": m["role"], "content": m["content"]} for m in stored
        ]

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input(lbl["placeholder"]):
        # Auto-detect language from input
        detected_lang = detect_language(prompt)
        active_lang = detected_lang if detected_lang != language else language

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Save user message to DB
        save_message(session_id, "user", prompt, active_lang, "chat")

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner(lbl["thinking"]):
                reply = chat_with_gpt(
                    [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    active_lang
                )
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Save assistant message to DB
        save_message(session_id, "assistant", reply, active_lang, "chat")

        # Real-time sync to Google Sheets (best effort)
        msg_id = get_last_message_id()
        append_single_message({
            "id": msg_id,
            "session_id": session_id,
            "role": "assistant",
            "content": reply,
            "language": active_lang,
            "mode": "chat",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # ── Footer actions ────────────────────────────────────────────────────────
    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        # Feedback
        with st.expander(lbl["feedback_title"]):
            rating = st.slider("⭐", 1, 5, 3, key="chat_rating")
            comment = st.text_input("Comment (optional)", key="chat_comment")
            if st.button("Submit Feedback"):
                from utils.database import save_feedback
                save_feedback(session_id, rating, comment)
                st.success(lbl["feedback_thanks"])

    with col2:
        # Manual sync button
        if st.button(lbl["sync"]):
            from utils.sheets import sync_messages_to_sheet
            from utils.database import get_all_messages_flat
            result = sync_messages_to_sheet(get_all_messages_flat())
            if result["success"]:
                st.success(f"{lbl['sync_success']} ({result['synced']} rows)")
            else:
                st.error(lbl["sync_fail"] + result["error"])
