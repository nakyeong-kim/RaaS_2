
import streamlit as st
from backend.rag_pipeline import RAGPipeline
import os

st.set_page_config(page_title="Azure RAG Chatbot", layout="wide")
st.title("💬 Azure RAG Chatbot")

# 초기화
if "rag" not in st.session_state:
    st.session_state.rag = RAGPipeline()

uploaded_files = st.file_uploader("문서 업로드 (PDF, PPTX, XLSX, CSV, TXT 등)", accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        st.session_state.rag.ingest(file)
    st.success("✅ 문서 업로드 및 인덱싱 완료!")

query = st.text_input("질문을 입력하세요.")
if st.button("질의 실행") and query:
    with st.spinner("검색 및 응답 생성 중..."):
        answer = st.session_state.rag.query(query)
        st.markdown("### 🧠 답변:")
        st.write(answer)
