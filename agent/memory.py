import json
import uuid
import numpy as np
from .database import SessionLocal
from .models import Plan, Module, Feedback
from sqlalchemy.orm import joinedload
import tldextract
from sqlalchemy import func

def get_embedding(genai_client, text):
  #Here we are generating a vector embedding for the text
  try:
    result = genai_client.embed_content(model="models/gemini-embedding-001", content=text)
    return result["embedding"]
  except Exception as e:
    raise RuntimeError(f"[Fatal Error] Could not create embedding: {e}")
  
def find_similar_plan_in_db(user_embedding):
  if user_embedding is None:
    return None
  
  SIMILARITY_THRESHOLD = 0.6

  db = SessionLocal()
  try:
    all_plans = db.query(Plan).options(joinedload(Plan.modules)).all()
    if not all_plans:
      return None
    
    best_match = None
    highest_similarity = 0.0
    
    user_vector = np.array(user_embedding)

    for plan in all_plans:
      saved_vector = np.array(plan.embedding)
      cosine_similarity = np.dot(user_vector, saved_vector) / (np.linalg.norm(user_vector) * np.linalg.norm(saved_vector))

      if cosine_similarity > highest_similarity:
        highest_similarity = cosine_similarity
        best_match = plan
    
    if highest_similarity > SIMILARITY_THRESHOLD:
      print(f"  > Found a similar plan in DB ('{best_match.topic}') with similarity: {highest_similarity:.2f}")
      # The 'best_match' object already contains all the modules thanks to the 'relationship'
      return best_match
  
  finally:
    db.close()

  return None

def mark_module_as_complete(module_id: str):
  """Updates the module's status to complete in the database."""
  db = SessionLocal()
  try:
    # First we have to find the module through its unique ID
    module_to_update = db.query(Module).filter(Module.id == module_id).first()
    if module_to_update:
      module_to_update.is_complete = True
      db.commit()
      print(f"Progress saved for module: {module_to_update.title}")
    else:
      print(f"  > Error: Could not find module with ID {module_id} to mark as complete.")
  except Exception as e:
    print(f"  > Error updating database: {e}")
    db.rollback()
  finally:
    db.close()

def save_feedback_to_db(module_id: str, resource_link: str, resource_type: str, source: str, rating: int):
  """Saves a user's feedback rating for a specific resource to the database."""
  db = SessionLocal()
  try:
    new_feedback = Feedback(
      id = str(uuid.uuid4()),
      module_id = module_id,
      resource_link = resource_link,
      resource_type = resource_type,
      source = source,
      rating= rating
    )
    db.add(new_feedback)
    db.commit()
    print(f" > Thank you! your feedback for the {resource_type} has been recorded.")

  except Exception as e:
    print(f"Error saving feedback {e}")
    db.rollback()
  finally:
    db.close()


def get_feedback_summary(topic: str) -> str:
  """Retrieves all feedback for a given topic and creates a summary of liked/disliked resources.
      Using a 'three strikes' rule for disliked sources."""
  db = SessionLocal()
  try:
    # Step 1: Find the plan to get its associated modules
    plan = db.query(Plan).filter(func.lower(Plan.topic) == topic.lower()).first()
    if not plan: return "No past feedback found for this topic."

    modules = db.query(Module).filter(Module.plan_id == plan.id).all()
    module_ids = [m.id for m in modules]
    if not module_ids: return "No past feedback found for this topic."

    # Step 2: Get all feedback for those modules
    all_feedback = db.query(Feedback).filter(Feedback.module_id.in_(module_ids)).all()
    if not all_feedback: return "No past feedback found for this topic."

    # Step 3: Tally the likes and dislikes for each unique source
    source_ratings = {}
    for fb in all_feedback:
      if fb.source not in source_ratings:
        source_ratings[fb.source] = {'likes': 0, 'dislikes': 0}
      if fb.rating >= 4: # 4 or 5 stars is a "like"
        source_ratings[fb.source]['likes'] += 1
      elif fb.rating <= 2: # 1 or 2 stars is a "dislike"
        source_ratings[fb.source]['dislikes'] += 1
    
    # Step 4: Apply our rules to create the final lists
    liked_sources = [source for source, ratings in source_ratings.items() if ratings['likes']>0]

    #Three strike rule
    disliked_sources = [source for source, ratings in source_ratings.items() if ratings['dislikes']>=3]

    # Step 5: Build the summary string for the AI
    summary_parts = []
    if liked_sources:
      summary_parts.append(f"The user has previously LIKED resources from these sources: {liked_sources}.")
    if disliked_sources:
      summary_parts.append(f"The user has previously DISLIKED resources from these sources and they should be AVOIDED: {disliked_sources}.")

    if not summary_parts:
      return "No strong preferences found in past feedback."
    
    return " ".join(summary_parts)
  
  finally:
    db.close()




def save_curriculum_to_db(genai_client, topic, curriculum_data):
  print(f"\n💾 Saving your curriculum for '{topic}' to the database...")
  db = SessionLocal()
  try:
    #creating the vector embedding of the topic
    topic_embedding = get_embedding(genai_client, topic)
    if not topic_embedding:
      print("  [Error] Could not create embedding. Aborting save.")
      return
    
    #Create the main plan record
    new_plan = Plan(
      id=str(uuid.uuid4()), # Generate a unique ID
      topic= topic,
      embedding = topic_embedding,
    )
    db.add(new_plan) # Adding the new plan to the session

    for i, step_data in enumerate(curriculum_data):
      new_module = Module(
        id = str(uuid.uuid4()),
        plan_id = new_plan.id,
        stepNumber = i+1,
        title = step_data['step'],
        articleTitle = step_data['article']['title'],
        articleReason = step_data['article']['reason'],
        articleLink = step_data['article']['link'],
        #Converting the videos dictionary into a json string for storage
        videosJson = json.dumps(step_data['videos'])
      )
      db.add(new_module) #Add the new module to our workspace

    # Committing your work and saving your changes in the database
    db.commit()
    print("✅ Your plan has been saved to the database!")
  except Exception as e:
    print(f"  [Error] Could not save to database: {e}")
    db.rollback() # Incase anything goes wrong, undo all the changes
  finally:
    #End of session
    db.close()

def format_plan_for_display(plan: Plan):
  output = []
  output.append(f"🎉 Here is your complete, detailed learning curriculum! 🎉")
  output.append("==========================================================")

  # Sort modules by step number to ensure they are in order
  sorted_modules = sorted(plan.modules, key=lambda m: m.stepNumber)

  for module in sorted_modules:
    output.append(f"\nModule {module.stepNumber}: {module.title}")
    output.append("----------------------------------------------------------")
    output.append("✍️ Recommended Article/Tutorial:")
    output.append(f"  - Title: {module.articleTitle}")
    output.append(f"    Reason: {module.articleReason}")
    output.append(f"    Link: {module.articleLink}")

    output.append("\n🎓 Recommended YouTube Videos:")
    videos = json.loads(module.videosJson) # Turn the JSON string back into a Python dictionary
    for category, video_info in videos.items():
        output.append(f"  - Best ({category}): {video_info['title']}")
        output.append(f"    Reason: {video_info['reason']}")
        output.append(f"    Link: {video_info['link']}")
    output.append("==========================================================")
  return "\n".join(output)