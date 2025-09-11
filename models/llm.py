# models/llm.py
from typing import Optional
from config.config import OPENAI_API_KEY, GROQ_API_KEY

def get_chat_model(provider_preference: str = "auto"):
    provider_preference = provider_preference.lower()
    # Try OpenAI
    if provider_preference in ("openai", "auto") and OPENAI_API_KEY:
        try:
            # FIX: Updated import to use langchain_openai
            from langchain_openai import ChatOpenAI
            # default to a reliable model; change if needed
            chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.1)
            return chat
        except Exception as e:
            print(f"[llm] OpenAI init failed: {e}")

    # Try Groq
    if GROQ_API_KEY:
        try:
            from langchain_groq import ChatGroq
            groq = ChatGroq(api_key=GROQ_API_KEY, model="mixtral-8x7b-32768")
            return groq
        except Exception as e:
            print(f"[llm] Groq init failed: {e}")

    return None
