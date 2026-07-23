# test_setup.py

from dotenv import load_dotenv
import os

# This line reads your .env file and makes its variables available
load_dotenv()

# Try to import everything you installed on Day 1
import langchain
import chromadb
import pypdf
from sentence_transformers import SentenceTransformer

# Try to read your API key
api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key:
    print("API key loaded successfully.")
else:
    print("API key NOT found — check your .env file.")

print("All packages imported successfully. Setup is working.")