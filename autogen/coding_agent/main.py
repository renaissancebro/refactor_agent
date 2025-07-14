import os
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# Set up your OpenAI API key
# You can either set it as an environment variable or uncomment the line below
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Initialize the config list for the model
config_list = [
    {
        "model": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# System prompt defines the task
system_prompt = """
You're DevAgent. You take my scraper + keyword flagger code and:
1. Break it into modules: scraping, flagging, notifications.
2. Add docstrings, type hints.
3. Suggest tests for each module.
4. Generate Chainlit-compatible wrappers where needed.
Always ask follow-up questions before refactoring.
"""

assistant = AssistantAgent(
    name="DevAgent",
    system_message=system_prompt,
    llm_config={"config_list": config_list}
)

user = UserProxyAgent(
    name="Developer",
    human_input_mode="NEVER",  # Set to "ALWAYS" if you want to interact manually
    llm_config={"config_list": config_list}
)

def main():
    # Read the backend file
    backend_file = "backend/main.py"
    try:
        with open(backend_file, 'r') as f:
            code = f.read()

        # Start a chat between the user and assistant with the code
        user.initiate_chat(
            assistant,
            message=f"I have this scraper and keyword flagger code that I want to refactor into modules. Here's the current code:\n\n```python\n{code}\n```\n\nCan you help me break it down into separate modules with proper documentation and tests?"
        )
    except FileNotFoundError:
        print(f"Error: {backend_file} not found. Please make sure the backend directory exists.")
    except Exception as e:
        print(f"Error reading {backend_file}: {e}")

if __name__ == "__main__":
    main()
