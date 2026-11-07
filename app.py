
import os
import streamlit as st
from google import genai
from google.genai import types
from ddgs import DDGS
from pypdf import PdfReader


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------- INTERNET SEARCH ----------
def search_internet(query):
    try:
        results = DDGS().text(query, max_results=5)

        search_results = ""

        for result in results:
            search_results += (
                f"Title: {result.get('title', '')}\n"
                f"Description: {result.get('body', '')}\n"
                f"Link: {result.get('href', '')}\n\n"
            )

        return search_results or "No search results found."

    except Exception as e:
        return f"Search error: {str(e)}"


# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: #111318;
    color: #E8EAED;
}
[data-testid="stSidebar"] {
    background: #191B23;
    border-right: 1px solid #30323B;
}
.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}
.welcome {
    text-align: center;
    padding-top: 90px;
    padding-bottom: 30px;
}
.welcome h1 {
    font-size: 42px;
    font-weight: 700;
}
.welcome p {
    color: #A7AAB5;
    font-size: 17px;
}
.stChatMessage {
    border-radius: 15px;
    border: 1px solid #30323B;
}
.stChatInput {
    border-radius: 18px;
}
div.stButton > button {
    border-radius: 12px;
    border: 1px solid #414450;
}
</style>
""", unsafe_allow_html=True)


# ---------- GEMINI CONNECTION ----------
api_key = st.secrets.get(
    "GEMINI_API_KEY",
    os.getenv("GEMINI_API_KEY")
)

if not api_key:
    st.error("Gemini API key is missing. Configure it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.5-flash-lite"


# ---------- STUDY TOOLS ----------
features = {
    "AI Tutor": "Explain the topic step by step using simple English and examples. Ask one practice question.",

    "Notes Summarizer": "Summarize the notes with an overview, important points, definitions and exam preparation notes.",

    "Quiz Generator": "Create 5 multiple-choice questions with four options, correct answers and explanations.",

    "Flashcard Generator": "Create 10 question-and-answer flashcards for revision.",

    "Doubt Solver": "Solve the student's doubt step by step with a simple example.",

    "AI Study Planner": "Create a practical study timetable with learning goals, breaks and revision.",

    "Ask My PDF": "Answer questions using the uploaded PDF document. If the answer is not in the document, clearly say so.",

    "Internet Search": "Use the latest internet search results to answer the student's question. Include useful source links and explain the information in simple English.",

    "Coding Assistant": "Act as an expert programming tutor. Generate correct code in Python, Java, C, and C++. Explain code line by line, debug errors, identify mistakes, and suggest optimized solutions. Use beginner-friendly explanations.",

    "Image Understanding": "Analyze the uploaded image carefully. Explain diagrams, handwritten notes, mathematical problems, flowcharts, and programming screenshots in simple English."
}


# ---------- SESSION STATE ----------
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "feature" not in st.session_state:
    st.session_state.feature = "AI Tutor"


# ---------- SIDEBAR ----------
with st.sidebar:

    st.markdown("## 📚 StudyMate AI")
    st.caption("Your personal learning companion")

    st.divider()

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.rerun()

    st.markdown("### 💬 Chat History")

    if st.session_state.messages:
        st.caption("Current conversation")
        st.write(f"Messages: {len(st.session_state.messages)}")
    else:
        st.caption("No previous conversations yet.")

    st.divider()
    
    st.markdown("### Study Tools")

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
        type=["pdf"]
    )

    if uploaded_pdf:
        try:
            reader = PdfReader(uploaded_pdf)

            pdf_text = ""

            for page in reader.pages:
                pdf_text += page.extract_text() or ""

            st.session_state.pdf_text = pdf_text

            st.success("PDF uploaded successfully!")
            st.caption(f"Pages: {len(reader.pages)}")

        except Exception as e:
            st.error(f"PDF error: {e}")

    # IMAGE UPLOAD
    st.markdown("### 🖼️ Upload an Image")

    uploaded_image = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg"]
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
    st.caption("Study smarter with AI-powered learning tools.")
    st.caption("Powered by Google Gemini")


# ---------- MAIN CHAT ----------
st.markdown(
    f"<p style='color:#A7AAB5'>📚 StudyMate AI / {st.session_state.feature}</p>",
    unsafe_allow_html=True
)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <h1>👋 Hello, Student!</h1>
        <p>What would you like to learn today?</p>
        <p>Ask questions, summarize notes, create quizzes or plan your studies.</p>
    </div>
    """, unsafe_allow_html=True)


# ---------- DISPLAY CHAT HISTORY ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------- CHAT INPUT ----------
user_input = st.chat_input("Message StudyMate AI...")

voice_input = st.audio_input("🎤 Record your question")

if voice_input:
    with st.spinner("Converting your voice into text..."):
        try:
            audio_part = types.Part.from_bytes(
                data=voice_input.getvalue(),
                mime_type=voice_input.type
            )

            transcription = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    "Transcribe the spoken words exactly. Return only the transcription.",
                    audio_part
                ]
            )

            user_input = transcription.text

        except Exception as e:
            st.error(f"Voice transcription error: {e}")
            st.stop()

    # SEARCH INTERNET
    search_results = ""

    if st.session_state.feature == "Internet Search":
        with st.spinner("Searching the internet..."):
            search_results = search_internet(user_input)

    # SAVE USER MESSAGE
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # GEMINI RESPONSE
    with st.chat_message("assistant"):

        with st.spinner("StudyMate AI is thinking..."):

            prompt = f"""
You are StudyMate AI, a friendly and knowledgeable personal study tutor.

Selected learning mode: {st.session_state.feature}

Programming language: {programming_language}

Instructions:
{features[st.session_state.feature]}

Use simple English, clear headings and practical examples.
Be accurate and helpful.

If the user asks a general follow-up,
answer naturally while respecting the selected learning mode.

Uploaded PDF content:
{st.session_state.get("pdf_text", "")[:30000]}

Internet search results:
{search_results}

Previous conversation:
{st.session_state.messages[-10:]}

Student's message:
{user_input}
"""

            try:

                request_contents = [prompt]

                # IMAGE UNDERSTANDING
                if st.session_state.feature == "Image Understanding":

                    if "uploaded_image" in st.session_state:

                        image_part = types.Part.from_bytes(
                            data=st.session_state.uploaded_image.getvalue(),
                            mime_type=st.session_state.uploaded_image.type
                        )

                        request_contents.append(image_part)

                    else:
                        st.warning(
                            "Please upload an image in the sidebar first."
                        )
                        st.stop()

                # GENERATE GEMINI RESPONSE
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=request_contents
                )

                answer = response.text or "No response was generated."

                st.markdown(answer)

                # SAVE ASSISTANT MESSAGE
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                st.error(f"Something went wrong: {e}")
