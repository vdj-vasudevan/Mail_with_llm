from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
from phi.model.openai import OpenAIChat
import json
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

OAI_KEY = os.getenv("OAI_KEY")

def extract_json(data):
    """Safely extracts JSON from a formatted string."""
    _, _, json_part = data.partition("```json")
    json_part, _, _ = json_part.partition("```")
    
    try:
        return json.loads(json_part)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in extracted data.")
    
def get_port_pair_data(input, local_agent=False):
    if local_agent:
        try:
            local_agent = Agent(
                model=Ollama(id="deepseek-r1:1.5b"),
                instructions = ["Your task is to Read the given text Port pair data",
                            "you return as json or list of dict with port pair data",
                            "Response Example :[{'origin_port': '...', 'destination_port': '...'},{'origin_port': '...', 'destination_port': '...'}...]",
                            "Dont Go out of the context",
                            "Response should always be in english"],
                markdown=True,
            )
            
            run: RunResponse = local_agent.run(f"Note your work is to extract a json from input text: {input}, Response should always be in english. Example :[{{'origin_port': '...', 'destination_port': '...'}}...]")
            print(run.content)
            output = extract_json(run.content)
            return output
        except Exception as e:
            pass
    
    api_agent =Agent(
        name="Web Agent",
        model=OpenAIChat(id="gpt-4o",api_key=OAI_KEY),
        instructions= ["Your task is to Read the given text Port pair data",
                            "you return as json or list of dict with port pair data",
                            "Response Example :[{'origin_port': '...', 'destination_port': '...'},{'origin_port': '...', 'destination_port': '...'}...]",
                            "Dont Go out of the context",
                            "Response should always be in english"]
            # debug_mode=True,
    )
    agent_input = f"Note your work is to extract a json from input text: {input}"+", Response should always be in english. Example :[{'origin_port': '...', 'destination_port': '...'}...]"
    api_agent.print_response(agent_input)
    output = eval(api_agent.get_chat_history())
    try:
        output = eval(output[1]["content"].split("```")[1].strip("json").strip("\n")) if "json" in output[1]["content"] else eval(output[1]["content"].strip("\n"))
    except:
        pass
    return output
    
# input2 = 'Body: Get Schedule From Shanghai to Hamburg, From Shanghai to New york, From Shanghai to Davao city\n\n'
# input1 = "Subject: Get Schedule\nBody: From Shanghai to Hamburg\n\n"
# data = get_port_pair_data(input1,False)
# data2 = get_port_pair_data(input2,False)

# print(data)

# print("Test Passed")