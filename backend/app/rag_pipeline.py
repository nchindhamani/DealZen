import json
from openai import OpenAI
from .weaviate_client import get_weaviate_client, perform_hybrid_search
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RAGPipeline:
    def __init__(self):
        self.weaviate_client = get_weaviate_client()

    async def answer_query(self, query: str):
        search_results = await perform_hybrid_search(self.weaviate_client, query)
        
        if not search_results:
            return {"answer": "I'm sorry, I couldn't find any specific deals matching your query.", "source_deals": []}

        context = self.format_context(search_results)
        answer = self.generate_answer(context, query)
        
        source_deals = [json.loads(item['full_json']) for item in search_results]
        return {"answer": answer, "source_deals": source_deals}

    def format_context(self, search_results: list[dict]):
        context_str = "Available deals (Context):\n"
        for i, item in enumerate(search_results):
            context_str += f"--- Deal {i+1} ---\n{item['full_json']}\n\n"
        return context_str

    def generate_answer(self, context: str, query: str):
        system_prompt = f"""
        You are a helpful Black Friday shopping assistant. 
        Your goal is to answer the user's question based *only* on the deals provided in the context.
        Do not use any outside knowledge.
        If the deals do not contain the answer, say "I'm sorry, I couldn't find any deals for that."
        Be friendly, concise, and helpful. Summarize the deals that match the query.
        
        Context:
        {context}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o", # Use GPT-4o for RAG
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

