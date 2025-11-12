import json
from openai import OpenAI
from .weaviate_client import get_weaviate_client, perform_hybrid_search
import os

class RAGPipeline:
    def __init__(self):
        self.weaviate_client = get_weaviate_client()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def answer_query(self, query: str):
        search_results = await perform_hybrid_search(self.weaviate_client, query)
        
        if not search_results:
            return {"answer": "I'm sorry, I couldn't find any specific deals matching your query.", "source_deals": []}

        context = self.format_context(search_results)
        answer, relevant_indices = self.generate_answer_with_relevance(context, query, len(search_results))
        
        all_deals = [json.loads(item['full_json']) for item in search_results]
        
        # Check if GPT-4o explicitly said "no deals found"
        no_deals_phrases = ["couldn't find any deals", "couldn't find any specific deals", 
                           "no deals", "not find any deals", "don't have any deals"]
        answer_lower = answer.lower()
        gpt_found_no_deals = any(phrase in answer_lower for phrase in no_deals_phrases)
        
        # If GPT-4o says no deals found, return empty list (don't show random deals!)
        if gpt_found_no_deals:
            return {"answer": answer, "source_deals": []}
        
        # Trust GPT-4o's relevance filtering
        # Only show deals that GPT-4o identifies as truly relevant
        if relevant_indices:
            source_deals = [all_deals[i] for i in relevant_indices if i < len(all_deals)]
        else:
            # If no indices but GPT has an answer, show no deals (trust GPT)
            source_deals = []
        
        return {"answer": answer, "source_deals": source_deals}

    def format_context(self, search_results: list[dict]):
        context_str = "Available deals (Context):\n"
        for i, item in enumerate(search_results):
            context_str += f"--- Deal {i+1} ---\n{item['full_json']}\n\n"
        return context_str

    def generate_answer_with_relevance(self, context: str, query: str, num_deals: int):
        """Generate answer and identify which deals are actually relevant to the query."""
        system_prompt = f"""
        You are a helpful Black Friday shopping assistant. 
        Your goal is to answer the user's question based *only* on the deals provided in the context.
        Do not use any outside knowledge.
        If the deals do not contain the answer, say "I'm sorry, I couldn't find any deals for that."
        Be friendly, concise, and helpful. Summarize the deals that match the query.
        
        IMPORTANT: After your answer, on a new line, write "RELEVANT_DEALS:" followed by a comma-separated list of deal numbers (1, 2, 3, etc.) that are relevant to the user's query.
        Include ALL deals that match the user's intent, even if you don't mention every single one in your answer. Be generous in determining relevance.
        
        Example format:
        [Your friendly answer about the deals]
        RELEVANT_DEALS: 1, 3
        
        Context:
        {context}
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        
        full_response = response.choices[0].message.content
        
        # Parse out the relevant deals
        relevant_indices = []
        if "RELEVANT_DEALS:" in full_response:
            parts = full_response.split("RELEVANT_DEALS:")
            answer = parts[0].strip()
            
            # Extract deal numbers and convert to 0-indexed
            try:
                deals_str = parts[1].strip()
                deal_numbers = [int(x.strip()) for x in deals_str.split(",") if x.strip().isdigit()]
                relevant_indices = [num - 1 for num in deal_numbers if num > 0]  # Convert to 0-indexed
            except:
                # If parsing fails, return all deals
                relevant_indices = list(range(num_deals))
        else:
            # If no RELEVANT_DEALS marker found, return answer as-is and all deals
            answer = full_response
            relevant_indices = list(range(num_deals))
        
        return answer, relevant_indices
    
    def generate_answer(self, context: str, query: str):
        """Legacy method for backward compatibility."""
        system_prompt = f"""
        You are a helpful Black Friday shopping assistant. 
        Your goal is to answer the user's question based *only* on the deals provided in the context.
        Do not use any outside knowledge.
        If the deals do not contain the answer, say "I'm sorry, I couldn't find any deals for that."
        Be friendly, concise, and helpful. Summarize the deals that match the query.
        
        Context:
        {context}
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

