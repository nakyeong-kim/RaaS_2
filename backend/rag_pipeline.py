import os
from backend.document_parser import parse_document
from backend.embed import EmbedManager
from backend.chunking import chunk_text
from openai import AzureOpenAI
import numpy as np

class RAGPipeline:
    def __init__(self):
        self.embedder = EmbedManager()
        self.docs = []
        self.client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_KEY"),
            api_version="2025-04-01-preview"
        )
        self.deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")

    def ingest(self, file):
        text = parse_document(file)
        chunks = chunk_text(text)
        self.embedder.add_embeddings(chunks)

    def query(self, q):
        q_vec = self.embedder.embed_query(q)
        docs = self.embedder.search(q_vec)
        context = "\\n\\n".join(docs)
        completion = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. 한국어로 답변하세요."},
                {"role": "user", "content": f"다음 문맥을 참고해 질문에 답해줘:\\n{context}\\n\\n질문: {q}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return completion.choices[0].message.content
