import os
from openai import AzureOpenAI
class LLM:
    def __init__(self, openai_endpoint, openai_api_key, chat_model, search_endpoint, search_api_key, index_name):
        self.chat_client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint=openai_endpoint,
            api_key=openai_api_key
        )

        self.chat_model = chat_model
        self.search_endpoint = search_endpoint
        self.search_api_key = search_api_key
        self.index_name = index_name
    def get_openai_response(self, query: str):
        try:
            rag_params = {
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": self.search_endpoint,
                            "index_name": self.index_name,
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
                messages=[
                    {"role": "system", "content": "당신은 인시던트 분석 에이전트입니다. 사용자의 질문에 대해 정확하고 유용한 답변을 제공하세요."},
                    {"role": "user", "content": query}
                ],
                max_tokens=1000,
                temperature=0.5,
                extra_body=rag_params
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"에러 발생: {e}"

