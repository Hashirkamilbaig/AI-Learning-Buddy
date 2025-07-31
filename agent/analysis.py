import json
import google.generativeai as genai

try:
  with open("SERPER_API_KEY.txt", 'r') as f:
    GEMINI_API_KEY = f.read().strip()
except:
  #error
  raise EnvironmentError("GEMINI_API_KEY.txt not found. Please create the file with your API key.")

#Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# A function for AI to pick the single best option for these search
def analyze_results(results, query, search_type='web'):
  if not results:
    return {'title': 'N/A', "link": 'N/A', "reason": f"No {search_type} results found."}
  
  analysis_prompt = f"""
  You are a helpfull learning assistant. From the following list of {search_type} search results for the query "{query}", pick the ONE best result for the beginner.

  Search Results (JSON format):
  {json.dumps(results[:5])}

  Your goal is to return a JSON object with the keys "title", "link", and "reason".
  The "reason" should be a one-sentence explaination for your choice.
  Provide ONLY the json object and nothing else.
  """

  try:
    response = model.generate_content(analysis_prompt)
    clean_json_string = response.text.strip().replace('```json', '').replace('```', '')
    return json.loads(clean_json_string)
  except (json.JSONDecodeError, Exception) as e:
    print(f"      [Error] Could not parse AI response for analysis: {e}")
    return {"title": "Error", "link": "Error", "reason": "Failed to analyze results."}