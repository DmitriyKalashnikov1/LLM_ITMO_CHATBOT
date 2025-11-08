from langchain_core.embeddings import Embeddings
from typing import List, Dict, Any, Optional
#from langchain_ollama import OllamaEmbeddings
#from langchain_openai import OpenAIEmbeddings
import lmstudio as lms



class MyEmbeddingFunction(Embeddings):
    def embed_documents(texts: List[str]) -> List[List[float]]:
        # embed the documents somehow
        #embeddingsModel = OllamaEmbeddings(model="evilfreelancer/enbeddrus")
        embeddingsModel = lms.embedding_model("mxbai-embed-large-v1")
        embeddings = embeddingsModel.embed(texts)
        return embeddings
    def embed_query(text: str) -> list[float]:
        #embeddingsModel = OllamaEmbeddings(model="evilfreelancer/enbeddrus")
        embeddingsModel = lms.embedding_model("mxbai-embed-large-v1")
        embeddings = embeddingsModel.embed(text)
        return embeddings