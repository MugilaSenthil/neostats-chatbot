# models/embeddings.py
from config.config import OPENAI_API_KEY, EMBEDDING_MODEL_NAME

def get_embedding_fn():
    try:
        if OPENAI_API_KEY:
            # FIX: Updated import to use langchain_openai
            from langchain_openai import OpenAIEmbeddings
            emb = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL_NAME)
            return emb
    except Exception as e:
        print(f"[embeddings] OpenAIEmbeddings init failed: {e}")

    try:
        # FIX: Updated import to use langchain_community
        from langchain_community.embeddings import HuggingFaceEmbeddings
        emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return emb
    except Exception as e:
        print(f"[embeddings] HuggingFaceEmbeddings init failed: {e}")

    raise RuntimeError("No embedding backend available. Set OPENAI_API_KEY or install sentence-transformers.")