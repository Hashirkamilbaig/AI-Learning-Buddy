# File: agent_backend/agent/tools.py

import os
import requests
import json

from googleapiclient.discovery import build
from . import config
from .logger import logger
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound, YouTubeTranscriptApi


# Now to our new tool
def google_search(query: str):
  url = "https://google.serper.dev/search"
  payload = json.dumps({'q' : query})
  headers = {
    'X-API-KEY' : config.SERPER_API_KEY,
    'Content-Type': 'application/json'
  }

  print(f" > Web searching for: {query}...")

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
        order=order
      ).execute()

      video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
      if not video_ids: return []
      
      video_response = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(video_ids)
      ).execute()

      rich_results = []
      for item in video_response.get('items', []):
        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})
        rich_results.append({
            'title': snippet.get('title'),
            'link': f"https://www.youtube.com/watch?v={item.get('id')}",
            'channelTitle': snippet.get('channelTitle'),
            'viewCount': int(stats.get('viewCount', 0)),
            'likeCount': int(stats.get('likeCount', 0)),
            # ==================================================================
            # THE ONLY CHANGE IS ADDING THIS LINE
            # ==================================================================
            'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url')
        })
      return rich_results
  except Exception as e:
    logger.error(f"Could not perform YouTube search: {e}")
    return []



#New function to get youtube transcript
def get_youtube_transcript(video_url: str) -> str:
  """
  Fetches the transcript for a given YouTube video URL.
  Returns the transcript text or an error message string.
  """
  logger.info(f"Fetching Transcript for video: {video_url}")
  try:
      if "youtu.be/" in video_url:
          video_id = video_url.split("youtu.be/")[-1].split("?")[0].split("&")[0]
      elif "watch?v=" in video_url:
          video_id = video_url.split("v=")[-1].split("&")[0]
      elif "embed/" in video_url:
          video_id = video_url.split("embed/")[-1].split("?")[0].split("&")[0]
      else:
          return "Error: Could not extract video ID from the URL."
      
      if not video_id:
          return "Error: Could not extract video ID from the URL."
      
      logger.info(f"Extracted video ID: {video_id}")
      
      ytt_api = YouTubeTranscriptApi()
      transcript_data = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])

      transcript_text = ""
      for snippet in transcript_data:
          minutes, seconds = divmod(int(snippet.start), 60)
          timestamp = f"[{minutes:02d}:{seconds:02d}]"
          transcript_text += f"{timestamp} {snippet.text}\n"
          
      print(transcript_text)    
      return transcript_text

  except (TranscriptsDisabled, NoTranscriptFound):
      logger.warning(f"No transcript found or transcripts are disabled for video: {video_id}")
      return "Error: No transcript is available for this video."
  except Exception as e:
      logger.error(f"An unexpected error occurred while fetching transcript: {e}")
      return f"Error: An unexpected error occurred: {e}"