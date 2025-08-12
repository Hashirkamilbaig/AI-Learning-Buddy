import os
import requests
import json
from . import config


# Now to our new tool
def google_search(query: str):
  url = "https://google.serper.dev/search"
  payload = json.dumps({'q' : query})
  headers = {
    'X-API-KEY' : config.SERPER_API_KEY,
    'Content-Type': 'application/json'
  }

  print(f" > Web searching for: {query}...")
  #response = requests.request("Post",url, headers=headers, data=payload)

  # Now we try to get top 5 search results and pick the best one
  try:
    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json().get('organic',[])
  except requests.exceptions.RequestException as e:
    print(f"[Error] could not perform a web search: {e}")
    return[]
  
# Now we have to get to work on the youtube search
def youtube_search(query: str, sort_by: str = 'relevance'):
  url = "https://google.serper.dev/videos"
  payload = json.dumps({"q": query, "gl": "us", "hl": "en", "sort_by": sort_by})
  headers = {
      'X-API-KEY': config.SERPER_API_KEY,
      'Content-Type': 'application/json'
  }
  print(f">YouTube Search ({sort_by}): {query}...")
  
  try:
    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json().get('videos',[])
  except requests.exceptions.RequestException as e:
    print(f"[Error] Could not perform YouTube search: {e}")
    return []