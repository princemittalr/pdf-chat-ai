import streamlit as st
from groq import Groq
import PyPDF2
import os

api_key = os.environ.get("GROQ_API_KEY", "ENTER YOUR GROQ_API_KEY")
client = Groq(api_key=api_key)

st.set_page_config(page_title="PDF Chat", page_icon="📄")
st.title("📄 Chat with any PDF")
st.write("Upload a PDF — ask anything about it in simple language.")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    st.success(f"PDF loaded — {len(pdf_reader.pages)} pages read.")

    if "pdf_messages" not in st.session_state:
        st.session_state.pdf_messages = []

    for message in st.session_state.pdf_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_question = st.chat_input("Ask anything about this PDF...")

    if user_question:
        st.session_state.pdf_messages.append(
            {"role": "user", "content": user_question}
        )
        with st.chat_message("user"):
            st.write(user_question)

        system_prompt = f"""You are a helpful assistant that answers questions 
about a document. Only use information from this document to answer.
If the answer is not in the document, say "I could not find this in the document."
Keep answers simple and clear.

DOCUMENT CONTENT:
{pdf_text[:8000]}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.pdf_messages
            ]
        )

        ai_reply = response.choices[0].message.content
        st.session_state.pdf_messages.append(
            {"role": "assistant", "content": ai_reply}
        )
        with st.chat_message("assistant"):
            st.write(ai_reply)
else:
    st.info("👆 Upload a PDF above to get started.")