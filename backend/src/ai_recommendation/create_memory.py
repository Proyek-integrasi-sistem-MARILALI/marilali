import json
import os
from dotenv import load_dotenv
from langbase import Langbase

def main():
    load_dotenv()
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    langbase = Langbase(api_key=langbase_api_key)
    
    try:
        response = langbase.memories.create(
            name="bali-travel-cohere-light", 
            embedding_model="cohere:embed-multilingual-light-v3.0",
            chunk_size=1024, 
            chunk_overlap=256,  
        )

        print("Memory created successfully!")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Error creating memory: {e}")

if __name__ == "__main__":
    main()
