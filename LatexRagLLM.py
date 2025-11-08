from langchain_chroma import Chroma
from typing import List, Dict
#from langchain_ollama.chat_models import ChatOllama
import lmstudio as lms
#from langchain.chains import ConversationalRetrievalChain
from rag import LatexRAGSystem, LatexProcessor
import time
import datasetsPaths


class LatexLLM:
    def __init__(self):
        self.dbPaths = {
            "Энтропия": datasetsPaths.ENTROPY_CHROMA_PATH,
            "Ансамбли моделей": datasetsPaths.ENSEMBLES_CHROMA_PATH,
            "Обучение с подкреплением": datasetsPaths.RL_CHROMA_PATH
        }
        self.rag = None
        self.ollama = None
        self.chain =  None

    def stream(self, modelName: str, lTitle:str, prompt:str, userQuery: str, chatHistory: List[Dict]):
        if lTitle in self.dbPaths.keys():
            self.rag = LatexRAGSystem(LatexProcessor(self.dbPaths[lTitle]).collection)
            #self.ollama = ChatOllama(model=modelName, validate_model_on_init=True, num_predict=500, reasoning=False)
            # self.chain = ConversationalRetrievalChain.from_llm(
            #     self.ollama,
            #     retriever=self.rag.collection.as_retriever(search_kwargs={'k': 6}),
            #     return_source_documents=False,
            #     verbose=False
            # )
            self.ollama = lms.llm(modelName)
            promptAndQuery = self.rag.generatePromptWithLatexContext(prompt, userQuery)
            self.chain = lms.Chat(promptAndQuery[0]["content"])
            h = self.rag.convertHistory(chatHistory)
            for d in h:
                if d["role"] == "user":
                    self.chain.add_user_message(d["content"])
                else:
                    self.chain.add_assistant_response(d["content"])
            self.chain.add_user_message(promptAndQuery[1]["content"])
            outputStream = self.ollama.respond_stream(self.chain)

            reason = True
            for chunk in outputStream:
                if chunk.reasoning_type == "none":
                    reason = False
                    yield ""
                if (reason == False):
                    yield chunk.content
                    time.sleep(0.05)
        else:
            resp = "В системе нет лекций с таким названием."
            for word in resp.split():
                yield word + " "
                time.sleep(0.05)


if __name__ == "__main__":
    llm = LatexLLM()
    genWord = llm.stream(modelName="deepseek-r1-0528-qwen3-8b", lTitle="Энтропия", prompt="Ты учитель по машинному обучению, как можно понятнее отвечай студенту на его вопросы, при необходимости дополнительно опираясь на данный тебе Latex-контекст.",
                         userQuery="что такое энтропия в машинном обучении?",
                         chatHistory=[{}])
    for word in genWord:
        print(word, end="")