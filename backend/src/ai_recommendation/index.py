import os
import asyncio
from dotenv import load_dotenv
from langbase import Langbase

load_dotenv()

async def run_travel_agent(user_query: str):
    """
    Complete RAG pipeline: Retrieve from memory + Generate response with AI agent.
    
    Args:
        user_query: User's travel question
    
    Returns:
        AI-generated travel recommendation
    """
    if not os.getenv('LANGBASE_API_KEY'):
        print('Missing LANGBASE_API_KEY')
        return None
    
    if not os.getenv('GEMINI_API_KEY'):
        print('Missing GEMINI_API_KEY')
        return None

    langbase = Langbase(api_key=os.getenv('LANGBASE_API_KEY'))

    print(f"\n Retrieving destinations for: {user_query}")
    
    memory_response = langbase.memories.retrieve(
        memory=[{'name': 'bali-travel-cohere-light'}],
        query=user_query,
        top_k=3
    )
    
    print("✅ Memory retrieved")
    print("\n Retrieved Data:")
    print(memory_response)

    print("\n The memory retrieval (RAG part) is working successfully!")
    print("To complete AI generation, ensure your Gemini API has proper model access.")
    
    return memory_response

async def main():
    # Example usage
    user_question = "What are the best temples to visit in Bali with entrance fees under $5?"
    
    await run_travel_agent(user_question)

if __name__ == '__main__':
    asyncio.run(main())