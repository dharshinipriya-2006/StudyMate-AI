
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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "feature" not in st.session_state:
    st.session_state.feature = "AI Tutor"

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = ""

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"


# ---------- THEME COLORS ----------

if st.session_state.theme == "Dark":

    bg_color = "#111318"
    sidebar_color = "#191B23"
    text_color = "#F1F3F5"
    secondary_color = "#A7AAB5"
    card_color = "#20232D"
    border_color = "#343744"
    accent_color = "#A78BFA"

else:

    bg_color = "#F7F8FC"
    sidebar_color = "#FFFFFF"
    text_color = "#202333"
    secondary_color = "#687086"
    card_color = "#FFFFFF"
    border_color = "#E3E5EF"
    accent_color = "#7654D6"


# ---------- GEMINI CONNECTION ----------

api_key = st.secrets.get(
    "GEMINI_API_KEY",
    os.getenv("GEMINI_API_KEY")
)

if not api_key:
    st.error(
        "Gemini API key is missing. "
        "Configure it in Streamlit Secrets."
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


# ---------- MAIN DESIGN ----------

st.markdown(f"""
<style>

.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}

[data-testid="stSidebar"] {{
    background-color: {sidebar_color};
    border-right: 1px solid {border_color};
}}

.block-container {{
    max-width: 1050px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}}

.studymate-title {{
    font-size: 36px;
    font-weight: 800;
    text-align: center;
    color: {accent_color};
    margin-bottom: 8px;
}}

.studymate-subtitle {{
    text-align: center;
    color: {secondary_color};
    font-size: 16px;
    margin-bottom: 35px;
}}

.feature-card {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 20px;
    min-height: 115px;
    margin-bottom: 14px;
    transition: 0.2s ease;
}}

.feature-card:hover {{
    border-color: {accent_color};
}}

.feature-card h4 {{
    color: {text_color};
    margin: 0 0 8px 0;
    font-size: 17px;
}}

.feature-card p {{
    color: {secondary_color};
    margin: 0;
    font-size: 13px;
}}

.stChatMessage {{
    border-radius: 16px;
    border: 1px solid {border_color};
    background-color: {card_color};
    margin-bottom: 12px;
}}

[data-testid="stChatInput"] {{
    border: 1px solid {border_color};
    border-radius: 18px;
    background-color: {card_color};
}}

[data-testid="stChatInput"] textarea {{
    color: {text_color};
    font-size: 15px;
}}

[data-testid="stSidebar"] h2 {{
    color: {accent_color};
    font-size: 25px;
    font-weight: 800;
}}

[data-testid="stSidebar"] h3 {{
    color: {text_color};
    font-size: 17px;
    font-weight: 700;
}}

[data-testid="stSidebar"] [data-testid="stMetric"] {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 12px;
}}

[data-testid="stSidebar"] [data-testid="stFileUploader"] {{
    background: {card_color};
    border: 1px dashed {border_color};
    border-radius: 12px;
    padding: 8px;
}}

div.stButton > button {{
    border-radius: 12px;
    border: 1px solid {border_color};
    background-color: {card_color};
    color: {text_color};
}}

.stSelectbox label,
.stRadio label {{
    color: {text_color};
}}

.stSpinner > div {{
    border-top-color: {accent_color};
}}

/* ---------- MOBILE RESPONSIVE DESIGN ---------- */

@media screen and (max-width: 768px) {{

    .block-container {{
        padding-top: 0.8rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }}

    .studymate-title {{
        font-size: 27px !important;
        margin-bottom: 5px !important;
    }}

    .studymate-subtitle {{
        font-size: 14px !important;
        margin-bottom: 18px !important;
    }}

    .feature-card {{
        min-height: auto !important;
        padding: 14px !important;
        margin-bottom: 9px !important;
        border-radius: 13px !important;
    }}

    .feature-card h4 {{
        font-size: 15px !important;
    }}

    .feature-card p {{
        font-size: 12px !important;
    }}

    .stChatMessage {{
        padding: 10px !important;
        border-radius: 13px !important;
    }}

    [data-testid="stChatInput"] {{
        width: 100% !important;
        margin-bottom: 5px !important;
    }}

    [data-testid="stSidebar"] {{
        min-width: 0 !important;
    }}

    h1 {{ font-size: 25px !important; }}
    h2 {{ font-size: 21px !important; }}
    h3 {{ font-size: 18px !important; }}

}}

</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------

with st.sidebar:

    st.markdown("## 📚 StudyMate AI")

    st.caption("Your personal learning companion")

    st.divider()

    # THEME SELECTOR

    st.markdown("### 🎨 Appearance")

    selected_theme = st.selectbox(
        "Choose theme",
        ["Dark", "Light"],
        index=["Dark", "Light"].index(
            st.session_state.theme
        )
    )

    if selected_theme != st.session_state.theme:

        st.session_state.theme = selected_theme
        st.rerun()

    st.divider()

    # NEW CHAT

    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.last_audio_hash = ""

        st.rerun()

    # CLEAR HISTORY

    if st.button(
        "🗑️ Clear Chat History",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.total_questions = 0
        st.session_state.last_audio_hash = ""

        st.rerun()

    st.divider()

    # CHAT HISTORY

    st.markdown("### 💬 Chat History")

    if st.session_state.messages:

        st.caption("Current conversation")

        st.write(
            f"Messages: {len(st.session_state.messages)}"
        )

        user_questions = [
            message["content"]
            for message in st.session_state.messages
            if message["role"] == "user"
        ]

        for index, question in enumerate(
            user_questions[-5:],
            1
        ):

            st.caption(
                f"{index}. {question[:60]}"
            )

    else:

        st.caption("No previous conversations yet.")

    st.divider()

    # LEARNING DASHBOARD

    st.markdown("### 📊 Learning Dashboard")

    st.metric(
        "Total Questions Asked",
        st.session_state.total_questions
    )

    st.metric(
        "Messages in Chat",
        len(st.session_state.messages)
    )

    # DOWNLOAD CHAT

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

    # STUDY TOOLS

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

    # PDF UPLOAD

    st.markdown("### 📄 Upload Study Notes")

    uploaded_pdf = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        key="pdf_uploader"
    )

    if uploaded_pdf:

        try:

            reader = PdfReader(uploaded_pdf)

            pdf_text = ""

            for page in reader.pages:

                pdf_text += page.extract_text() or ""

            st.session_state.pdf_text = pdf_text

            st.success("PDF uploaded successfully!")

            st.caption(
                f"Pages: {len(reader.pages)}"
            )

        except Exception as e:

            st.error(f"PDF error: {e}")

    # IMAGE UPLOAD

    st.markdown("### 🖼️ Upload an Image")

    uploaded_image = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg"],
        key="image_uploader"
    )

    if uploaded_image:

        st.session_state.uploaded_image = uploaded_image

        st.success("Image uploaded successfully!")

    # PROGRAMMING LANGUAGE

    st.markdown("### 💻 Programming Language")

    programming_language = st.selectbox(
        "Choose a language",
        ["Python", "Java", "C", "C++"]
    )

    st.divider()

    st.markdown("### About")

    st.caption(
        "Study smarter with AI-powered learning tools."
    )

    st.caption(
        "Powered by Google Gemini"
    )


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

    st.markdown(
        f"""
        <p style="
            text-align:center;
            color:{secondary_color};
            margin-top:25px;
        ">
            Start by typing your question below 👇
        </p>
        """,
        unsafe_allow_html=True
    )


# ---------- DISPLAY CHAT HISTORY ----------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ---------- CHAT INPUT WITH VOICE ----------

col_input, col_mic = st.columns(
    [12, 1],
    vertical_alignment="bottom",
    gap="small"
)

with col_input:

    typed_input = st.chat_input(
        "Message StudyMate AI..."
    )

with col_mic:

    audio_recording = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True,
        key="voice_recorder"
    )

user_input = typed_input

# ---------- VOICE TRANSCRIPTION ----------

if audio_recording and typed_input is None:

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

                    user_input = (
                        transcription.text or ""
                    ).strip()

                    st.session_state.last_audio_hash = audio_hash

                    if user_input:
                        st.info(
                            f"Voice transcription: {user_input}"
                        )

                except Exception as e:

                    st.error(
                        f"Voice transcription error: {e}"
                    )

# ---------- PROCESS QUESTION ----------

if user_input:

    # PREVIOUS CONVERSATION CONTEXT

    previous_messages = st.session_state.messages[-10:]

    history_context = ""

    for message in previous_messages:

        history_context += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n"
        )

    # COUNT QUESTION

    st.session_state.total_questions += 1

    # INTERNET SEARCH

    search_results = ""

    if st.session_state.feature == "Internet Search":

        with st.spinner("Searching the internet..."):

            search_results = search_internet(
                user_input
            )

    # SAVE USER MESSAGE

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):

        st.markdown(user_input)

    # GEMINI RESPONSE

    with st.chat_message("assistant"):

        with st.spinner(
            "StudyMate AI is thinking..."
        ):

            prompt = f"""
You are StudyMate AI, a friendly and knowledgeable personal study tutor.

Selected learning mode: {st.session_state.feature}

Programming language: {programming_language}

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

                # IMAGE UNDERSTANDING

                if st.session_state.feature == "Image Understanding":

                    if st.session_state.uploaded_image is not None:

                        image_part = types.Part.from_bytes(
                            data=st.session_state.uploaded_image.getvalue(),
                            mime_type=st.session_state.uploaded_image.type
                        )

                        request_contents.append(
                            image_part
                        )

                    else:

                        st.warning(
                            "Please upload an image in the sidebar first."
                        )

                        st.stop()

                # GEMINI RESPONSE

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=request_contents
                )

                answer = (
                    response.text or
                    "No response was generated."
                )

                st.markdown(answer)

                # SAVE ASSISTANT RESPONSE

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )


  
    
