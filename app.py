
import streamlit as st
import requests
import sqlite3
from pathlib import Path
from gtts import gTTS
from io import BytesIO
from datetime import datetime

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="LingoAI Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= LANGUAGES =================

languages = {
    "English": "en",
    "Urdu": "ur",
    "Hindi": "hi",
    "Arabic": "ar",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Japanese": "ja",
    "Turkish": "tr",
    "Chinese": "zh-CN",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Korean": "ko",
    "Bengali": "bn",
    "Punjabi": "pa",
    "Dutch": "nl",
    "Greek": "el",
    "Thai": "th",
    "Vietnamese": "vi",
    "Indonesian": "id",
    "Polish": "pl",
    "Swedish": "sv",
    "Tamil": "ta",
    "Persian": "fa"
}

# ================= DATABASE =================

DB_PATH = Path(__file__).parent / "translations.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_language TEXT,
                target_language TEXT,
                original_text TEXT,
                translated_text TEXT,
                created_at TEXT
            )
        """)


def save_translation(source, target, original, translated):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO translations
            (source_language, target_language, original_text,
             translated_text, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            source,
            target,
            original,
            translated,
            datetime.now().strftime("%d %b %Y, %I:%M %p")
        ))


def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
            SELECT source_language, target_language,
                   original_text, translated_text, created_at
            FROM translations
            ORDER BY id DESC
            LIMIT 5
        """).fetchall()


def clear_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM translations")


init_db()

# ================= SESSION STATE =================

defaults = {
    "input_text": "",
    "translated_text": "",
    "app_message": None,
    "audio_data": None,
    "translation_count": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ================= CALLBACKS =================

def clear_text():
    st.session_state.input_text = ""
    st.session_state.translated_text = ""
    st.session_state.audio_data = None
    st.session_state.app_message = None


def swap_languages():
    source = st.session_state.source_language
    target = st.session_state.target_language

    st.session_state.source_language = target
    st.session_state.target_language = source

    st.session_state.translated_text = ""
    st.session_state.audio_data = None
    st.session_state.app_message = None


def delete_history():
    clear_history()
    st.session_state.app_message = (
        "success", "Translation history cleared!"
    )


# ================= TRANSLATION =================

def translate_text():
    text = st.session_state.input_text.strip()
    source = st.session_state.source_language
    target = st.session_state.target_language

    st.session_state.translated_text = ""
    st.session_state.audio_data = None
    st.session_state.app_message = None

    if not text:
        st.session_state.app_message = (
            "warning", "Please enter some text before translating."
        )
        return

    if len(text) > 1000:
        st.session_state.app_message = (
            "warning", "Maximum 1000 characters allowed."
        )
        return

    if source == target:
        st.session_state.app_message = (
            "warning", "Source and target languages cannot be the same."
        )
        return

    url = "https://api.mymemory.translated.net/get"

    params = {
        "q": text,
        "langpair": f"{languages[source]}|{languages[target]}"
    }

    try:
        with st.spinner("🌍 Translating your text... Please wait!"):
            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            response.raise_for_status()
            data = response.json()

            if data.get("responseStatus") != 200:
                raise ValueError(
                    data.get("responseDetails", "Translation service error.")
                )

            translated = data.get("responseData", {}).get(
                "translatedText", ""
            )

            if not translated.strip():
                raise ValueError("Translation result is empty.")

            st.session_state.translated_text = translated

            save_translation(
                source,
                target,
                text,
                translated
            )

            st.session_state.translation_count += 1

        st.session_state.app_message = (
            "success", "Translation completed successfully!"
        )

    except requests.exceptions.Timeout:
        st.session_state.app_message = (
            "error", "Request timed out. Please try again."
        )

    except requests.exceptions.ConnectionError:
        st.session_state.app_message = (
            "error", "No internet connection. Please check your internet."
        )

    except requests.exceptions.HTTPError:
        st.session_state.app_message = (
            "error", "Translation service is temporarily unavailable."
        )

    except ValueError as error:
        st.session_state.app_message = (
            "error", f"Translation failed: {error}"
        )

    except requests.exceptions.RequestException:
        st.session_state.app_message = (
            "error", "A network error occurred. Please try again."
        )

    except Exception:
        st.session_state.app_message = (
            "error", "Something went wrong. Please try again."
        )


# ================= AUDIO =================

def generate_audio():
    translated = st.session_state.translated_text

    if not translated:
        st.session_state.app_message = (
            "warning", "Translate some text before generating audio."
        )
        return

    target_code = languages[st.session_state.target_language]

    try:
        with st.spinner("🔊 Generating audio..."):
            audio_buffer = BytesIO()

            tts = gTTS(
                text=translated,
                lang=target_code
            )

            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            st.session_state.audio_data = audio_buffer.getvalue()

    except Exception:
        st.session_state.audio_data = None
        st.session_state.app_message = (
            "error", "Audio is unavailable for this language or connection."
        )


# ================= CSS DESIGN =================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #080d1c 0%,
        #11152c 50%,
        #17132e 100%
    );
    color: #ffffff;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 1px;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #aaa9c8;
    font-size: 17px;
    margin-bottom: 30px;
}

