from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
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

  articleTitle = Column(String)
  articleReason = Column(String)
  articleLink = Column(String)

  videosJson = Column(String) # We will store the videos list as a JSON text block

  # This is the foreign key that links this module back to a specific plan
  plan_id = Column(String, ForeignKey('plans.id'))
  plan = relationship("Plan", back_populates="modules")