from langchain.tools import Tool
import google.generativeai as genai
import os

#langchain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

#import our custom tools we created
from agent.agent_tools import(
  curriculum_planning_tool,
  resource_search_tool,
  save_plan_to_database_tool
)
from agent.memory import find_similar_plan_in_db, get_embedding, format_plan_for_display

def main():
  "Main function to run the AI Learning Buddy as a LangChain Agent"
  try:
    with open("GEMINI_API_KEY.txt", 'r') as f:
        GEMINI_API_KEY = f.read().strip()
    
    # This line is for LangChain. It finds the key in the environment variables.
    os.environ['GOOGLE_API_KEY'] = GEMINI_API_KEY
    
    # --- THE FIX (PART 2) ---
    # This line is for our direct calls to the genai library (like in get_embedding).
    # We need to explicitly configure it.
    genai.configure(api_key=GEMINI_API_KEY)

  except FileNotFoundError:
    print("ERROR: GEMINI_API_KEY.txt not found. Please create the file.")
    return
  
  #1. Setting up brain for our agent LLM
  llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

  # --- 2. Give the Agent its Tools ---
  # Create wrapper functions that include the required parameters
  def curriculum_planning_wrapper(topic: str) -> str:
    return curriculum_planning_tool.invoke({"chat_model": llm, "topic": topic})
  
  def resource_search_wrapper(step_description: str) -> str:
    return resource_search_tool.invoke({"chat_model": llm, "step_description": step_description})
  
  def save_plan_wrapper(tool_input: str) -> str:
    # Parse the input - it should be JSON with topic and full_curriculum_json
    import json
    try:
      parsed_input = json.loads(tool_input)
      return save_plan_to_database_tool.invoke({
        "genai_client": genai,
        "topic": parsed_input["topic"],
        "full_curriculum_json": parsed_input["full_curriculum_json"]
      })
    except:
      # If parsing fails, assume it's just the topic and create empty curriculum
      return save_plan_to_database_tool.invoke({
        "genai_client": genai,
        "topic": tool_input,
        "full_curriculum_json": "{}"
      })

  tools = [
    Tool(
      name="Curriculum Planning Tool",
      func=curriculum_planning_wrapper,
      description="Use this tool ONLY to generate the initial step-by-step learning plan outline. This tool DOES NOT find resources; it only creates the numbered list of module titles. Input must be the user's desired learning topic.",
    ),
    Tool(
      name="Resource Search Tool", 
      func=resource_search_wrapper,
      description="Use this tool for EACH module of the learning plan to find one web article and several YouTube videos. The input must be a single, specific step from the learning plan.",
    ),
    Tool(
      name="Save Plan to Database Tool",
      func=save_plan_wrapper,
      description="Use this FINAL tool to save the completed learning plan to the database. Input must be JSON with 'topic' and 'full_curriculum_json' keys.",
    ),
  ]

  # --- 3. Create the Agent's "Mission Briefing" (the Prompt) ---
  # We pull a standard, high-quality prompt from the LangChain Hub
  # This prompt is specifically designed for agents that use tools (ReAct framework)
  
  prompt = hub.pull("hwchase17/react")

  # --- 4. Assemble the Agent ---
  agent = create_react_agent(llm, tools, prompt)
  agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

  # Now we run the agent
  print("Hello! I am your AI Learning Buddy (LangChain edition)")
  user_topic = input("What amazing thing do you want to learn today? ")

  # We will check our database first instead of manually starting generating answers
  print("\n Checking my database memory")
  user_topic_embedding = get_embedding(genai, user_topic)
  found_plan = find_similar_plan_in_db(user_topic_embedding)

  if found_plan:
    print(f"\n🧠 I found a very similar plan for '{found_plan.topic}' in my database!")
    load_plan = input("Do you want to load this saved plan? (yes/no): ")
    if load_plan.lower() == 'yes':
      print("\nLoading your plan from the database...\n")
      print(format_plan_for_display(found_plan))
      return
    
  # If no plan is found, we launch the agent to create a new one
  print(f"\n🤖 Launching LangChain agent to create a new plan for '{user_topic}'...")

  result = agent_executor.invoke({
    "input":  f"Create a full, detailed learning plan with resources for the topic: '{user_topic}'."
              "First, create the plan outline. Then, for each step in the outline, find resources."
              "Finally, save the complete plan to the database and confirm when you are done."
  })

  print("\nAgent has finished its work.")
  print(f"Final output: {result['output']}")

if __name__ == "__main__":
  main()