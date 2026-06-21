import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic")
AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6")
AI_BASE_URL = os.getenv("AI_BASE_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cashflow.db")
