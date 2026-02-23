"""
utils/ai_engine.py
OpenAI GPT-4 chat + Whisper voice transcription + gTTS voice response.
"""
import os
import tempfile
import openai
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# ─────────────────────────────────────────────
# System prompts
# ─────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "en": """You are a helpful, friendly customer support agent for a premium OTT (Over-The-Top) 
streaming platform. You assist customers with:
- Subscription plans and billing issues
- Account login and password reset
- Streaming quality and device compatibility
- Content availability and parental controls
- Cancellation and refund policies
- Technical troubleshooting

Always be polite, concise, and empathetic. If you cannot solve an issue, 
escalate gracefully by saying the customer will be contacted by a specialist within 24 hours.
Respond in English only.""",

    "ar": """أنت وكيل دعم عملاء ودود ومتعاون لمنصة بث OTT مميزة. تساعد العملاء في:
- خطط الاشتراك ومشاكل الفواتير
- تسجيل الدخول إلى الحساب وإعادة تعيين كلمة المرور
- جودة البث وتوافق الأجهزة
- توفر المحتوى وضوابط الرقابة الأبوية
- سياسات الإلغاء والاسترداد
- استكشاف الأخطاء التقنية وإصلاحها

كن دائمًا مهذبًا وموجزًا ومتعاطفًا. إذا لم تتمكن من حل مشكلة، 
أبلغ العميل بأن متخصصًا سيتواصل معه خلال 24 ساعة.
أجب باللغة العربية فقط."""
}

def get_system_prompt(language: str) -> str:
    return SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

# ─────────────────────────────────────────────
# Chat completion
# ─────────────────────────────────────────────
def chat_with_gpt(messages: list, language: str = "en") -> str:
    """
    Send conversation history to GPT-4 and return assistant reply.
    
    messages: list of {"role": "user"/"assistant", "content": "..."}
    """
    system = {"role": "system", "content": get_system_prompt(language)}
    full_messages = [system] + messages

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# ─────────────────────────────────────────────
# Whisper: audio → text
# ─────────────────────────────────────────────
def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    """
    Transcribe audio bytes using OpenAI Whisper.
    Returns transcribed text.
    """
    lang_code = "ar" if language == "ar" else "en"
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=lang_code
            )
        return transcript.text.strip()
    finally:
        os.unlink(tmp_path)

# ─────────────────────────────────────────────
# gTTS: text → audio bytes
# ─────────────────────────────────────────────
def text_to_speech(text: str, language: str = "en") -> bytes:
    """
    Convert text to speech using gTTS.
    Returns audio bytes (MP3).
    """
    lang_code = "ar" if language == "ar" else "en"
    tts = gTTS(text=text, lang=lang_code, slow=False)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tts.save(tmp.name)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        return audio_bytes
    finally:
        os.unlink(tmp_path)

# ─────────────────────────────────────────────
# Language detection (simple heuristic)
# ─────────────────────────────────────────────
def detect_language(text: str) -> str:
    """Simple Arabic character detection."""
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return "ar" if arabic_chars > len(text) * 0.2 else "en"
