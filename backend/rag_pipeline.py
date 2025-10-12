# backend/rag_pipeline.py
import os, json
from backend.document_parser import parse_document
from backend.embed import EmbedManager
from backend.chunking import chunk_text
from backend.reranker import Reranker
from backend.tools import summarize_dataframe, plot_dataframe
from openai import AzureOpenAI
import tempfile

class RAGPipeline:
    def __init__(self):
        self.embedder = EmbedManager()
        self.reranker = Reranker()
        self.client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_KEY"),
            api_version="2025-04-01-preview"
        )
        self.deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")

    def ingest(self, uploaded_file):
        """
        uploaded_file: Streamlit UploadedFile or file-like
        """
        text = parse_document(uploaded_file)
        chunks = chunk_text(text)
        self.embedder.add_embeddings(chunks)

    def query(self, q, top_k=10):
        # 1) embed query & get candidate chunks (use vector store)
        q_vec = self.embedder.embed_query(q)
        candidates = self.embedder.search(q_vec, top_k=top_k)  # returns list of chunk texts

        # 2) rerank using cross-encoder if available
        reranked = self.reranker.rerank(q, candidates, top_k=5, embed_fn=self.embedder.embed_text)

        # build context text
        context = "\n\n".join([t for t, s in reranked])

        # 3) Call Azure OpenAI with tools metadata to allow function calling
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "summarize_dataframe",
                    "description": "CSV/XLSX 데이터의 기초 통계를 JSON으로 반환합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string", "description": "CSV 텍스트 또는 파일 경로"}
                        },
                        "required": ["data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "plot_dataframe",
                    "description": "CSV데이터를 읽어 x,y 컬럼으로 그래프를 그려 이미지 경로를 반환합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"},
                            "x": {"type": "string"},
                            "y": {"type": "string"},
                            "kind": {"type": "string"}
                        },
                        "required": ["data", "x", "y"]
                    }
                }
            }
        ]

        messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond in Korean."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"}
        ]

        completion = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.0,
            max_tokens=1200
        )

        assistant_msg = completion.choices[0].message

        # If model requests a tool (function) call, handle it
        if assistant_msg.tool_calls:
            tool_call = assistant_msg.tool_calls[0]
            fname = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            try:
                if fname == "summarize_dataframe":
                    result = summarize_dataframe(args["data"])
                    # return result to model to get final answer
                    messages.append({
                        "role": "tool",
                        "name": fname,
                        "content": result,
                        "tool_call_id": tool_call.id
                    })
                elif fname == "plot_dataframe":
                    img_path = plot_dataframe(args["data"], args["x"], args["y"], kind=args.get("kind","line"))
                    # we can return image path or base64
                    # return path
                    messages.append({
                        "role": "tool",
                        "name": fname,
                        "content": json.dumps({"image_path": img_path}),
                        "tool_call_id": tool_call.id
                    })
                # ask model for final answer
                final = self.client.chat.completions.create(model=self.deployment, messages=messages)
                return final.choices[0].message.content
            except Exception as e:
                return f"함수 호출 처리 중 오류 발생: {e}"

        # If no tool_calls, just return assistant text
        return assistant_msg.content
