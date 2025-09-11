# utils/rag_utils.py
import os
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Note: The loader below requires the 'unstructured' package, not PyPDF2.
# The fix has been applied in requirements.txt.
from langchain_community.document_loaders import UnstructuredFileLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from models.embeddings import get_embedding_fn
from config.config import VECTOR_STORE_DIR

os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

def load_documents_from_file(path: str) -> List[Document]:
    try:
        loader = UnstructuredFileLoader(path)
        docs = loader.load()
        return docs
    except Exception:
        try:
            loader = TextLoader(path, encoding="utf-8")
            return loader.load()
        except Exception as e:
            print(f"[rag_utils] failed to load {path}: {e}")
            return []

def chunk_documents(docs: List[Document], chunk_size=1000, chunk_overlap=200) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)

def build_vector_store(docs: List[Document], persist_directory: Optional[str] = VECTOR_STORE_DIR):
    emb = get_embedding_fn()
    if not docs:
        raise ValueError("No documents to index.")
    chunks = chunk_documents(docs)
    if not chunks:
        raise ValueError("No chunks produced.")
    try:
        # Allow FAISS to load from a local directory using the correct class method
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            db = FAISS.load_local(persist_directory, emb, allow_dangerous_deserialization=True)
            db.add_documents(chunks)
            db.save_local(persist_directory)
            return db
        else:
            db = FAISS.from_documents(chunks, emb)
            db.save_local(persist_directory)
            return db
    except Exception as e:
        raise RuntimeError(f"Failed building vector store: {e}")

def query_vector_store(query: str, k=4, persist_directory: Optional[str] = VECTOR_STORE_DIR):
    emb = get_embedding_fn()
    try:
        # Allow FAISS to load from a local directory using the correct class method
        db = FAISS.load_local(persist_directory, emb, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"[rag_utils] Failed to load vectorstore: {e}")
        return []
    docs_and_scores = db.similarity_search_with_score(query, k=k)
    return docs_and_scores
