from langchain_community.retrievers.azure_cognitive_search import AzureCognitiveSearchRetriever
from langchain_community.chat_models import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import os

from config import settings


# 1. Azure Cognitive Search retriever 생성
def build_azure_search_retriever():
    retriever = AzureCognitiveSearchRetriever(
        azure_search_endpoint=settings.search_endpoint,
        azure_search_key=settings.search_api_key,
        index_name=settings.index_name,
        api_version="2023-11-01"
    )
    return retriever

# 2. Langchain 기반 QA 체인 생성

def create_langchain_qa_chain(retriever):
    llm = AzureChatOpenAI(
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_endpoint,
        openai_api_version="2024-12-01-preview",
        deployment_name=settings.chat_model,
        openai_api_type="azure",
        temperature=0.2
    )
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )
    return qa_chain

# 3. 예시: Langchain QA 체인으로 질의
if __name__ == "__main__":
    retriever = build_azure_search_retriever()
    qa_chain = create_langchain_qa_chain(retriever)
    print("질문을 입력하세요 (종료: exit):")
    while True:
        query = input("> ")
        if query.strip().lower() == "exit":
            break
        result = qa_chain({"question": query})
        print("답변:", result["answer"])
        print("\n---\n")
