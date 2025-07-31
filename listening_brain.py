import google.generativeai as genai

API_KEY = "AIzaSyBCnUbl7C0zWrIYZLtLSnuVBEgRZqwCarM"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

print('Hello! I am your AI Learning Buddy: \n')
user_topic = input("What would you like to learn today?")

print(f"\n Okay thinking about '{user_topic}'...")
response = model.generate_content(f"Explain the absolute basics of {user_topic} to a complete beginner in three simple points")

print("\nGEMINI SAYS:")
print(response.text)