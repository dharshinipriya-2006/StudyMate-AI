
import streamlit as st
import os
from google import genai

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="centered"
)

st.title("📚 StudyMate AI")
st.subheader("Your Personal AI Study Assistant")

st.write("Learn smarter with your AI-powered study companion!")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.5-flash-lite"

features = {
    "AI Tutor": "Explain the topic step by step with examples.",
    "Notes Summarizer": "Summarize notes using simple English and key points.",
    "Quiz Generator": "Create 5 multiple-choice questions with four options, answers and explanations.",
    "Flashcard Generator": "Create 10 question-and-answer flashcards.",
    "Doubt Solver": "Solve the doubt with a step-by-step explanation.",
    "AI Study Planner": "Create a practical study timetable with breaks and revision."
}

feature = st.selectbox("Choose a feature", list(features.keys()))

user_input = st.text_area(
    "Enter your topic, notes, or question:",
    height=150
)

if st.button("Generate", type="primary"):

    if not user_input.strip():
        st.warning("Please enter some content.")

    else:
        prompt = f"""
        You are StudyMate AI, a friendly personal study assistant.
        Feature: {feature}
        Instructions: {features[feature]}
        Use simple English and clear formatting.
        Student input: {user_input}
        """

        try:
            with st.spinner("StudyMate AI is thinking..."):
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt
                )

            st.success("Your result is ready!")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Error: {e}")
