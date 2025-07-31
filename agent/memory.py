import re
import json
import os
import numpy as np

#First what we do is Vector and Embedding Functions
def get_embedding(model, text):
  try:
    embedding = model.embed_content(model="models/gemini-embedding-001", content=text)
    return embedding["embedding"]
  except Exception as e:
    raise RuntimeError(f"[Fatal Error] Could not create embedding: {e}")
  
def find_similar_plan(embedding_model, user_embedding):
  """
    Searches for similar plans in the directory and also returns the name of the file if it is matched
  """
  if user_embedding is None:
    return None, None
  
  SIMILARITY_THRESHOLD = 0.6

  for filename in os.listdir('.'):
    if filename.endswith(".npy"):
      try:
        # this is when we load the saved vector
        saved_vector = np.load(filename)

        # We will use that saved vector of that file and use cosine rule to find the similarity and give us the saved plan if available
        cosine_similarity = np.dot(user_embedding, saved_vector) / (np.linalg.norm(user_embedding) * np.linalg.norm(saved_vector))

        if cosine_similarity > SIMILARITY_THRESHOLD:
          print(f"  > Found a similar plan with similarity: {cosine_similarity:.2f}")
          # This is when we will return the orignal topic name and return orignal file
          original_topic = filename.replace('learning_plan_', '').replace('.npy', '').replace('_', ' ')
          text_filename = filename.replace('.npy', '.txt')
          return original_topic, text_filename
      except Exception as e:
        print(f"  [Error] Could not process vector file {filename}: {e}")
  return None, None

def save_curriculum_to_file(embedding_model, topic, curriculum_data):
  """Saves the generated curriculum to a text file"""
  safe_filename_base = re.sub(r'[^a-zA-Z0-9_]', '_', topic)
  text_filename = f"learning_plan_{safe_filename_base}.txt"
  vector_filename = f"learning_plan_{safe_filename_base}.npy"

  print(f"Saving your curriculum to {text_filename}...")
  try:
    #this is saving human readable text file
    with open(text_filename, "w", encoding='utf-8') as f:
      f.write(f"Learning curriculum: {topic}\n")
      f.write("=" * 40 + "\n\n")
      for item in curriculum_data:
        f.write(f"MODULE: {item['step']}\n")
        f.write("-" * 40 + "\n")

        #We have to write article info
        article_info = item['article']
        f.write("Recommended Article/Tutorial:\n")
        f.write(f"  - Title: {article_info['title']}\n")
        f.write(f"    Reason: {article_info['reason']}\n")
        f.write(f"    Link: {article_info['link']}\n\n")

        #Write video info
        f.write("Recommended YouTube Videos:\n")
        for category, video_info in item['videos'].items():
          f.write(f"  - Best ({category}): {video_info['title']}\n")
          f.write(f"    Reason: {video_info['reason']}\n")
          f.write(f"    Link: {video_info['link']}\n")

        f.write("\n" + "=" * 40 + "\n\n")
    
    #Now we have to create and save vector embedding
    print(f"🧠 Creating a memory embedding for '{topic}'...")

    topic_embedding = get_embedding(embedding_model, topic)
    if topic_embedding:
      np.save(vector_filename, topic_embedding)
    print("✅ Your plan has been saved!")

  except IOError as e:
    print(f"[Error] Could not save file: {e}")