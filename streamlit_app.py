import streamlit as st
from pyvis.network import Network
import networkx as nx
import time
import os

# 만약 stvis 설치 가능하면 (pip install stvis)
use_stvis = False
if use_stvis:
    from stvis import pv_static

st.set_page_config(layout="wide")

if "status" not in st.session_state:
    st.session_state.status = "waiting"
if "ontology_triples" not in st.session_state:
    st.session_state.ontology_triples = []

# 사이드바: 파일 업로드
uploaded = st.sidebar.file_uploader("문서 업로드", type=["pdf", "docx", "txt", "xlsx"])
if uploaded:
    st.sidebar.success("업로드됨")

col1, col2 = st.columns([0.6, 0.4])
with col1:
    st.header("질문")
    user_q = st.text_input("문의 입력")
    if st.button("질문 보내기") and user_q:
        st.session_state.status = "embedding"

with col2:
    st.header("진행 상태 / 그래프")
    status = st.session_state.status

    if status == "embedding":
        st.info("📘 문서 임베딩 중...")
        time.sleep(1.0)
        # 예시용: 미리 만들어 둔 triples 일부만 꺼내기
        st.session_state.ontology_triples = [
            {"subject": "Alice", "relation": "works_for", "object": "Acme Corp"},
        ]
        st.session_state.status = "ontology"

    elif status == "ontology":
        st.success("✅ 임베딩 완료")
        st.info("🔍 온톨로지 추출 중...")
        time.sleep(1.3)
        # 단계 확장: 기존 노드 + 새로운 관계 추가
        st.session_state.ontology_triples.append({
            "subject": "Acme Corp",
            "relation": "based_in",
            "object": "San Francisco"
        })
        st.session_state.status = "graph"

    elif status == "graph":
        st.success("✅ 온톨로지 부분 확장됨")
        st.info("🌐 지식 그래프 렌더링 중...")

        # Build graph
        G = nx.DiGraph()
        for t in st.session_state.ontology_triples:
            G.add_edge(t["subject"], t["object"], relation=t["relation"])

        net = Network(height="400px", width="100%", directed=True)
        net.from_nx(G)
        for node in net.nodes:
            # node["title"] = node id or 기타 hover 정보
            pass

        # 렌더링
        if use_stvis:
            pv_static(net)
        else:
            # HTML 임시 저장
            tmpfile = "graph.html"
            net.save_graph(tmpfile)
            html = open(tmpfile, 'r', encoding="utf-8").read()
            st.components.v1.html(html, height=450)

        st.session_state.status = "answer"

    elif status == "answer":
        st.success("✅ 그래프 렌더링 완료")
        st.info("💡 답변 생성 중...")
        time.sleep(0.7)
        st.write("Alice works for Acme Corp, which is based in San Francisco.")
        st.session_state.status = "done"

    elif status == "done":
        st.write("✨ 데모 완료")

# import streamlit as st
# from backend.rag_pipeline import RAGPipeline
# import os

# st.set_page_config(page_title="Azure RAG Chatbot", layout="wide")
# st.title("💬 Azure RAG Chatbot")

# # 초기화
# if "rag" not in st.session_state:
#     st.session_state.rag = RAGPipeline()

# uploaded_files = st.file_uploader("문서 업로드 (PDF, PPTX, XLSX, CSV, TXT 등)", accept_multiple_files=True)
# if uploaded_files:
#     for file in uploaded_files:
#         st.session_state.rag.ingest(file)
#     st.success("✅ 문서 업로드 및 인덱싱 완료!")

# query = st.text_input("질문을 입력하세요.")
# if st.button("질의 실행") and query:
#     with st.spinner("검색 및 응답 생성 중..."):
#         answer = st.session_state.rag.query(query)
#         st.markdown("### 🧠 답변:")
#         st.write(answer)

# import requests
# st.write("여기에..")
# st.write(requests.get("http://10.233.47.163:8000/ping").json())
