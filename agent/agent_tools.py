# agent/agent_tools.py (Rate-Limited Version)

import json
import uuid
import time  # Add this import
from .tools import google_search, youtube_search
from .analysis import analyze_results
from .memory import get_embedding
from .database import SessionLocal
from .models import Plan, Module

def curriculum_planning_tool(chat_model, topic: str) -> str:
    """Generate the initial step-by-step learning plan outline."""
    print(f"🤖 Using Curriculum Planning Tool for topic: {topic}")
    
    # Add a small delay before API call
    time.sleep(1)
    
    planner_prompt = f"""
    You are an expert curriculum designer. Your task is to generate a list of main module titles for a learning plan on the topic: '{topic}'.
    IMPORTANT: The output MUST BE a simple, numbered list and NOTHING ELSE. Just provide the main titles for 3 modules.
    Example for 'Learning Guitar': 1. Parts of the Guitar\n2. Basic Chords\n3. First Song
    Now, generate the output for the topic: '{topic}'.
    """
    
    try:
        plan_response = chat_model.invoke(planner_prompt)
        steps = [step.strip() for step in plan_response.content.split('\n') if step.strip()]
        return json.dumps(steps)
    except Exception as e:
        if "429" in str(e) or "ResourceExhausted" in str(e):
            print("⚠️ Rate limit hit during planning. Waiting 60 seconds...")
            time.sleep(60)
            return "Error: Rate limit exceeded. Please try again."
        raise e

def research_and_save_module_tool(chat_model, genai_client, tool_input: dict) -> str:
    """Find resources for a module AND save them to the database."""
    try:
        topic = tool_input['topic']
        step_description = tool_input['step_description']
    except KeyError:
        return "Error: Input dictionary must contain 'topic' and 'step_description' keys."

    print(f"🤖 Researching and Saving Module for step: '{step_description}'")

    # Add delay before API call
    time.sleep(2)
    
    search_query_prompt = f"""
    You are an expert at generating search queries. Your task is to take the following learning topic and create a single, simple, and effective search query for a beginner.

    IMPORTANT: Your output MUST be the search query string and NOTHING ELSE. Do not add numbers, bullets, explanations, quotes, or any extra text.

    Here is a perfect example:
    Input: "1. Understanding the Parts of the Guitar"
    Output: guitar parts for beginners

    Now, generate the output for the following input:
    Input: "{step_description}"
    """
    
    try:
        search_query_response = chat_model.invoke(search_query_prompt)
        search_query = search_query_response.content.strip().replace('"', '')
    except Exception as e:
        if "429" in str(e) or "ResourceExhausted" in str(e):
            print("⚠️ Rate limit hit during search query generation. Waiting 60 seconds...")
            time.sleep(60)
            return "Error: Rate limit exceeded during search query generation."
        raise e
    
    # Search operations (no API calls)
    web_results = google_search(search_query)
    video_categories = {
        "General": youtube_search(search_query, 'relevance'),
        "Most Viewed": youtube_search(search_query, "viewCount"),
        "Most Recent": youtube_search(search_query, "uploadDate")
    }
    
    # Analyze results with rate limiting
    try:
        curated_article = analyze_results(chat_model, web_results, search_query, 'web')
        time.sleep(2)  # Delay between analyses
        
        curated_videos = {}
        for category, results in video_categories.items():
            curated_videos[category] = analyze_results(chat_model, results, f"{category} video for {search_query}", "video")
            time.sleep(2)  # Delay between each video analysis
            
    except Exception as e:
        if "429" in str(e) or "ResourceExhausted" in str(e):
            print("⚠️ Rate limit hit during analysis. Using fallback data...")
            curated_article = {"title": "Manual Research Required", "link": "#", "reason": "Rate limit reached"}
            curated_videos = {"General": {"title": "Manual Research Required", "link": "#", "reason": "Rate limit reached"}}
        else:
            raise e
    
    # Database operations (no API calls except for embedding)
    db = SessionLocal()
    try:
        plan = db.query(Plan).filter(Plan.topic == topic).first()
        if not plan:
            print(f"  > Creating new plan for '{topic}' in the database...")
            try:
                topic_embedding = get_embedding(genai_client, topic)
                if not topic_embedding:
                    return "Error: Could not create embedding for the plan."
            except Exception as e:
                if "429" in str(e):
                    print("⚠️ Rate limit hit during embedding generation.")
                    return "Error: Rate limit exceeded during embedding generation."
                raise e
            
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
        db.rollback()
        return f"Error: Failed to save module. Reason: {e}"
    finally:
        db.close()