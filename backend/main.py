import os
from dotenv import load_dotenv
from langbase import Langbase
load_dotenv()

def main():
	langbase_api_key = os.environ.get("LANGBASE_API_KEY")
	llm_api_key = os.environ.get("GEMINI_API_KEY")

	langbase = Langbase(api_key=langbase_api_key)

	# Run the agent
	response = langbase.agent.run(
		stream=False,
		model="google:gemini-1.5-flash",
		api_key=llm_api_key,
		instructions='You are an AI agent that summarizes user support queries for a support agent.',
		input='I am having trouble logging into my account. I keep getting an error message that says "Invalid credentials." I have tried resetting my password, but it still does not work. Can you help me?',
	)

	print("response:", response.get("output"))


if __name__ == "__main__":
	main()
