import streamlit as st
import openai
import psycopg2
import numpy as np
import time
from sentence_transformers import SentenceTransformer

st.image("images/image.png", width=110) 
# Back button to main app page
if st.button("⬅️ Back"):
    st.switch_page("app.py")

st.set_page_config(page_title="Chat with Lake", layout="wide")
st.title("Chat with your Data")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input at the bottom
user_input = st.chat_input("Ask something about your data...")

if user_input:
    # Add user message and set as pending for processing
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.pending_user_input = user_input
    st.rerun()

# If there is a pending user input, process it and stream the assistant's response
if st.session_state.get("pending_user_input"):
    # Show animation
    with st.chat_message("assistant"):
        placeholder = st.empty()
        # Animated "Thinking..." dots
        for i in range(6):
            placeholder.markdown("🎣 Fishing" + "." * (i % 3 + 1))
            time.sleep(0.3)

        # --- Backend logic: embedding, vector search, LLM call ---
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_emb = model.encode(st.session_state.pending_user_input).tolist()

        conn = psycopg2.connect(
            dbname="data_lake",
            user="postgres",
            password="postgres",
            host="db",
            port=5432
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT chunk_text, embedding <-> %s::vector as distance
            FROM vector_store
            ORDER BY distance
            LIMIT 5
        """, (query_emb,))
        top_chunks = cur.fetchall()
        conn.close()

        context = "\n".join([chunk[0] for chunk in top_chunks])
        prompt = f"Context:\n{context}\n\nQuestion: {st.session_state.pending_user_input}\nAnswer:"

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You're a helpful data assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content

        # Stream the answer character by character
        streamed = ""
        for char in answer:
            streamed += char
            placeholder.markdown(streamed)
            time.sleep(0.01)  # Adjust speed as desired

    # Add assistant message to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.session_state.pending_user_input = None
    st.rerun()