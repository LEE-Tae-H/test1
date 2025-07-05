import os
from openai import AzureOpenAI

class LLM:
    index_name = os.getenv("INDEX_NAME")
    def __init__(self, openai_endpoint, openai_api_key, chat_model, search_endpoint, search_api_key):
        self.chat_client = AzureOpenAI(
            api_version="2024-12-01-preview"
            azure_endpoint=openai_endpoint,
            api_key=openai_api_key
        )
        self.chat_model = chat_model
        self.search_endpoint = search_endpoint
        self.search_api_key = search_api_key

    def get_openai_response(self, messages):
        """
        GPT 응답을 생성하는 함수 (기본적으로 RAG 활성화)
        """
        rag_params = {
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": self.search_endpoint,
                        # "index_name": index_name,
                        "authentication": {
                            "type": "api_key",
                            "key": self.search_api_key,
                        }
                    }
                }
            ]
        }

        response = self.chat_client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            extra_body=rag_params
        )
        return response.choices[0].message.content