# main_agent.py
import os
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# You can also load this from a .env file for security
config_list = [
    {
        "model": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

system_prompt = """
You are a professional software refactor agent. When given source code, you:
1. Identify reusable components and group them logically
2. Extract them to proper utility modules (e.g., io.py, string_utils.py)
3. Generate clean import statements for main files
4. Return a preview-only output as a dictionary of files
5. Await confirmation before making actual file edits
"""

assistant = AssistantAgent(
    name="RefactorAgent",
    system_message=system_prompt,
    llm_config={"config_list": config_list}
)

user = UserProxyAgent(
    name="Developer",
    human_input_mode="NEVER",
    llm_config={"config_list": config_list}
)

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set. Please set it before running.")

    # Example code snippet to refactor
    code_snippet = '''
def add(a, b):
    return a + b

def sub(a, b):
    return a - b
'''
    print("Sending code to RefactorAgent...")
    user.initiate_chat(
        assistant,
        message=f"Please refactor the following code and preview the changes as described in your instructions.\n\n{code_snippet}"
    )

if __name__ == "__main__":
    main()
