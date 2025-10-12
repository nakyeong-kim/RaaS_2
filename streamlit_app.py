import streamlit as st

st.set_page_config(page_title="RaaS - RAG as a Service", layout="wide")
st.title("🤖 RaaS (RAG as a Service)")
st.subheader("어떤 문서든, 얼마나 많든, 원하는 정보를 신뢰성 있게 찾는다.")

st.markdown("""
RaaS는 **문서 포맷에 상관없이 전처리 → 임베딩 → 검색 → 응답 생성** 과정을 자동화하는  
AI 기반 검색/요약 서비스입니다.

---

### 🚩 문제 정의
- 사내에는 다양한 형식의 문서(PDF, Excel, PPT, E-mail 등)가 존재하지만  
  기존 RAG 방식은 문서 구조 파악과 대규모 데이터 검색에서 정확도가 급격히 떨어집니다.

---

### 💡 RaaS가 해결하는 문제
1. **포맷 무관 문서 전처리**  
   - PDF, Excel, 이미지 스캔 등 모든 문서에 대응  
2. **정확한 임베딩 & 검색**  
   - Azure Text-Embedding + Semantic Reranker 기반  
3. **정확한 응답 생성**  
   - GPT-4o 기반 LLM 응답 + 근거 문서 출처 제공  
4. **API / MCP 모듈 제공**  
   - 사내 챗봇, ERP, 자동화 서비스에 연동 가능  

---

### 🧩 서비스 제공 형태
| 구분 | 설명 |
|------|------|
| 💬 사용자용 RaaS Chat | 문서 업로드 후 질문하면 AI가 자동 요약/검색 |
| ⚙️ 개발자용 API/MCP | 사내 시스템과 연동할 수 있는 모듈 제공 |

---

### 📈 기대 효과
- 문서 검색 시간 **70% 단축**  
- 보고서 작성 자동화율 **60% 향상**  
- 재무/기술팀 등 문서 기반 업무의 **생산성 극대화**

---

> 지금 [왼쪽 메뉴]에서 **LLM 테스트** 페이지로 이동해 직접 체험해보세요!
""")
