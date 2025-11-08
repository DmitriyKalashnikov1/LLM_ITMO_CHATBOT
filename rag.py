from langchain_chroma import Chroma
from typing import List, Dict, Any, Optional
import os
from langchain_core.documents import Document
from latexProcessor import LatexProcessor
import datasetsPaths

class LatexRAGSystem:
    def __init__(self, collection:Chroma):
        self.collection = collection

    def query_latex(self, query: str) -> List[Dict]:
        """Ищет релевантные LaTeX фрагменты"""
        results = self.collection.similarity_search_with_score(
            query=query,
        )

        formatted_results = []
        for (document, score) in results:
            formatted_results.append({
                "content": document.page_content,  # LaTeX с разметкой
                "clean_text": document.metadata.get("clean_text", ""),
                "metadata": document.metadata,
                "score": score
            })

        return formatted_results

    def generatePromptWithLatexContext(self, systemPrompt: str, query: str) -> List[dict]:
        """Генерирует финальный промпт для LLM с LATEX-контекстом"""

        latex_context = "\n\n".join([item["content"] for item in self.query_latex(query)])

        messages = [
            {   "role":"system",
                "content": f"{systemPrompt} LaTeX контекст: {latex_context} Отвечай сторого в формате LaTeX."
            },
            {'role':"user", "content": query}
        ]

        return messages

    def convertHistory(self, history: List[dict]) -> List[dict]:
        cH = []
        for m in history:
            if "role" in m.keys():
                if m["role"] == "user":
                    cH += [{'role':"user", "content": m['content']}]
                elif m["role"] == "assistant":
                    cH += [{'role':"assistant", "content": m['content']}]
                else:
                    pass
        return cH


# Использование всей системы
def setup_latex_rag_system(directory_path: str, dbPath:str) -> LatexRAGSystem:
    """Настраивает полную RAG систему для LaTeX"""
    processor = LatexProcessor(dbPath)
    print(f"Create chroma db from: {directory_path}", end="")
    for filename in os.listdir(directory_path):
        if filename.endswith('.tex'):
            file_path = os.path.join(directory_path, filename)
            processor.add_latex_file(file_path)
    print(" done.")

    return LatexRAGSystem(processor.collection)


if __name__ == "__main__":

    dbPaths = [datasetsPaths.RL_CHROMA_PATH, datasetsPaths.ENTROPY_CHROMA_PATH, datasetsPaths.ENSEMBLES_CHROMA_PATH]
    dsPaths = [datasetsPaths.RL_DS_PATH, datasetsPaths.ENTROPY_DS_PATH, datasetsPaths.ENSEMBLES_DS_PATH]

    rags = []

    for (dirP, dbP) in zip(dsPaths, dbPaths):
        rags.append(setup_latex_rag_system(dirP, dbP))
