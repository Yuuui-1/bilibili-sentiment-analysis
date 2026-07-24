import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
