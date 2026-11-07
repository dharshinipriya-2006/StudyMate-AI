# 📚 StudyMate AI – Your Personal AI Study Assistant

StudyMate AI is an AI-powered learning assistant designed to help students learn smarter and prepare effectively for exams. It uses Google Gemini AI and Streamlit to provide interactive learning tools in one application.

## 🚀 Live Demo

studymate-ai-hg7bg3dhd6krxonyd3pu42

## ✨ Features

- 🤖 **AI Tutor** – Explains complex topics in simple English with examples.
- 📝 **Notes Summarizer** – Converts lengthy study notes into easy summaries.
- 🧠 **Quiz Generator** – Generates multiple-choice questions for practice.
- 📇 **Flashcard Generator** – Creates flashcards for quick revision.
- 💡 **Doubt Solver** – Provides step-by-step explanations.
- 📅 **AI Study Planner** – Creates personalized study schedules.
- 📄 **PDF Upload & Q&A** – Upload study materials and ask questions about them.
- 🌐 **Internet Search** – Retrieves online information to answer questions.
- 💻 **Coding Assistant** – Supports Python, Java, C and C++ programming.
- 🖼️ **Image Understanding** – Analyzes images, diagrams and screenshots.
- 🎤 **Voice Assistant** – Accepts voice-based questions.
- 💬 **Chat History** – Displays the current conversation.
- 📊 **Learning Dashboard** – Tracks questions asked during the session.
- 📥 **Download Chat** – Exports conversations as a text file.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Streamlit | Web application framework |
| Google Gemini API | AI-powered responses |
| Google GenAI SDK | Gemini integration |
| PyPDF | PDF text extraction |
| DuckDuckGo Search | Internet search |
| GitHub | Version control and source code hosting |
| Streamlit Community Cloud | Application deployment |

## 🏗️ Project Architecture

1. User interacts with the Streamlit interface.
2. The application receives text, PDF, image or voice input.
3. Python processes the input.
4. Google Gemini generates AI-powered responses.
5. StudyMate AI displays the response through the web interface.

## 📂 Project Structure

```text
StudyMate-AI/
│
├── app.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/dharshinipriya-2006/StudyMate-AI.git
```

### 2. Navigate to the project folder

```bash
cd StudyMate-AI
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key

Create a `.streamlit/secrets.toml` file:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Never upload your API key to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

## 📦 Requirements

```text
streamlit>=1.40.0
google-genai
pypdf
ddgs
```

## 🎯 Project Objective

The main objective of StudyMate AI is to make learning easier, faster and more interactive by integrating artificial intelligence into everyday student activities.

## 🔮 Future Enhancements

- Persistent conversation storage
- User authentication
- Personalized learning recommendations
- Progress tracking across sessions

## 👩‍💻 Developer

**Dharshini Priya**

B.E. Computer Science and Engineering

**Areas of Interest:** Artificial Intelligence, Machine Learning, Cloud Computing and Software Development.

## 📄 License

This project is created for educational and portfolio purposes.
