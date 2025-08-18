from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
import datetime

from .database import Base

class Plan(Base):
  __tablename__ = 'plans' # The names of the table

  id = Column(String, primary_key=True, index=True)
  topic = Column(String, unique=True, index=True)
  embedding = Column(ARRAY(Float)) # this is a special coloum type for a list of numbers
  createdAt = Column(DateTime, default=datetime.datetime.utcnow)

  #This is creating a link: a plan can have many modules
  modules = relationship("Module", back_populates="plan")

class Module(Base):
  __tablename__ = 'modules'

  id = Column(String, primary_key=True, index=True)
  stepNumber = Column(Integer)
  title = Column(String)

  #The progress tracker
  is_complete = Column(Boolean, default=False, nullable=False)

  articleTitle = Column(String)
  articleReason = Column(String)
  articleLink = Column(String)

  videosJson = Column(String) # We will store the videos list as a JSON text block

  # This is the foreign key that links this module back to a specific plan
  plan_id = Column(String, ForeignKey('plans.id'))
  plan = relationship("Plan", back_populates="modules")

  # Adding another relationship the links modules with feedback
  feedback = relationship("Feedback", back_populates="module")
  
  #A new relationship for notes
  notes = relationship("Note", back_populates="module")

# A new class for our new table called feedback
class Feedback(Base):
  __tablename__ = 'feedback'

  id = Column(String, primary_key=True, index=True)
  rating = Column(Integer) # 1 to 5
  resource_type = Column(String) # 'article' or 'video'
  resource_link = Column(String)

  source = Column(String, index=True)
  createdAt = Column(DateTime, default=datetime.datetime.utcnow)

  #Linking feedback with its respective module
  module_id = Column(String, ForeignKey('modules.id'))
  module = relationship("Module", back_populates="feedback")

class Note(Base):
  __tablename__ = 'notes'

  id = Column(String, primary_key=True, index=True)
  video_link = Column(String, index=True)
  
  #The text type is to store very long strings, like our notes.
  content = Column(Text)
  createdAt = Column(DateTime, default=datetime.datetime.utcnow)

  # This links the note back to a specific module in a plan
  module_id = Column(String, ForeignKey('modules.id'))
  module = relationship("Module", back_populates="notes")