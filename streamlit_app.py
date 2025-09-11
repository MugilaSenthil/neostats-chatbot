# app.py
import streamlit as st
from config.config import VECTOR_STORE_DIR
from models.llm import get_chat_model
from utils.rag_utils import load_documents_from_file, build_vector_store, query_vector_store
from utils.web_search import web_search
from utils.memory import new_session_id, save_message, load_session_messages, dump_session_json, list_sessions, _conn
from utils.voice import transcribe_with_openai
from utils.voice_tts import synthesize_text_to_mp3

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="NeoStats Chatbot Blueprint", page_icon="🤖", layout="wide")
st.title("NeoStats — Chatbot Blueprint (RAG + Web Search + Memory + Voice)")

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.write("Environment keys (set in your system):")
    st.write("- OPENAI_API_KEY (for LLM/Embeddings/Whisper)")
    st.write("- GROQ_API_KEY (alternative LLM)")
    st.write("- SERPAPI_KEY or GOOGLE_CSE_KEY + GOOGLE_CX (optional for web search)")
    st.divider()
    mode = st.radio("Response mode", ["Concise", "Detailed"], index=0)
    provider = st.selectbox("LLM Provider", ["auto", "openai", "groq"])
    st.divider()
    if st.button("Clear vector store"):
        try:
            import shutil
            shutil.rmtree(VECTOR_STORE_DIR)
            os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
            st.success("Vector store cleared.")
        except Exception as e:
            st.error(f"Failed to clear vector store: {e}")

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_available" not in st.session_state:
    st.session_state.db_available = False
if "last_rag_index_time" not in st.session_state:
    st.session_state.last_rag_index_time = None
if "session_id" not in st.session_state:
    st.session_state.session_id = new_session_id()
if "persisted_messages_loaded" not in st.session_state:
    old = load_session_messages(st.session_state.session_id)
    if old:
        st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in old]
    st.session_state.persisted_messages_loaded = True

# Document upload & indexing
st.subheader("1) Upload & Index Documents for RAG")
uploaded_files = st.file_uploader("Upload files (PDF, DOCX, TXT)", accept_multiple_files=True)
if uploaded_files:
    st.write(f"{len(uploaded_files)} file(s) uploaded.")
    if st.button("Index uploaded files for RAG"):
        with st.spinner("Indexing documents... Please wait."):
            docs = []
            tmp_dir = "uploaded_docs"
            os.makedirs(tmp_dir, exist_ok=True)
            for f in uploaded_files:
                path = os.path.join(tmp_dir, f.name)
                with open(path, "wb") as out:
                    out.write(f.read())
                loaded = load_documents_from_file(path)
                docs.extend(loaded)
            if not docs:
                st.error("No documents loaded or failed to parse files.")
            else:
                try:
                    build_vector_store(docs)
                    st.session_state.db_available = True
                    st.session_state.last_rag_index_time = datetime.datetime.now().isoformat()
                    st.success("Indexed documents into vector store.")
                except Exception as e:
                    st.error(f"Indexing failed: {e}")

st.markdown("---")

# Chat area
st.subheader("2) Chat")
chat_col, tools_col = st.columns([3,1])

# Initialize LLM
chat_model = get_chat_model(provider_preference=provider)
if chat_model is None:
    st.warning("LLM not initialized. Set OPENAI_API_KEY or GROQ_API_KEY in env.")
else:
    st.success(f"LLM ready: {type(chat_model).__name__}")

# IMPROVEMENT: System prompt is now dynamically adjusted for concise/detailed mode.
base_system_prompt = "You are a helpful assistant. Use retrieved docs and web search when required."
if mode == "Concise":
    final_system_prompt = base_system_prompt + "\n\nYou must provide concise, short, and summarized replies."
else: # Detailed mode
    final_system_prompt = base_system_prompt + "\n\nYou must provide expanded, in-depth, and detailed responses."
system_prompt_input = st.text_area("System prompt", value=final_system_prompt, height=120)


use_rag = st.checkbox("Enable RAG retrieval", value=True)
use_web_search = st.checkbox("Allow web search (use 'web:' prefix)", value=False)

def llm_chat_response(messages):
    try:
        lmsgs = []
        if system_prompt_input:
            lmsgs.append(SystemMessage(content=system_prompt_input))
        for m in messages:
            if m["role"] == "user":
                lmsgs.append(HumanMessage(content=m["content"]))
            else:
                lmsgs.append(AIMessage(content=m["content"]))
        
        resp = chat_model.invoke(lmsgs)
        return getattr(resp, "content", str(resp))

    except Exception as e:
        return f"LLM error: {e}"

