from agent.database import engine, Base
from agent.models import Plan, Module

def main():
  print("Creating database tables")
  # This one magical line reads all the blueprints inheriting from Base
  # and creates the corresponding tables in your Neon database.
  Base.metadata.create_all(bind=engine)
  print("Tables created succesfully!")

if __name__ == "__main__":
  main()