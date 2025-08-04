from langchain.tools import tool
import json

#Now we import the functions we have built and tested
from .tools import google_search, youtube_search
from .analysis import analyze_results
from .memory import save_curriculum_to_db, get_embedding, find_similar_plan_in_db, format_plan_for_display

#This is a special decorator from langchain that turns a normal python function into a tool
#that the langchain agent can use

@tool
def curriculum_planning_tool(topic: str, chat_model) -> str:
  """
  Use this tool ONLY to generate the initial step-by-step learning plan outline.
  This tool DOES NOT find resources; it only creates the numbered list of module titles.
  Input must be the user's desired learning topic.
  """
  print(f"🤖 Using Curriculum Planning Tool for topic: {topic}")
  planner_prompt = f"Create a step-by-step learning path of 1 modules for a beginner learning '{topic}'. Present as a numbered list."
  plan_response = chat_model.generate_content(planner_prompt)
  return planner_prompt.text

@tool
def resource_search_tool(step_description: str, chat_model) -> str:
  """
  Use this tool for EACH module of the learning plan to find one web article and several YouTube videos.
  The input must be a single, specific step from the learning plan, for example: '1. Understand Stock Market Fundamentals'.
  Returns a JSON string with the found resources for that single step.
  """

  print(f"🤖 Using Resource Search Tool for step: {step_description}")

  search_query_prompt = f"Generate a simple, effective search query for a beginner on: \"{step_description}\". Just the query"
  search_query_response = chat_model.generate_content(search_query_prompt)
  search_query = search_query_response.text.strip()

  web_results = google_search(search_query)
  curated_article = analyze_results(chat_model, web_results, search_query, search_type='web')

  video_categories = {
    "General": youtube_search(search_query, sort_by='relevance'),
    "Most Viewed": youtube_search(search_query, sort_by="viewCount"),
    "Most Recent": youtube_search(search_query, sort_by="uploadDate")
  }

  curated_videos = {}
  for category, results in video_categories.items():
    curated_videos[category] = analyze_results(chat_model, results, f"{category} video for {search_query}", search_type="videos")

  # Bundle the results for this single step
  step_resources = {
    "step": step_description,
    "article": curated_article,
    "videos": curated_videos
  }

  return json.dumps(step_resources)

@tool
def save_plan_to_database_tool(topic: str, full_curriculum_json: str, genai_client) -> str:
  """
  Use this FINAL tool to save the completed learning plan to the database.
  The input must be the original topic and a JSON string representing the full curriculum with all its researched modules.
  """
  print(f"🤖 Using Database Save Tool for topic: {topic}")
  try:
    full_curriculum = json.loads(full_curriculum_json)
    save_curriculum_to_db(genai_client, topic, full_curriculum)
    return 'Successfully saved the plan to database.'
  except Exception as e:
    return f'Error: Failed to save to database. Reason {e}'