with chat_col:
    # Render existing messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # Voice STT uploader
    st.markdown("**Voice input (file)**")
    audio_file = st.file_uploader("Upload audio for transcription (wav/mp3/m4a/ogg)", type=["wav","mp3","m4a","ogg"])
    if audio_file:
        bytes_data = audio_file.read()
        st.info("Transcribing...")
        res = transcribe_with_openai(bytes_data, filename=audio_file.name)
        if res.get("error"):
            st.error("Transcription error: " + res["error"])
        else:
            transcript = res.get("text", "")
            st.success("Transcription complete:")
            st.write(transcript)
            if st.button("Send transcription as message"):
                st.session_state.messages.append({"role":"user","content":transcript})
                save_message(st.session_state.session_id, "user", transcript)
                st.rerun() # FIX: Replaced deprecated experimental_rerun

    user_input = st.chat_input("Type a message or use voice upload above")
    if user_input:
        st.session_state.messages.append({"role":"user","content":user_input})
        save_message(st.session_state.session_id, "user", user_input)
        st.chat_message("user").markdown(user_input)

        with st.spinner("Assistant is thinking..."):
            # Web search trigger
            if use_web_search and user_input.strip().lower().startswith(("web:", "search:", "google:")):
                q = user_input.split(":",1)[1].strip() if ":" in user_input else user_input
                st.info("Running web search...")
                res = web_search(q, num_results=3)
                if res.get("error"):
                    answer = f"Web search failed: {res['error']}"
                else:
                    snippets = "\n\n".join([f"- {r['title']}\n{r['snippet']}\n({r['link']})" for r in res.get("results", [])])
                    answer = f"Web search results:\n\n{snippets}"
                st.chat_message("assistant").markdown(answer)
                st.session_state.messages.append({"role":"assistant","content":answer})
                save_message(st.session_state.session_id, "assistant", answer)
            else:
                # RAG retrieval
                context = ""
                if use_rag:
                    try:
                        docs_and_scores = query_vector_store(user_input, k=4)
                        if docs_and_scores:
                            pieces = [doc.page_content for doc, score in docs_and_scores]
                            context = "\n\n---\n\n".join(pieces)
                    except Exception as e:
                        st.warning(f"RAG lookup failed: {e}")

                if context:
                    composed_input = f"Context:\n{context}\n\nQuestion: {user_input}"
                    assistant_reply = llm_chat_response([{"role":"user","content":composed_input}])
                else:
                    assistant_reply = llm_chat_response([{"role":"user","content":user_input}])

                # DELETED: Old, inefficient concise mode logic is no longer needed.

                st.chat_message("assistant").markdown(assistant_reply)
                st.session_state.messages.append({"role":"assistant","content":assistant_reply})
                save_message(st.session_state.session_id, "assistant", assistant_reply)

                # TTS moved outside the main logic flow to avoid re-triggering chat
                st.session_state.last_reply = assistant_reply


    # TTS button for the last reply
    if "last_reply" in st.session_state and st.session_state.last_reply:
        if st.button("Speak last reply (TTS)"):
            try:
                mp3_path = synthesize_text_to_mp3(st.session_state.last_reply)
                with open(mp3_path, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                os.remove(mp3_path) # Clean up temp file
            except Exception as e:
                st.error(f"TTS failed: {e}")


with tools_col:
    st.markdown("### Tools & Session")
    if st.button("Export chat (.txt)"):
        out = ""
        for m in st.session_state.messages:
            out += f"{m['role'].upper()}: {m['content']}\n\n"
        st.download_button("Download chat history", data=out, file_name="chat_history.txt")

    if st.button("Export session JSON"):
        path = dump_session_json(st.session_state.session_id)
        with open(path, "rb") as f:
            st.download_button("Download JSON", f, file_name=os.path.basename(path))

    if st.button("Clear chat (current session)"):
        from utils.memory import delete_session
        delete_session(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = new_session_id()
        st.rerun() # FIX: Replaced deprecated experimental_rerun

    prev = list_sessions(50)
    chosen = st.selectbox("Load previous session", ["-- current --"] + prev)
    if chosen and chosen != "-- current --":
        st.session_state.session_id = chosen
        st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in load_session_messages(chosen)]
        st.rerun() # FIX: Replaced deprecated experimental_rerun

st.markdown("---")
st.subheader("Analytics")
try:
    cur = _conn.cursor()
    cur.execute("SELECT session_id, role, content, created_at FROM messages ORDER BY created_at ASC")
    rows = cur.fetchall()
    if not rows:
        st.info("No message data collected yet.")
    else:
        df = pd.DataFrame(rows, columns=["session_id","role","content","created_at"])
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["date"] = df["created_at"].dt.date
        df["length_words"] = df["content"].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)

        st.write("Messages sample:")
        st.dataframe(df.tail(50))

        # Analytics plots
        st.write("### Charts")
        c1, c2, c3 = st.columns(3)
        with c1:
            msgs_per_day = df.groupby("date").size()
            fig1, ax1 = plt.subplots()
            ax1.plot(msgs_per_day.index, msgs_per_day.values)
            ax1.set_title("Messages per day")
            ax1.tick_params(axis='x', rotation=45)
            st.pyplot(fig1)
        with c2:
            fig2, ax2 = plt.subplots()
            ax2.hist(df["length_words"][df["length_words"] > 0].values, bins=30)
            ax2.set_title("Message length distribution")
            st.pyplot(fig2)
        with c3:
            top_sessions = df.groupby("session_id").size().nlargest(10)
            fig3, ax3 = plt.subplots()
            ax3.bar(range(len(top_sessions)), top_sessions.values)
            ax3.set_xticks(range(len(top_sessions)))
            ax3.set_xticklabels([s[:8] for s in top_sessions.index], rotation=45, ha="right")
            ax3.set_title("Top 10 sessions by messages")
            st.pyplot(fig3)
except Exception as e:
    st.error(f"Analytics failed: {e}")

st.markdown("---")
st.caption("Extend with streamlit-webrtc for in-browser recording or replace FAISS with Chroma if FAISS install fails.")
