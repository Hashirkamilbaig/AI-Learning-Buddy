# agent/analysis.py (The Final, Caching-Enabled, Professional Version)

import json
import hashlib

from agent.memory import get_feedback_summary 

# This is our simple, in-memory cache. It will be reset every time the program runs.
analysis_cache = {}

def analyze_results(model, topic: str, results, query, search_type='web'):
  """
  Asks the AI model to pick the single best result from a list.
  Now includes a cache to avoid re-analyzing the same data and hitting rate limits.
  """
  if not results:
    return {'title': 'N/A', "link": 'N/A', "reason": f"No {search_type} results found."}
  
  # --- 1. Create a Unique Key for the Cache ---
  # We create a unique signature for this specific request by combining the
  # query and the search results. We then hash it to get a simple key.
  cache_key_string = query + json.dumps(results[:5])
  cache_key = hashlib.md5(cache_key_string.encode()).hexdigest()

  # --- 2. Check the Cache ---
  if cache_key in analysis_cache:
      print(f"      CACHE HIT! Reusing previous analysis for '{query}'.")
      return analysis_cache[cache_key]

  print(f"      CACHE MISS! Performing new analysis for {search_type}...")

  feedback_summary = get_feedback_summary(topic)
  
  # --- MODIFIED PROMPT: Now we include the rich statistics! ---
  analysis_prompt = f"""
  You are a helpful learning assistant. From the following list of {search_type} search results for the query "{query}", pick the ONE best result for a complete beginner.

  Search Results (JSON format):
  {json.dumps(results[:5])}

  IMPORTANT CONTEXT:
  - User Feedback Summary: {feedback_summary}
  - For videos, a high 'likeCount' relative to 'viewCount' is a strong signal of quality.
  - A descriptive 'channelTitle' can also indicate a reliable source.
  
  Use all available information, including the user's past feedback and the video statistics, to make your decision. Strongly prefer sources the user has liked and avoid sources the user has disliked.

  Your goal is to return a JSON object with the keys "title", "link", and "reason".
  Your reason should be a one-sentence explanation for your choice, and if you used the feedback or statistics, briefly mention it.
  Provide ONLY the JSON object and nothing else.
  """

  try:
    response = model.invoke(analysis_prompt)
    clean_json_string = response.content.strip().replace('```json', '').replace('```', '')
    analysis_result = json.loads(clean_json_string)
    
    analysis_cache[cache_key] = analysis_result
    
    return analysis_result
  except (json.JSONDecodeError, Exception) as e:
    # We check if the error is a rate limit error to give a better message
    if "429" in str(e) or "ResourceExhausted" in str(e):
        print("      [Error] Rate limit hit during analysis. Try again in a minute.")
        return {"title": "Rate Limit Hit", "link": "#", "reason": "The AI is thinking too fast! Please try again in a minute."}
    
    print(f"      [Error] Could not parse AI response for analysis: {e}")
    return {"title": "Error", "link": "Error", "reason": "Failed to analyze results."}