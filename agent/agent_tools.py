# agent/agent_tools.py (Corrected and Final)

from langchain.tools import tool
import json

# Import the functions we've already built and tested
from .tools import google_search, youtube_search
from .analysis import analyze_results
from .memory import save_curriculum_to_db

@tool
def curriculum_planning_tool(chat_model, topic: str) -> str:
  """
  Use this tool ONLY to generate the initial step-by-step learning plan outline.
  This tool DOES NOT find resources; it only creates the numbered list of module titles.
  Input must be the user's desired learning topic.
  """

  print(f"🤖 Using Curriculum Planning Tool for topic: {topic}")

  planner_prompt = f"Create a step-by-step learning path of 3 simple numbered list for a beginner learning '{topic}'. Donot have more bullet point inside those bullet points, i am just testing something so i donot want to waste API calls"
  # Use LangChain's invoke method instead of generate_content
  plan_response = chat_model.invoke(planner_prompt)
  # LangChain returns an AIMessage object, so we need to get the content
  return plan_response.content

@tool
def resource_search_tool(chat_model, step_description: str) -> str:
  """
  Use this tool for EACH module of the learning plan to find one web article and several YouTube videos.
  The input must be a single, specific step from the learning plan.
  """
  print(f"🤖 Using Resource Search Tool for step: {step_description}")

  search_query_prompt = f"Generate a simple, effective search query for a beginner on: \"{step_description}\". Just the query"
  # Use LangChain's invoke method instead of generate_content
  search_query_response = chat_model.invoke(search_query_prompt)
  search_query = search_query_response.content.strip()
  web_results = google_search(search_query)

  curated_article = analyze_results(web_results, search_query, 'web')
  video_categories = {
    "General": youtube_search(search_query, sort_by='relevance'),
    "Most Viewed": youtube_search(search_query, sort_by="viewCount"),
    "Most Recent": youtube_search(search_query, sort_by="uploadDate")
  }

  curated_videos = {}
  for category, results in video_categories.items():
    curated_videos[category] = analyze_results(results, f"{category} video for {search_query}", "video")
  step_resources = {"step": step_description, "article": curated_article, "videos": curated_videos}
  return json.dumps(step_resources)

@tool
def save_plan_to_database_tool(genai_client, topic: str, full_curriculum_json: str) -> str:
  """
  Use this FINAL tool to save the completed learning plan to the database.
  Input must be the original topic and a JSON string representing the full curriculum.
  """
  print(f"🤖 Using Database Save Tool for topic: {topic}")
  
  try:
    full_curriculum = json.loads(full_curriculum_json)
    save_curriculum_to_db(genai_client, topic, full_curriculum)
    return 'Successfully saved the plan to the database.'
  except Exception as e:
    return f'Error: Failed to save to database. Reason: {e}'