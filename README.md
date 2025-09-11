NeoStats AI Engineer Assessment: The Chatbot Blueprint
This project is a submission for the NeoStats AI Engineer Internship assessment. The goal was to take a foundational chatbot template and build a complete, functional, and specialized AI solution by defining a unique problem and implementing the necessary features to solve it.

Chosen Use Case: The Intelligent Document Analyzer
Problem: Important documents, from business reports to academic papers, are often dense and time-consuming to read. Extracting specific information or understanding complex topics quickly is a significant challenge.

Solution: This chatbot functions as an intelligent document analysis assistant. A user can upload any text-based document (PDF, DOCX, TXT), which is then indexed for Retrieval-Augmented Generation (RAG). The user can then ask specific, complex questions about the document's contents, and the chatbot will provide answers in plain, easy-to-understand language. For ambiguous terms or concepts that require broader context, the chatbot can automatically use a web search to find definitions or relevant external information, enriching its answers.

Live Demo
You can access the live, deployed version of this application here:

[Streamlit Cloud app](https://neostats-chatbot.streamlit.app/)

Core Features Implemented
This chatbot is equipped with the following features as required by the assessment:

📄 RAG Integration: The chatbot can ingest local documents (PDF, DOCX, TXT), create a vector embedding, and use this knowledge base to answer user questions with high accuracy.

🌐 Live Web Search: When the LLM lacks knowledge or the user explicitly asks, the bot can perform real-time web searches using SerpApi or Google Custom Search to provide up-to-date information.

💬 Dual Response Modes: Users can switch between:

Concise Mode: For quick, summarized answers.

Detailed Mode: For in-depth, comprehensive responses.

🧠 Persistent Memory: The application uses an SQLite database to save and load chat sessions, allowing users to continue previous conversations.

🎤 Voice I/O:

Voice-to-Text: Users can upload audio files (WAV, MP3, etc.), which are transcribed using OpenAI's Whisper API.

Text-to-Speech: The chatbot's responses can be converted into audible speech.

🤖 Multi-LLM Support: The application is configured to seamlessly switch between different LLM providers (OpenAI and Groq) based on user selection.

📊 Basic Analytics: A simple dashboard visualizes chat statistics, such as messages per day and message length distribution.

Tech Stack
Backend: Python

UI Framework: Streamlit

AI/LLM Framework: LangChain

Vector Store: FAISS (for in-memory RAG)

LLM Providers: OpenAI, Groq

Web Search: SerpApi, Google Custom Search API

Database: SQLite (for chat history)

Project Structure
The project follows a modular structure for maintainability and scalability:

├── .github/workflows/      # CI/CD configuration
├── config/                 # API keys and settings
├── models/                 # LLM and embedding model logic
├── utils/                  # Helper functions (RAG, search, memory)
├── .env                    # (Local) Environment variables (ignored by git)
├── .gitignore              # Files and folders to ignore
├── app.py                  # Main Streamlit application
├── Dockerfile              # Containerization setup
├── requirements.txt        # Python dependencies
└── README.md               # This file

Local Setup and Installation
To run this project on your local machine, follow these steps:

1. Clone the Repository

git clone [https://github.com/MugilaSenthil/AI_UseCase.git](https://github.com/MugilaSenthil/neostats-chatbot)
cd AI_UseCase

2. Create and Activate a Virtual Environment (Recommended)

For Windows
python -m venv .venv
.\.venv\Scripts\activate

For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Set Up Environment Variables

Create a file named .env in the root of the project directory.

Add your secret API keys to this file. This file is included in .gitignore and will not be committed.

.env file
OPENAI_API_KEY="sk-proj-..."
GROQ_API_KEY="gsk_..."
SERPAPI_KEY="..."
Or GOOGLE_CSE_KEY="..." and GOOGLE_CX="..."

5. Run the Application

streamlit run app.py

The application should now be running and accessible in your web browser at http://localhost:8501.

Presentation Deck
The final presentation summarizing the project's objectives, approach, and outcomes can be found here:
[PPT](https://www.canva.com/design/DAGymrHURmM/STP5E7S8NQ32kSzWRt2ZgQ/edit?utm_content=DAGymrHURmM&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)



