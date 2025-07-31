# This is import from the toolkit we just installed
import google.generativeai as genai

API_KEY = "AIzaSyBCnUbl7C0zWrIYZLtLSnuVBEgRZqwCarM"

# Now to connect AI to our Api Key
genai.configure(api_key=API_KEY)

# We have to select a model now to use for our thinking process
model = genai.GenerativeModel('gemini-2.5-flash')

#Now we test
print("The brain is awake! Ask it a question...")

response = model.generate_content("In one sentence, what is the most exciting thing about learning to code")

# Now we print the answers
print("\nGemini Says:")
print(response.text)