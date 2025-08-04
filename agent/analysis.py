# agent/analysis.py (The Final, Caching-Enabled, Professional Version)

import json
import hashlib # We need this to create a unique "fingerprint" for our cache

# This is our simple, in-memory cache. It will be reset every time the program runs.
analysis_cache = {}

def analyze_results(model, results, query, search_type='web'):
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
  
  analysis_prompt = f"""
  You are a helpful learning assistant. From the following list of {search_type} search results for the query "{query}", pick the ONE best result for a complete beginner.

  Search Results (JSON format): {json.dumps(results[:5])}

  Your goal is to return a JSON object with the keys "title", "link", and "reason".
  The "reason" should be a one-sentence explanation for your choice.
  Provide ONLY the JSON object and nothing else.
  """

  try:
    response = model.invoke(analysis_prompt)
    clean_json_string = response.content.strip().replace('```json', '').replace('```', '')
    analysis_result = json.loads(clean_json_string)
    
    # --- 3. Save to Cache ---
    # Store the new result in our cache before returning it.
    analysis_cache[cache_key] = analysis_result
    
    return analysis_result
  except (json.JSONDecodeError, Exception) as e:
    # We check if the error is a rate limit error to give a better message
    if "429" in str(e) or "ResourceExhausted" in str(e):
        print("      [Error] Rate limit hit during analysis. Try again in a minute.")
        return {"title": "Rate Limit Hit", "link": "#", "reason": "The AI is thinking too fast! Please try again in a minute."}
    
    print(f"      [Error] Could not parse AI response for analysis: {e}")
    return {"title": "Error", "link": "Error", "reason": "Failed to analyze results."}