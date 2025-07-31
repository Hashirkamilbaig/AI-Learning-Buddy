import google.generativeai as genai

API_KEY = "AIzaSyBCnUbl7C0zWrIYZLtLSnuVBEgRZqwCarM"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

print("Hello I am your AI learning Buddy")
user_topic = input("What big topic do you want to master")

prompt = f"""
You are a excellent curriculum designer. Your task is to create a step-by-step learning path for a complete beginner who wants to learn about {user_topic}

Please provide a list of 5 to 7 main main modules.
Each module should be a single clear step on the learning journey.
Present this as numbered list. Do not add any extra explaination, just the list.
"""

print(f"\nGenerating a learning path for {user_topic}...")

response = model.generate_content(prompt)

print("\nHere is your personalized learning plan:")
print("---------------------------------------")
print(response.text)
print("---------------------------------------")