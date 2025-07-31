import google.generativeai as genai
import os
import re
import json # Library for handling JSON data from the web
from agent.tools import google_search, youtube_search
from agent.analysis import analyze_results
from agent.memory import save_curriculum_to_file, get_embedding, find_similar_plan


def main():
  try:
    with open("GEMINI_API_KEY.txt", 'r') as f:
      GEMINI_API_KEY = f.read().strip()
    with open("SERPER_API_KEY.txt", "r") as f:
      SERPER_API_KEY = f.read().strip()
  except FileNotFoundError:
    print("ERROR: Make sure you have your API keys in files named 'GEMINI_API_KEY.txt' and 'SERPER_API_KEY.txt'")
    exit()

  #Configure the Gemini API
  genai.configure(api_key=GEMINI_API_KEY)
  chat_model = genai.GenerativeModel("gemini-2.5-flash")


  #Main agent logic 
  print("Hello! I am your AI Learning Buddy.")
  user_topic = input("What amazing thing do you want to learn today? ")

  user_topic_embedding = get_embedding(genai, user_topic)
  found_topic, plan_filename = find_similar_plan(genai, user_topic_embedding)

  if found_topic:
    print(f"\n I found a very similar plan for '{found_topic}' in my memory!")
    load_plan = input("Do you want to load this saved plan? (yes/no): ")
    if load_plan.lower() == 'yes':
      print(f"\nLoading your plan from '{plan_filename}'...\n")
      with open(plan_filename, 'r', encoding='utf-8') as f:
        print(f.read())
      return

  """##This is where I will start implementing the Memory logic
  safe_topic_filename = re.sub(r'[^a-zA-Z0-9_]', '_', user_topic)
  memory_file = f"learning_plan_{safe_topic_filename}.txt"

  if os.path.exists(memory_file):
    print("\nI found a learning plan for this topic in my memory")
    load_plan = input("Do you want to load the saved plan? Only reply with yes or no:")
    if load_plan == "yes":
      print(f"Loading you plan from {memory_file}...\n")
      with open(memory_file, 'r', encoding='utf-8') as f:
        print(f.read())
      return"""
  
  #If no memory is shown then we can just proceed with the usual code:
  print(f"\nOK! Generating a new learning path for '{user_topic}'...")

  # == STEP 1: The AI generates a learning plan ==
  print(f"\n🗺️ Generating a learning path for '{user_topic}'...")
  planner_prompt = f"""
  You are an expert curriculum designer. Your task is to create a step-by-step learning path for a complete beginner who wants to learn about '{user_topic}'.
  Please provide 1 main learning modules. 
  Each module should be a single, clear step on the learning journey.
  Present this as a numbered list. Do not add any extra explanations, just the list.
  """
  plan_response = chat_model.generate_content(planner_prompt)
  learning_plan_text = plan_response.text
  learning_steps = [step.strip() for step in learning_plan_text.split('\n') if step.strip()]


  print("\nHere is your personalized learning plan:")
  print("---------------------------------------")
  print(learning_plan_text)
  print("---------------------------------------")

  full_curriculum = []
  for steps in learning_steps:
    print(f"\nResearching resources for step:\"{steps}\"")

    search_query_prompt = f"Generate a simple, effective search query for a beginner to find a tutorial on: \"{steps}\". Just the query, no extra text."
    search_query_response = chat_model.generate_content(search_query_prompt)
    search_query = search_query_response.text.strip()

    #First find the best articles
    web_results = google_search(search_query)
    curated_article = analyze_results(web_results, search_query, search_type='web')

    #Second find the best videos
    video_categories = {
      "General": youtube_search(search_query, sort_by='relevance'),
      "Most Viewed": youtube_search(search_query, sort_by="viewCount"),
      "Most Recent": youtube_search(search_query, sort_by="uploadDate")
    }

    curated_videos = {}
    for category, results in video_categories.items():
      print(f"  > Analyzing '{category}' videos...")
      curated_videos[category] = analyze_results(results, f"{category} video for {search_query}", search_type='video')
    
    full_curriculum.append({
      "step": steps,
      "article": curated_article,
      "videos": curated_videos
    })

    ##Another Memory implementation
    save_curriculum_to_file(genai, user_topic, full_curriculum)

  #FINAL PRESENTATION
  print("\n\nHere is your complete, detailed learning curriculum! 🎉")
  print("==========================================================")

  for item in full_curriculum:
    print(f"\nMODULE: {item['step']}")
    print("----------------------------------------------------------")
    
    print("Recommended Article/Tutorial:")
    article_info = item["article"]
    print(f"  - Title: {article_info['title']}")
    print(f"    Reason: {article_info['reason']}")
    print(f"    Link: {article_info['link']}")
    print("Recommended Youtube Videos:")
    for category, video_info in item['videos'].items():
      print(f"  - Best ({category}): {video_info['title']}")
      print(f"    Reason: {video_info['reason']}")
      print(f"    Link: {video_info['link']}")
    print("==========================================================")

if __name__ == "__main__":
  main()