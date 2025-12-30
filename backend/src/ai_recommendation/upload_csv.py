import os
from dotenv import load_dotenv
from langbase import Langbase

def main():
    load_dotenv()
    langbase_api_key = os.getenv("LANGBASE_API_KEY")

    langbase = Langbase(api_key=langbase_api_key)

    memory_name = "bali-travel-cohere-light"

    csv_file_path = os.path.join(os.path.dirname(__file__), "csv", "Bali_Popular_Destination_for_Tourist_2022_-_Sheet1.csv")

    try:
        with open(csv_file_path, "r", encoding="utf-8") as f:
            csv_content = f.read()

        print(f"Uploading CSV file: {csv_file_path}")
        print(f"File size: {len(csv_content)} bytes")

        # Upload the actual CSV file content
        response = langbase.memories.documents.upload(
            memory_name=memory_name,
            document_name="Bali_Popular_Destination_for_Tourist_2022_-_Sheet1.csv",
            document=csv_content.encode("utf-8"),
            content_type="text/csv",
            meta={
                "domain": "travel",
                "category": "tourism_destination",
                "location": "bali",
                "country": "indonesia",
                "year": "2022",
                "data_type": "tourist_attraction",
                "format": "csv"
            },
        )
        print("Document uploaded successfully!")
        print(f"Status: {response.status_code}")

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
    except Exception as e:
        print(f"Error uploading document: {e}")

if __name__ == "__main__":
    main()
