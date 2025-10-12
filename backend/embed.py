
import numpy as np
from chromadb import Client
from chromadb.config import Settings
from openai import AzureOpenAI
import os
import chromadb

chromadb.api.client.SharedSystemClient.clear_system_cache()

class EmbedManager:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_KEY"),
            api_version="2025-04-01-preview"
        )
        self.embed_deployment = os.environ.get("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-large")
        self.chroma = Client(Settings(persist_directory="storage/embeddings"))
        self.collection = self.chroma.get_or_create_collection("docs")

    def add_embeddings(self, texts):
        for t in texts:
            emb = self.client.embeddings.create(model=self.embed_deployment, input=t).data[0].embedding
            self.collection.add(documents=[t], embeddings=[emb])

    def embed_query(self, q):
        return self.client.embeddings.create(model=self.embed_deployment, input=q).data[0].embedding

    def search(self, q_vec, top_k=5):
        results = self.collection.query(query_embeddings=[q_vec], n_results=top_k)
        return results["documents"][0] if results["documents"] else []

