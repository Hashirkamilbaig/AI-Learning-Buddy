import google.generativeai as genai
import os
import requests #This is the library to make web requests
import json # Library for handling JSON data from the web

# Getting keys from there apikey file instead of copy pasting each time

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
model = genai.GenerativeModel("gemini-2.5-flash")

# Now to our new tool
def google_search(query: str):
  url = "https://google.serper.dev/search"
  payload = json.dumps({'q' : query})
  headers = {
    'X-API-KEY' : SERPER_API_KEY,
    'Content-Type': 'application/json'
  }

  print(f" > Searching for: {query}...")
  response = requests.request("Post",url, headers=headers, data=payload)

  # Check if the search was successful
  if response.status_code == 200:
      results = response.json()
      # Let's check if there are organic results
      if 'organic' in results:
          return results['organic']
  return [] # Return empty list if search fails or has no results

#Main agent logic 
print("Hello! I am your AI Learning Buddy.")
user_topic = input("What amazing thing do you want to learn today? ")

# == STEP 1: The AI generates a learning plan ==
print(f"\n🗺️ Generating a learning path for '{user_topic}'...")
planner_prompt = f"""
You are an expert curriculum designer. Your task is to create a step-by-step learning path for a complete beginner who wants to learn about '{user_topic}'.
Please provide a list of 5 to 7 main learning modules. 
Each module should be a single, clear step on the learning journey.
Present this as a numbered list. Do not add any extra explanations, just the list.
"""
plan_response = model.generate_content(planner_prompt)
learning_plan = plan_response.text

print("\nHere is your personalized learning plan:")
print("---------------------------------------")
print(learning_plan)
print("---------------------------------------")

# Step 2
print("\nLets find the resource for the first step")

# We have to extract first line from the plan
first_step = learning_plan.split("\n")[0]

#Step 3 is basically finding a good search query to search for the first step
search_prompt = f"""
Based on the following learning step: "{first_step}", generate the best possible, simple search
query a beginner would use to find a high-quality tutorial video or article.
Provide only the search query itself, nothing else
"""

search_response = model.generate_content(search_prompt)
search_query = search_response.text.strip()

# Step 4: The agent uses the tool to search using that prompt
search_results = google_search(search_query)

# Step 5: The AI analyzes the search query and also we have to check if we got any results back

if not search_results:
  print("\nI couldn't find any good resources for that step. Let's try another topic")
else:
  # We will ask AI to pick the best one possible from those search_results
  analysis_prompt = f"""
  You are a helpful learning assistant. I have perfomed a web search for a beginner learning about the topic "{user_topic}"
  Here are some top search results in JSON format:
  {json.dumps(search_results[:5])}

  Please analyse the results and pick ONE best resource (Link) for complete beginner.
  Your criteria should be: a title that sounds like a tutorial or guide, and a snippet that is easy to understand.

  First explain in one sentence why you chose that specific link.
  Then, provide the chosen title and link.
  Format your response like this
  REASON: [Your one sentence reason]
  TITLE: [The title of the article/video]
  Link: [The URL]
"""
  analysis_response = model.generate_content(analysis_prompt)

  print("\nHere is the best resource I found for you to start with:")
  print(analysis_response.text)