.section-title {
    color: #c4b5fd;
    font-size: 22px;
    font-weight: 750;
    margin-bottom: 12px;
}

.feature-card {
    background: linear-gradient(135deg, #1c2341, #252044);
    border: 1px solid #49416d;
    border-radius: 15px;
    padding: 20px;
    min-height: 140px;
    margin-bottom: 10px;
}

.feature-card h3 {
    color: #c4b5fd;
    font-size: 19px;
}

.feature-card p {
    color: #c0c0d6;
    font-size: 14px;
}

.about-card {
    background: #171d35;
    border: 1px solid #51467e;
    padding: 22px;
    border-radius: 15px;
    color: #d2d1e7;
    line-height: 1.8;
}

div[data-testid="stTextArea"] textarea {
    background-color: #171d35;
    color: white;
    border: 1px solid #51467e;
    border-radius: 12px;
    font-size: 16px;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #171d35;
    border-radius: 10px;
}

.stButton button {
    background: linear-gradient(90deg, #7055e8, #9b5de5);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    padding: 11px 18px;
    width: 100%;
}

.stButton button:hover {
    background: linear-gradient(90deg, #8b75f0, #b276ed);
    color: white;
    border: none;
}

div[data-testid="stDownloadButton"] button {
    background: #252044;
    color: white;
    border: 1px solid #6655a5;
    border-radius: 10px;
    width: 100%;
}

.footer {
    text-align: center;
    color: #9695b4;
    margin-top: 40px;
    padding: 20px;
    border-top: 1px solid #353450;
    font-size: 13px;
}

@media (max-width: 700px) {
    .main-title {
        font-size: 34px;
    }

    .subtitle {
        font-size: 14px;
    }
}

</style>
""", unsafe_allow_html=True)


# ================= HEADER =================

st.markdown(
    '<div class="main-title">🌍 LingoAI Translator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Break Language Barriers with AI-Powered Translation</div>',
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#a78bfa;'>"
    "✨ Translate • Listen • Save • Explore"
    "</p>",
    unsafe_allow_html=True
)

st.divider()


# ================= LANGUAGE SELECTION =================

st.markdown(
    '<div class="section-title">🌐 Language Selection</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([5, 1, 5])

with col1:
    st.selectbox(
        "Source Language",
        list(languages.keys()),
        index=0,
        key="source_language"
    )

with col2:
    st.write("")
    st.write("")
    st.button(
        "🔄 Swap",
        on_click=swap_languages
    )

with col3:
    st.selectbox(
        "Target Language",
        list(languages.keys()),
        index=1,
        key="target_language"
    )

st.write("")


# ================= INPUT AREA =================

st.markdown(
    '<div class="section-title">✍️ Enter Your Text</div>',
    unsafe_allow_html=True
)

input_text = st.text_area(
    "Enter text",
    key="input_text",
    height=180,
    max_chars=2000,
    placeholder="Type or paste your text here..."
)

character_count = len(input_text)

st.caption(f"Characters: {character_count} / 1000")

if character_count > 1000:
    st.warning("⚠️ Maximum 1000 characters allowed.")


# ================= ACTION BUTTONS =================

button1, button2 = st.columns(2)

with button1:
    st.button(
        "✨ Translate Now",
        on_click=translate_text,
        use_container_width=True
    )

with button2:
    st.button(
        "🗑️ Clear Text",
        on_click=clear_text,
        use_container_width=True
    )


# ================= STATUS MESSAGE =================

if st.session_state.app_message:
    message_type, message_text = st.session_state.app_message

    if message_type == "success":
        st.success(message_text)
    elif message_type == "warning":
        st.warning(message_text)
    else:
        st.error(message_text)


# ================= TRANSLATION RESULT =================

if st.session_state.translated_text:

    st.divider()

    st.markdown(
        '<div class="section-title">📝 Translation Result</div>',
        unsafe_allow_html=True
    )

    st.text_area(
        "Translated text",
        value=st.session_state.translated_text,
        height=180,
        key="translation_output"
    )

    download_text = f"""
LingoAI Translator
==================

From: {st.session_state.source_language}
To: {st.session_state.target_language}

Original Text:
{st.session_state.input_text}

Translated Text:
{st.session_state.translated_text}
"""

    download_col, audio_col = st.columns(2)

    with download_col:
        st.download_button(
            "⬇️ Download Translation",
            data=download_text,
            file_name="lingoai_translation.txt",
            mime="text/plain",
            use_container_width=True
        )

    with audio_col:
        st.button(
            "🔊 Generate Audio",
            on_click=generate_audio,
            use_container_width=True
        )

    if st.session_state.audio_data:
        st.audio(
            st.session_state.audio_data,
            format="audio/mp3"
        )


# ================= TRANSLATION HISTORY =================

st.divider()

st.markdown(
    '<div class="section-title">📚 Recent Translation History</div>',
    unsafe_allow_html=True
)

history = get_history()

if history:

    for item in history:
        source, target, original, translated, created_at = item

        with st.expander(
            f"{source} ➜ {target} | {created_at}"
        ):
            st.markdown("**Original Text:**")
            st.write(original)

            st.markdown("**Translated Text:**")
            st.write(translated)

    st.button(
        "🗑️ Clear History",
        on_click=delete_history
    )

else:
    st.info("No translation history yet.")


# ================= FEATURES =================

st.divider()

st.markdown(
    '<div class="section-title">✨ Why Choose LingoAI?</div>',
    unsafe_allow_html=True
)

feature1, feature2, feature3 = st.columns(3)

with feature1:
    st.markdown("""
    <div class="feature-card">
        <h3>🌍 25 Languages</h3>
        <p>Translate text between multiple languages with ease.</p>
    </div>
    """, unsafe_allow_html=True)

with feature2:
    st.markdown("""
    <div class="feature-card">
        <h3>🔊 Text to Speech</h3>
        <p>Listen to your translated text with audio support.</p>
    </div>
    """, unsafe_allow_html=True)

with feature3:
    st.markdown("""
    <div class="feature-card">
        <h3>📚 Translation History</h3>
        <p>Save and revisit your recent translations anytime.</p>
    </div>
    """, unsafe_allow_html=True)


# ================= ABOUT =================

st.divider()

with st.expander("ℹ️ About LingoAI Translator"):

    st.markdown("### 🌍 Welcome to LingoAI!")

    st.write(
        "LingoAI Translator is a simple and user-friendly "
        "language translation application developed using Python "
        "and Streamlit."
    )

    st.write(
        "It helps users translate text between different languages, "
        "listen to translated content, download results and maintain "
        "translation history."
    )

    st.markdown("**Technologies Used:**")

    st.write(
        "Python • Streamlit • MyMemory Translation API • SQLite • gTTS"
    )


# ================= FOOTER =================

st.markdown("""
<div class="footer">
    <h3 style="color:#c4b5fd;">🌍 LingoAI Translator</h3>
    Made with ❤️ using Python and Streamlit
    <br><br>
    Version 1.0 | AI Internship Project
    <br>
    © 2026 LingoAI. All Rights Reserved.
</div>
""", unsafe_allow_html=True)
