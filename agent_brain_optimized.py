# agent_brain_optimized.py (Fixed Version)

import google.generativeai as genai
import os
import json
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# Import our PLAIN PYTHON FUNCTIONS from agent_tools
from agent.agent_tools import (
    curriculum_planning_tool,
    research_and_save_module_tool
)
from agent.memory import find_similar_plan_in_db, get_embedding, format_plan_for_display

def main():
    """Main function to run the AI Learning Buddy as a LangChain Agent."""
    try:
        GEMINI_API_KEY = open("GEMINI_API_KEY.txt", 'r').read().strip()
        os.environ['GOOGLE_API_KEY'] = GEMINI_API_KEY
        genai.configure(api_key=GEMINI_API_KEY)
    except FileNotFoundError:
        print("ERROR: GEMINI_API_KEY.txt not found. Please create the file.")
        return

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5, convert_system_message_to_human=True)

    # Helper function to parse dictionary input from string
    def parse_dict_input(input_str):
        try:
            # Try to parse as JSON first
            if input_str.strip().startswith('{'):
                return json.loads(input_str)
            # If not JSON, try to parse key=value format
            else:
                # Simple parser for "topic=Python, step_description=Learn Basics"
                result = {}
                pairs = input_str.split(',')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        result[key.strip()] = value.strip()
                return result
        except:
            return input_str  # Return as-is if parsing fails

    # Build the tools using the Tool constructor
    tools = [
        Tool(
            name="Curriculum_Planning_Tool",
            func=lambda topic: curriculum_planning_tool(llm, topic),
            description="Use this tool FIRST to generate the initial step-by-step learning plan outline. Input must be the user's desired learning topic. Returns a JSON string of a list of module titles."
        ),
        Tool(
            name="Research_and_Save_Module_Tool",
            func=lambda tool_input: research_and_save_module_tool(llm, genai, parse_dict_input(tool_input)),
            description="Use this tool for EACH module of the learning plan to find resources AND save them to the database. The input MUST be in format: topic=TOPIC_NAME, step_description=MODULE_TITLE"
        ),
    ]

    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    print("Hello! I am your AI Learning Buddy (LangChain edition)")
    user_topic = input("What amazing thing do you want to learn today? ")

    print("\n🧠 Checking my database memory...")
    user_topic_embedding = get_embedding(genai, user_topic)
    found_plan = find_similar_plan_in_db(user_topic_embedding)

    if found_plan:
        print(f"\n🧠 I found a very similar plan for '{found_plan.topic}' in my database!")
        load_plan = input("Do you want to load this saved plan? (yes/no): ")
        if load_plan.lower() == 'yes':
            print("\nLoading your plan from the database...\n")
            print(format_plan_for_display(found_plan))
            return
    
    print(f"\n🤖 Launching LangChain agent to create a new plan for '{user_topic}'...")
    
    result = agent_executor.invoke({
        "input": f"Your mission is to create and save a learning plan for the topic: '{user_topic}'. "
                 "Follow these steps precisely: "
                 "1. First, use the 'Curriculum_Planning_Tool' with input '{user_topic}' to get a JSON list of module titles. "
                 "2. Then, for EACH module title in that JSON list, you MUST use the 'Research_and_Save_Module_Tool'. "
                 "For the Research_and_Save_Module_Tool, the input format must be: topic={user_topic}, step_description=MODULE_TITLE "
                 "3. After you have called the research tool for ALL modules, your job is done. "
                 "Your final answer should be a single sentence confirming the plan has been successfully created and saved."
    })
    
    print("\n✅ Agent has finished its work.")
    print(f"Final output: {result['output']}")

if __name__ == "__main__":
    main()