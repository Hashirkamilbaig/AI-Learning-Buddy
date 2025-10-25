# File: agent_backend/agent_brain_optimized.py

import json
import google.generativeai as genai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
import tldextract
from agent import config
from agent.logger import logger
import re
import sys 

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

def plan_to_dict(plan):
    if not plan:
        return None
    sorted_modules = sorted(plan.modules, key=lambda m: m.stepNumber)
    return {
        "id": plan.id,
        "topic": plan.topic,
        "modules": [
            {
                "id": module.id,
                "stepNumber": module.stepNumber,
                "title": module.title,
                "is_complete": module.is_complete,
                "articleTitle": module.articleTitle,
                "articleReason": module.articleReason,
                "articleLink": module.articleLink,
                "videos": json.loads(module.videosJson) 
            }
            for module in sorted_modules
        ]
    }

def interactive_session(plan):
	logger.info("Plan loaded, Entering interactive session.")
	print("Commands: 'next', 'quit', 'view plan', 'notes <video_number>' (e.g., 'notes 1')")
	while True:
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
		videos = json.loads(current_module.videosJson)
		video_list = []
		print("  Available Videos for Notes:")
		for i, (category, video_info) in enumerate(videos.items()):
				print(f"    {i+1}: [{category}] {video_info['title'][:60]}...")
				video_list.append(video_info)
		user_command = input("> ").lower().strip()
		if user_command == 'quit':
			logger.info("User quit the interactive session.")
			print("Saving your progress. See you next time!")
			break
		elif user_command == 'next':
			print("\nGreat! Before we move on, how helpful were the resources for this module?")
			article_url = current_module.articleLink
			extracted_article = tldextract.extract(article_url)
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
		elif user_command.startswith("notes"):
			try:
					parts = user_command.split()
					if len(parts) < 2:
							print("  Invalid format. Please use 'notes <video_number>', e.g., 'notes 1'.")
							continue
					video_number = int(parts[1])
					if 1 <= video_number <= len(video_list):
							selected_video = video_list[video_number - 1]
							video_url = selected_video['link']
							print(f"\n🤖 Generating notes for: '{selected_video['title']}'...")
							notes = youtube_note_taker_tool.invoke({ "video_url": video_url, "module_id": current_module.id })
							print("\n--- Generated Notes ---")
							print(notes)
							print("-----------------------")
					else:
							print(f"  Invalid video number. Please choose a number between 1 and {len(video_list)}.")
			except (ValueError, IndexError):
					print("  Invalid command. Please use 'notes <video_number>', e.g., 'notes 1'.")
		else:
			print("Unknown command. Available commands: 'next', 'quit', 'view plan'")


def main():
	"""Main function to run the AI Learning Buddy as a LangChain Agent."""
	
	genai.configure(api_key=config.GEMINI_API_KEY)

	# FIXED: Added google_api_key parameter
	llm = ChatGoogleGenerativeAI(
		model=config.CHAT_MODEL_NAME, 
		temperature=0.5, 
		convert_system_message_to_human=True,
		google_api_key=config.GEMINI_API_KEY
	)
	
	set_models(llm, genai)
	tools = [curriculum_planning_tool, research_and_save_module_tool]
	prompt = hub.pull("hwchase17/react")
	agent = create_react_agent(llm, tools, prompt)
	agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

	if len(sys.argv) > 1:
		user_input = sys.argv[1]
	else:
		user_input = input("How can I help you learn today? (Enter a topic, or a YouTube link for notes): ")

	youtube_regex = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
	is_youtube_link = re.match(youtube_regex, user_input)

	if is_youtube_link:
		logger.info(f"YouTube link detected. Running Note-Taker tool for: {user_input}")
		notes = youtube_note_taker_tool.invoke({"video_url": user_input})
		print(json.dumps({"notes": notes}))
		return

	user_topic = user_input
	logger.info(f"User requested topic: '{user_topic}'")
	user_topic_embedding = get_embedding(genai, user_topic)
	found_plan = find_similar_plan_in_db(user_topic_embedding)

	if found_plan:
		logger.info(f"Found similar plan for '{found_plan.topic}'. Returning existing plan.")
		plan_dict = plan_to_dict(found_plan)
		print(json.dumps(plan_dict))
		return
	
	logger.info(f"No existing plan found. Launching LangChain agent for '{user_topic}'.")
	
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
	logger.info("Fetching newly created plan from the database...")
	newly_created_plan = find_similar_plan_in_db(user_topic_embedding)
	
	if newly_created_plan:
		plan_dict = plan_to_dict(newly_created_plan)
		print(json.dumps(plan_dict))
	else:
		error_message = {"error": "Failed to create or retrieve the learning plan."}
		print(json.dumps(error_message))

if __name__ == "__main__":
	main()