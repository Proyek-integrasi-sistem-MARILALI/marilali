import os
import json
from langbase import Langbase
from dotenv import load_dotenv

load_dotenv()

langbase = Langbase(api_key=os.getenv('LANGBASE_API_KEY'))

def main():
	support_agent = langbase.pipes.create(
		name='ai-support-agent',
		description='An AI pipe agent that supports users with their queries.',
		messages=[
			{
				'role': 'system',
				'content': "You're a helpful AI assistant."
			}
		],
		upsert=True
	)

	print(json.dumps(support_agent, indent=2))

if __name__ == "__main__":
	main()
