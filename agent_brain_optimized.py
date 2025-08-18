import json
import google.generativeai as genai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
import tldextract
from agent import config
from agent.logger import logger
os.environ['GOOGLE_API_KEY'] = config.GEMINI_API_KEY
import re

# Import our decorated tools and the model setter
from agent.agent_tools import (
	curriculum_planning_tool,
	research_and_save_module_tool,
	set_models,
	youtube_note_taker_tool
)
from agent.memory import (
	find_similar_plan_in_db,
	get_embedding,
	format_plan_for_display,
	mark_module_as_complete,
	save_feedback_to_db
	)

def interactive_session(plan):
	"""Handles the user interaction after the plan is loaded."""
	logger.info("Plan loaded, Entering interactive session.")
	print("Commands: 'next', 'quit', 'view plan'")
	
	while True:
		# Find the first module that is NOT complete
		current_module = None
		sorted_modules = sorted(plan.modules, key=lambda m: m.stepNumber)
		for module in sorted_modules:
			if not module.is_complete:
				current_module = module
				break

		if current_module is None:
			logger.info("All modules for this plan are complete.")
			print("\n🎉 Congratulations! You have completed all modules for this plan! 🎉")
			break

		print("-"* 50)
		print(f"Current Step ({current_module.stepNumber}/{len(plan.modules)}): {current_module.title}")
		user_command = input("> ").lower().strip()

		if user_command == 'quit':
			logger.info("User quit the interactive session.")
			print("Saving your progress. See you next time!")
			break
		elif user_command == 'next':
			print("\nGreat! Before we move on, how helpful were the resources for this module?")

			#For the article
			article_url = current_module.articleLink
			extracted_article = tldextract.extract(article_url)
			# This logic correctly identifies specific sources like 'youtube.com'
			if extracted_article.subdomain and extracted_article.subdomain != 'www':
				article_source = f"{extracted_article.subdomain}.{extracted_article.domain}.{extracted_article.suffix}"
			else:
				article_source = extracted_article.registered_domain

			if not article_source.strip('.'):
				article_source = "Unknown Website"

			while True:
				try:
					article_rating = int(input(f"  - Rate the article from '{article_source}' (1 to 5): '{current_module.articleTitle[:50]}...'\n > "))
					if 1<= article_rating <= 5:
						save_feedback_to_db(current_module.id, current_module.articleLink, 'article', article_source, article_rating)
						break
					else: print(" Please enter a number between 1 and 5.")
				except ValueError: print("  Invalid input. Please enter a number.")
			
			#for videos
			videos = json.loads(current_module.videosJson)
			for category, video_info in videos.items():
				video_source = 'youtube.com'
				while True:
					try:
						video_rating = int(input(f"  - Rate the '{category}' video from YouTube (1-5): '{video_info['title'][:50]}...'\n  > "))
						if 1 <= video_rating <= 5:
							save_feedback_to_db(current_module.id, video_info['link'], 'video', video_source, video_rating)
							break
						else: print("  Please enter a number between 1 and 5.")
					except ValueError: print("  Invalid input. Please enter a number.")

			mark_module_as_complete(current_module.id)
			current_module.is_complete = True

		elif user_command == 'view plan':
			print("\nLoading your plan...\n")
			print(format_plan_for_display(plan))
		else:
			print("Unknown command. Available commands: 'next', 'quit', 'view plan'")



def main():
	"""Main function to run the AI Learning Buddy as a LangChain Agent."""
	genai.configure(api_key=config.GEMINI_API_KEY)

	llm = ChatGoogleGenerativeAI(model=config.CHAT_MODEL_NAME, temperature=0.5, convert_system_message_to_human=True)
	
	# Set the models for the tools to
	set_models(llm, genai)

	# The tools are now automatically available as decorated functions
	tools = [curriculum_planning_tool, research_and_save_module_tool]

	prompt = hub.pull("hwchase17/react")
	agent = create_react_agent(llm, tools, prompt)
	agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

	logger.info("Hello! I am your AI Learning Buddy (LangChain edition)")
	user_input = input("How can I help you learn today? (Enter a topic, or a YouTube link for notes): ")

	# Check if the input is a YouTube URL
	youtube_regex = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
	is_youtube_link = re.match(youtube_regex, user_input)

	if is_youtube_link:
			# --- Run the Note-Taker Workflow ---
			logger.info(f"YouTube link detected. Running Note-Taker tool for: {user_input}")
			# Use the new invoke method instead of direct call
			notes = youtube_note_taker_tool.invoke({"video_url": user_input})
			print("\n--- Generated Notes ---")
			print(notes)
			print("-----------------------")
			return # The job is done

	user_topic = user_input
	logger.info(f"User requested topic: '{user_topic}'")

	logger.info("Checking database for similar plans...")
	user_topic_embedding = get_embedding(genai, user_topic)
	found_plan = find_similar_plan_in_db(user_topic_embedding)

	if found_plan:
		logger.info(f"Found similar plan for '{found_plan.topic}'. Prompting user.")
		print(f"\n🧠 I found a very similar plan for '{found_plan.topic}' in my database!")
		load_plan = input("Do you want to load this saved plan? (yes/no): ")
		if load_plan.lower() == 'yes':
				#print("\nLoading your plan from the database...\n")
				#print(format_plan_for_display(found_plan))
				interactive_session(found_plan)
				return
	
	logger.info(f"No existing plan found or user declined load. Launching LangChain agent for '{user_topic}'.")
	print(f"\n🤖 Launching LangChain agent to create a new plan for '{user_topic}'...")
	
	result = agent_executor.invoke({
		"input": f"Your mission is to create and save a learning plan for the topic: '{user_topic}'. "
							"Follow these steps precisely: "
							"1. First, use the 'curriculum_planning_tool' with input '{user_topic}' to get a JSON list of module titles. "
							"2. Then, for EACH module title in that JSON list, you MUST use the 'research_and_save_module_tool'. "
							"For the research_and_save_module_tool, the input format must be: topic={user_topic}, step_description=MODULE_TITLE "
							"3. After you have called the research tool for ALL modules, your job is done. "
							"Your final answer should be a single sentence confirming the plan has been successfully created and saved."
	})
	
	logger.info("LangChain agent has finished its work.")
	print("\n✅ Agent has finished its work.")
	print(f"Final output: {result['output']}")

	print("\nWould you like to start this new plan now?")
	start_now = input("(Yes/No): ").lower().strip()
	if start_now == "yes":
		logger.info("User chose to start the newly created plan.")
		print("\n🧠 Loading the new plan...")
		newly_created_plan = find_similar_plan_in_db(user_topic_embedding)
		
		if newly_created_plan:
			interactive_session(newly_created_plan)
		else:
			logger.error("Failed to load the newly created plan for an interactive session.")

if __name__ == "__main__":
	main()