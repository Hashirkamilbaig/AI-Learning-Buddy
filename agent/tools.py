import os
import requests
import json

from googleapiclient.discovery import build
from . import config
from .logger import logger


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
def youtube_search(query: str, order: str = 'relevance', max_results=5):
  """
  Performs a YouTube search using the official YouTube API v3.
  'order' can be 'relevance', 'viewCount', or 'date'.
  """
  logger.info(f"YouTube Search (Official API, order by {order}): {query}...")
  try:
      youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)

      search_response = youtube.search().list(
        q=query,
        part='id',
        maxResults=max_results,
        type='video',
        # --- THE FIX ---
        # We now use the 'order' parameter here.
        order=order
      ).execute()

      video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
      if not video_ids: return []
      
      video_response = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids)
      ).execute() # <-- This was missing parentheses in your provided code, a critical bug.

      rich_results = []
      for item in video_response.get('items', []):
        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})
        rich_results.append({
            'title': snippet.get('title'),
            'link': f"https://www.youtube.com/watch?v={item.get('id')}",
            'channelTitle': snippet.get('channelTitle'),
            'viewCount': int(stats.get('viewCount', 0)),
            'likeCount': int(stats.get('likeCount', 0))
        })
      return rich_results
  except Exception as e:
    logger.error(f"Could not perform YouTube search: {e}")
    return []