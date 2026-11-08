
import os
import hashlib
import streamlit as st
from google import genai
from google.genai import types
from ddgs import DDGS
from pypdf import PdfReader
from streamlit_mic_recorder import mic_recorder


# ---------- PAGE CONFIG ----------

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------- SESSION STATE ----------

defaults = {
    "messages": [],
    "pdf_text": "",
    "uploaded_image": None,
    "uploaded_image_mime": None,
    "feature": "AI Tutor",
    "total_questions": 0,
    "last_audio_hash": "",
    "pdf_hash": "",
    "image_hash": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- THEME COLORS ----------

bg_color = "#111318"
sidebar_color = "#191B23"
text_color = "#F1F3F5"
secondary_color = "#A7AAB5"
card_color = "#20232D"
border_color = "#343744"
accent_color = "#A78BFA"


# ---------- GEMINI CONNECTION ----------

api_key = st.secrets.get(
    "GEMINI_API_KEY",
    os.getenv("GEMINI_API_KEY")
)

if not api_key:
    st.error(
        "Gemini API key is missing. "
        "Configure GEMINI_API_KEY in Streamlit Secrets."
    )
    st.stop()

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"


# ---------- INTERNET SEARCH ----------

def search_internet(query):
    try:
        results = DDGS().text(
            query,
            max_results=5
        )

        search_results = ""

        for result in results:
            search_results += (
                f"Title: {result.get('title', '')}\n"
                f"Description: {result.get('body', '')}\n"
                f"Link: {result.get('href', '')}\n\n"
            )

        return search_results or "No search results found."

    except Exception as e:
        return f"Search error: {e}"


# ---------- STUDY TOOLS ----------

features = {
    "AI Tutor":
        "Explain the topic step by step using simple English and examples.",

    "Notes Summarizer":
        "Summarize the notes with an overview, important points, definitions and exam preparation notes.",

    "Quiz Generator":
        "Create 5 multiple-choice questions with four options, correct answers and explanations.",

    "Flashcard Generator":
        "Create 10 question-and-answer flashcards for revision.",

    "Doubt Solver":
        "Solve the student's doubt step by step with a simple example.",

    "AI Study Planner":
        "Create a practical study timetable with learning goals, breaks and revision.",

    "Ask My PDF":
        "Answer questions using the uploaded PDF. If the answer is not in the document, clearly say so.",

    "Internet Search":
        "Use the latest internet search results to answer the question. Include useful source links.",

    "Coding Assistant":
        "Act as an expert programming tutor. Generate code in Python, Java, C and C++. Explain code line by line and debug errors.",

    "Image Understanding":
        "Analyze the uploaded image carefully. Explain diagrams, handwritten notes, mathematical problems and programming screenshots."
}


# ---------- CUSTOM DESIGN ----------

st.markdown(f"""
<style>

.stApp {{
    background: {bg_color};
    color: {text_color};
}}

[data-testid="stSidebar"] {{
    background: {sidebar_color};
    border-right: 1px solid {border_color};
}}

[data-testid="stSidebar"] {{
    display: block !important;
    visibility: visible !important;
}}

[data-testid="stSidebarCollapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
}}

.block-container {{
    max-width: 1050px;
    padding-top: 1rem;
    padding-bottom: 1rem;
}}

.studymate-title {{
    font-size: 34px;
    font-weight: 800;
    text-align: center;
    color: {accent_color};
    margin-bottom: 6px;
}}

.studymate-subtitle {{
    text-align: center;
    color: {secondary_color};
    font-size: 15px;
    margin-bottom: 20px;
}}

.feature-card {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 15px;
    padding: 15px;
    min-height: 95px;
    margin-bottom: 10px;
}}

.feature-card h4 {{
    color: {text_color};
    margin: 0 0 6px 0;
    font-size: 16px;
}}

.feature-card p {{
    color: {secondary_color};
    margin: 0;
    font-size: 13px;
}}

.stChatMessage {{
    border-radius: 15px;
    border: 1px solid {border_color};
    background: {card_color};
    margin-bottom: 10px;
}}

[data-testid="stSidebar"] h2 {{
    color: {accent_color};
    font-size: 24px;
    font-weight: 800;
}}

[data-testid="stSidebar"] h3 {{
    color: {text_color};
    font-size: 17px;
}}

[data-testid="stSidebar"] [data-testid="stMetric"] {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 10px;
}}

div.stButton > button {{
    border-radius: 12px;
    border: 1px solid {border_color};
    background: {card_color};
    color: {text_color};
    min-height: 42px;
}}

.stTextInput input {{
    background: {card_color};
    color: {text_color};
    border-color: {border_color};
    border-radius: 14px;
    min-height: 44px;
}}

.stSelectbox label,
.stRadio label {{
    color: {text_color};
}}

.stSpinner > div {{
    border-top-color: {accent_color};
}}

/* Composer layout */

.st-key-composer {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 18px;
    padding: 8px;
    margin-top: 12px;
}}

.st-key-composer [data-testid="stHorizontalBlock"] {{
    align-items: center;
    flex-wrap: nowrap !important;
    gap: 6px !important;
}}

.st-key-composer [data-testid="stTextInput"] input {{
    border-radius: 14px;
    background: {bg_color};
}}

.st-key-composer [data-testid="stTextInput"] label {{
    display: none;
}}

.st-key-composer div.stButton > button {{
    min-height: 44px;
    border-radius: 14px;
}}

/* Hide unnecessary Streamlit controls */

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

[data-testid="stToolbar"] {{
    visibility: hidden;
    height: 0;
}}

[data-testid="stStatusWidget"] {{
    display: none !important;
}}

/* Mobile design */

@media screen and (max-width: 768px) {{

    .block-container {{
        padding: 0.6rem 0.65rem 0.8rem 0.65rem !important;
        max-width: 100% !important;
    }}

    .studymate-title {{
        font-size: 25px !important;
        margin-bottom: 5px !important;
    }}

    .studymate-subtitle {{
        font-size: 13px !important;
        margin-bottom: 12px !important;
    }}

    .feature-card {{
        min-height: 75px !important;
        padding: 11px !important;
        margin-bottom: 7px !important;
        border-radius: 12px !important;
    }}

    .feature-card h4 {{
        font-size: 14px !important;
    }}

    .feature-card p {{
        font-size: 11px !important;
        line-height: 1.35 !important;
    }}

    .stChatMessage {{
        padding: 9px !important;
        border-radius: 12px !important;
    }}

    h1 {{
        font-size: 23px !important;
    }}

    h2 {{
        font-size: 20px !important;
    }}

    h3 {{
        font-size: 17px !important;
    }}

    .st-key-composer {{
        padding: 5px !important;
        margin-top: 8px !important;
    }}

    .st-key-composer [data-testid="stHorizontalBlock"] {{
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }}

    .st-key-composer [data-testid="stTextInput"] input {{
        font-size: 14px !important;
        min-width: 0 !important;
    }}

    .st-key-composer div.stButton > button {{
        min-height: 42px !important;
        padding: 0 7px !important;
        font-size: 16px !important;
    }}

    [data-testid="stSidebar"] {{
        min-width: 0 !important;
    }}

}}

</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------

with st.sidebar:

    st.markdown("## 📚 StudyMate AI")
    st.caption("Your personal learning companion")
    st.divider()

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.uploaded_image = None
        st.session_state.uploaded_image_mime = None
        st.session_state.last_audio_hash = ""
        st.rerun()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.total_questions = 0
        st.session_state.last_audio_hash = ""
        st.rerun()

    st.divider()

    st.markdown("### 💬 Chat History")

    if st.session_state.messages:

        st.caption("Current conversation")

        user_questions = [
            message["content"]
            for message in st.session_state.messages
            if message["role"] == "user"
        ]

        for index, question in enumerate(user_questions[-5:], 1):
            st.caption(f"{index}. {question[:60]}")

    else:
        st.caption("No previous conversations yet.")

    st.divider()

    st.markdown("### 📊 Learning Dashboard")

    st.metric(
        "Total Questions Asked",
        st.session_state.total_questions
    )

    st.metric(
        "Messages in Chat",
        len(st.session_state.messages)
    )

    if st.session_state.messages:

        chat_text = ""

        for message in st.session_state.messages:
            chat_text += (
                f"{message['role'].upper()}:\n"
                f"{message['content']}\n\n"
            )

        st.download_button(
            label="📥 Download Chat",
            data=chat_text,
            file_name="StudyMate_Chat.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.divider()

    st.markdown("### 📚 Study Tools")

    selected_feature = st.radio(
        "Choose a learning mode",
        list(features.keys()),
        index=list(features.keys()).index(
            st.session_state.feature
        )
    )

    st.session_state.feature = selected_feature

    st.divider()

    st.markdown("### About")
    st.caption("Study smarter with AI-powered learning tools.")
    st.caption("Powered by Google Gemini")


# ---------- MAIN PAGE ----------

st.markdown(
    f"📚 **StudyMate AI** / {st.session_state.feature}"
)

if not st.session_state.messages:

    st.markdown("""
    <div class="studymate-title">
        Welcome to StudyMate AI ✨
    </div>

    <div class="studymate-subtitle">
        Your personal AI learning companion.
        What would you like to learn today?
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI Tutor</h4>
            <p>Learn difficult concepts with simple explanations.</p>
        </div>

        <div class="feature-card">
            <h4>📝 Notes Summarizer</h4>
            <p>Turn lengthy notes into easy study materials.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>💻 Coding Assistant</h4>
            <p>Understand programming and solve coding doubts.</p>
        </div>

        <div class="feature-card">
            <h4>🧠 Quiz Generator</h4>
            <p>Test your knowledge with AI-generated quizzes.</p>
        </div>
        """, unsafe_allow_html=True)

    st.caption("Start by typing your question below 👇")


# ---------- DISPLAY CHAT HISTORY ----------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------- MESSAGE COMPOSER ----------

typed_input = None
audio_recording = None

with st.container(key="composer"):

    col_attach, col_message, col_mic = st.columns(
        [1, 8, 1],
        gap="small",
        vertical_alignment="center"
    )

    # ATTACHMENT MENU

    with col_attach:

        with st.popover("＋", use_container_width=True):

            st.markdown("### Attach files")

            uploaded_pdf = st.file_uploader(
                "📄 Upload PDF",
                type=["pdf"],
                key="composer_pdf"
            )

            if uploaded_pdf:

                current_pdf_hash = hashlib.sha256(
                    uploaded_pdf.getvalue()
                ).hexdigest()

                if current_pdf_hash != st.session_state.pdf_hash:

                    try:
                        reader = PdfReader(uploaded_pdf)

                        pdf_text = ""

                        for page in reader.pages:
                            pdf_text += page.extract_text() or ""

                        st.session_state.pdf_text = pdf_text
                        st.session_state.pdf_hash = current_pdf_hash

                        st.success(
                            f"PDF attached: {len(reader.pages)} pages"
                        )

                    except Exception as e:
                        st.error(f"PDF error: {e}")

            uploaded_image = st.file_uploader(
                "🖼️ Upload Image",
                type=["png", "jpg", "jpeg"],
                key="composer_image"
            )

            if uploaded_image:

                current_image_hash = hashlib.sha256(
                    uploaded_image.getvalue()
                ).hexdigest()

                if current_image_hash != st.session_state.image_hash:

                    st.session_state.uploaded_image = (
                        uploaded_image.getvalue()
                    )

                    st.session_state.uploaded_image_mime = (
                        uploaded_image.type
                    )

                    st.session_state.image_hash = current_image_hash

                st.success("Image attached successfully!")

            if st.session_state.pdf_text:
                st.caption("📄 PDF ready")

            if st.session_state.uploaded_image:
                st.caption("🖼️ Image ready")

    # TEXT INPUT AND SEND BUTTON

    with col_message:

        with st.form("message_form", clear_on_submit=True):

            input_col, send_col = st.columns(
                [8, 1],
                gap="small",
                vertical_alignment="center"
            )

            with input_col:
                typed_input = st.text_input(
                    "Message",
                    placeholder="Message StudyMate AI...",
                    label_visibility="collapsed"
                )

            with send_col:
                send_clicked = st.form_submit_button(
                    "➤",
                    use_container_width=True
                )

    # MICROPHONE

    with col_mic:

        audio_recording = mic_recorder(
            start_prompt="🎤",
            stop_prompt="⏹️",
            just_once=True,
            use_container_width=True,
            key="voice_recorder"
        )


# ---------- VOICE TRANSCRIPTION ----------

user_input = None

if send_clicked and typed_input:
    user_input = typed_input.strip()

if audio_recording:

    audio_bytes = audio_recording.get("bytes")

    if audio_bytes:

        audio_hash = hashlib.sha256(
            audio_bytes
        ).hexdigest()

        if audio_hash != st.session_state.last_audio_hash:

            with st.spinner("Converting your voice into text..."):

                try:

                    audio_part = types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav"
                    )

                    transcription = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=[
                            "Transcribe the spoken words exactly. Return only the transcription.",
                            audio_part
                        ]
                    )

                    voice_text = (
                        transcription.text or ""
                    ).strip()

                    st.session_state.last_audio_hash = audio_hash

                    if voice_text:
                        user_input = voice_text
                        st.info(f"Voice transcription: {voice_text}")

                except Exception as e:
                    st.error(f"Voice transcription error: {e}")


# ---------- PROCESS QUESTION ----------

if user_input:

    previous_messages = st.session_state.messages[-10:]

    history_context = ""

    for message in previous_messages:
        history_context += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n"
        )

    st.session_state.total_questions += 1

    search_results = ""

    if st.session_state.feature == "Internet Search":

        with st.spinner("Searching the internet..."):
            search_results = search_internet(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner("StudyMate AI is thinking..."):

            prompt = f"""
You are StudyMate AI, a friendly and knowledgeable personal study tutor.

Selected learning mode: {st.session_state.feature}

Programming language: {programming_language if 'programming_language' in globals() else 'Python'}

Instructions:
{features[st.session_state.feature]}

Use simple English, clear headings and practical examples.
Be accurate and helpful.

Previous conversation:
{history_context}

Uploaded PDF content:
{st.session_state.pdf_text[:30000]}

Internet search results:
{search_results}

Student's message:
{user_input}
"""

            try:

                request_contents = [prompt]

                if st.session_state.feature == "Image Understanding":

                    if st.session_state.uploaded_image is None:

                        st.warning(
                            "Please attach an image using the + button."
                        )
                        st.stop()

                    image_part = types.Part.from_bytes(
                        data=st.session_state.uploaded_image,
                        mime_type=st.session_state.uploaded_image_mime
                    )

                    request_contents.append(image_part)

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=request_contents
                )

                answer = (
                    response.text or
                    "No response was generated."
                )

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                st.error(f"Something went wrong: {e}")
