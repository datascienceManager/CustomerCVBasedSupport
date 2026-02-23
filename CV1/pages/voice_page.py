"""
pages/voice_page.py
Voice support interface - record audio, transcribe, get AI reply, play back TTS.
"""
import streamlit as st
import io
from utils.ai_engine import transcribe_audio, chat_with_gpt, text_to_speech, detect_language
from utils.database import create_session, save_message, get_session_messages
from utils.sheets import append_single_message
from utils.database import get_connection
from datetime import datetime

LABELS = {
    "en": {
        "title": "🎙️ Voice Support",
        "subtitle": "Record your question and get a voice response",
        "upload_label": "Upload audio file (WAV/MP3/M4A)",
        "transcribed": "📝 You said:",
        "ai_reply": "🤖 Assistant replied:",
        "play_response": "🔊 Play Response",
        "thinking": "Processing your voice...",
        "no_audio": "Please upload an audio file.",
        "history_title": "📜 Conversation History"
    },
    "ar": {
        "title": "🎙️ دعم صوتي",
        "subtitle": "سجّل سؤالك واحصل على رد صوتي",
        "upload_label": "رفع ملف صوتي (WAV/MP3/M4A)",
        "transcribed": "📝 قلت:",
        "ai_reply": "🤖 ردّ المساعد:",
        "play_response": "🔊 تشغيل الرد",
        "thinking": "جاري معالجة صوتك...",
        "no_audio": "يرجى رفع ملف صوتي.",
        "history_title": "📜 سجل المحادثة"
    }
}

def get_last_message_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM messages")
    result = cursor.fetchone()
    conn.close()
    return result[0] or 0

def render_voice(language: str, session_id: str):
    lbl = LABELS[language]

    if language == "ar":
        st.markdown("""
        <style>
        .element-container { direction: rtl; }
        </style>""", unsafe_allow_html=True)

    st.title(lbl["title"])
    st.caption(lbl["subtitle"])
    st.markdown("---")

    create_session(session_id, language, "voice")

    if "voice_messages" not in st.session_state:
        stored = get_session_messages(session_id)
        st.session_state.voice_messages = [
            {"role": m["role"], "content": m["content"]} for m in stored
            if m.get("mode") == "voice" or True  # load all for context
        ]

    # ── Audio upload ───────────────────────────────────────────────────────────
    st.subheader("🎤 Record or Upload")
    st.info("💡 Use your phone or mic recorder app to record a WAV/MP3 file, then upload it here.")

    audio_file = st.file_uploader(
        lbl["upload_label"],
        type=["wav", "mp3", "m4a", "ogg", "webm"],
        key="voice_upload"
    )

    if st.button("🚀 Process Audio", disabled=audio_file is None):
        if not audio_file:
            st.warning(lbl["no_audio"])
        else:
            with st.spinner(lbl["thinking"]):
                audio_bytes = audio_file.read()

                # Step 1: Transcribe
                user_text = transcribe_audio(audio_bytes, language)
                detected_lang = detect_language(user_text)
                active_lang = detected_lang

                st.success(f"{lbl['transcribed']} **{user_text}**")

                # Save user message
                save_message(session_id, "user", user_text, active_lang, "voice")
                st.session_state.voice_messages.append({"role": "user", "content": user_text})

                # Step 2: GPT-4 reply
                reply = chat_with_gpt(st.session_state.voice_messages, active_lang)
                st.info(f"{lbl['ai_reply']} **{reply}**")

                # Save assistant message
                save_message(session_id, "assistant", reply, active_lang, "voice")
                st.session_state.voice_messages.append({"role": "assistant", "content": reply})

                # Real-time Google Sheets sync
                msg_id = get_last_message_id()
                append_single_message({
                    "id": msg_id,
                    "session_id": session_id,
                    "role": "assistant",
                    "content": reply,
                    "language": active_lang,
                    "mode": "voice",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                # Step 3: TTS
                tts_audio = text_to_speech(reply, active_lang)
                st.audio(tts_audio, format="audio/mp3")
                st.caption(lbl["play_response"])

    # ── Conversation history ───────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(lbl["history_title"])
    for msg in st.session_state.get("voice_messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Sync button ────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("📤 Sync to Google Sheets"):
        from utils.sheets import sync_messages_to_sheet
        from utils.database import get_all_messages_flat
        result = sync_messages_to_sheet(get_all_messages_flat())
        if result["success"]:
            st.success(f"✅ Synced! ({result['synced']} new rows)")
        else:
            st.error("❌ " + result["error"])
