# agent/agent_tools.py (Simple @tool decorator version)

import json
import uuid
import google.generativeai as genai
from langchain.tools import tool
from .tools import google_search, youtube_search, get_youtube_transcript
from .analysis import analyze_results
from .memory import get_embedding
from .database import SessionLocal
from .models import Plan, Module
from .logger import logger

# Global variables to store the models (will be set from main)
_chat_model = None
_genai_client = None

def set_models(chat_model, genai_client):
	"""Set the global model instances for use in tools"""
	global _chat_model, _genai_client
	_chat_model = chat_model
	_genai_client = genai_client

@tool
def curriculum_planning_tool(topic: str) -> str:
	"""Generate the initial step-by-step learning plan outline.
	
	Args:
			topic: The learning topic to create a curriculum for
			
	Returns:
			JSON string containing a list of module titles
	"""
	logger.info(f"Using Curriculum Planning Tool for topic: {topic}")

	planner_prompt = f"""
	You are an expert curriculum designer. Your task is to generate a list of main module titles for a learning plan on the topic: '{topic}'.
	IMPORTANT: The output MUST BE a simple, numbered list and NOTHING ELSE. Just provide the main titles for 3 modules.
	Example for 'Learning Guitar': 1. Parts of the Guitar\n2. Basic Chords\n3. First Song
	Now, generate the output for the topic: '{topic}'.
	"""

	plan_response = _chat_model.invoke(planner_prompt)
	steps = [step.strip() for step in plan_response.content.split('\n') if step.strip()]
	return json.dumps(steps)

@tool
def research_and_save_module_tool(tool_input: str) -> str:
	"""Find resources for a module AND save them to the database.
	
	Args:
			tool_input: String in format "topic=TOPIC_NAME, step_description=MODULE_TITLE"
			
	Returns:
			Success or error message
	"""
	# Parse the input string
	try:
		# Simple parser for "topic=Python, step_description=Learn Basics"
		input_dict = {}
		pairs = tool_input.split(',')
		for pair in pairs:
				if '=' in pair:
						key, value = pair.split('=', 1)
						input_dict[key.strip()] = value.strip()
		
		topic = input_dict['topic']
		step_description = input_dict['step_description']
	except (KeyError, ValueError):
		return "Error: Input must be in format 'topic=TOPIC_NAME, step_description=MODULE_TITLE'"

	logger.info(f"Researching and Saving Module for step: '{step_description}'")
	
	search_query_prompt = f"""
	You are an expert at generating search queries. Your task is to take the following learning topic and create a single, simple, and effective search query for a beginner.

	IMPORTANT: Your output MUST be the search query string and NOTHING ELSE. Do not add numbers, bullets, explanations, quotes, or any extra text.

	Here is a perfect example:
	Input: "1. Understanding the Parts of the Guitar"
	Output: guitar parts for beginners

	Now, generate the output for the following input:
	Input: "{step_description}"
	"""
	
	search_query_response = _chat_model.invoke(search_query_prompt)
	search_query = search_query_response.content.strip().replace('"', '')
	
	# Search operations (no API calls)
	web_results = google_search(search_query)
	video_categories = {
		"General": youtube_search(query=search_query, order='relevance'),
		"Most Viewed": youtube_search(query=search_query, order="viewCount"),
		"Highest Rated": youtube_search(query=search_query, order="rating") 
	}
	
	# Analyze results
	curated_article = analyze_results(_chat_model, topic, web_results, search_query, 'web')
	
	curated_videos = {}
	for category, results in video_categories.items():
		curated_videos[category] = analyze_results(_chat_model, topic, results, f"{category} video for {search_query}", "video")
	
	try:
		logger.info(f"Connecting to database to save module: '{step_description}'")
		db = SessionLocal()

		plan = db.query(Plan).filter(Plan.topic == topic).first()
		if not plan:
				print(f"  > Creating new plan for '{topic}' in the database...")
				topic_embedding = get_embedding(_genai_client, topic)
				
				plan = Plan(id=str(uuid.uuid4()), topic=topic, embedding=topic_embedding)
				db.add(plan)
				db.commit()
				db.refresh(plan)

		current_step_count = db.query(Module).filter(Module.plan_id == plan.id).count()
		
		new_module = Module(
				id=str(uuid.uuid4()),
				plan_id=plan.id,
				stepNumber=current_step_count + 1,
				title=step_description,
				articleTitle=curated_article['title'],
				articleReason=curated_article['reason'],
				articleLink=curated_article['link'],
				videosJson=json.dumps(curated_videos)
		)
		db.add(new_module)
		db.commit()

		return f"Successfully researched and saved module: '{step_description}'"
		
	except Exception as e:
		logger.error(f"Failed to save module to database. Reason: {e}")
		db.rollback()
		return f"Error: Failed to save module. Reason: {e}"
	finally:
		db.close()

@tool
def youtube_note_taker_tool(video_url: str) -> str:
	"""
	Use this tool to generate timestamped notes for a specific YouTube video.
	The input MUST be a valid YouTube video URL.
	This tool fetches the video transcript and uses an AI to summarize it into key concepts with timestamps.
	"""
	logger.info(f"Using YouTube Note Taker Tool for URL: {video_url}")

	#Step 1: Get transcript using our specialist function
	transcript = get_youtube_transcript(video_url)
	if transcript.startswith("Error:"):
		return transcript
	
	#Step 2: Engineer the powerful summarizer prompt
	note_taker_prompt = f"""
	You are an expert academic note-taker. Your task is to analyze the following video transcript and distill it into a set of key concepts.

	The transcript is provided with timestamps in the format [MM:SS].

	Your instructions are:
	1.  Identify the main, high-level concepts discussed in the video.
	2.  For each concept, provide a concise, 2-3 sentence summary.
	3.  Crucially, for each summary, you MUST provide the starting timestamp (e.g., [02:35]) where that concept is first introduced in the transcript.
	4.  Format your output as a clean, structured list. Do not add any conversational fluff or introductory sentences.

	Here is the transcript:
	---
	{transcript[:12000]} 
	---
	""" 
	# We truncate the transcript to avoid exceeding model token limits

	# Step 3: Use the AI to generate the notes
	notes_response = _chat_model.invoke(note_taker_prompt)

	# We can add database saving logic here later if we want!
	# For now, it just returns the notes.

	return notes_response.content