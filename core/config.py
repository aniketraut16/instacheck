from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

class LLMSettings:
    provider: str = "ollama" # ollama or groq
    api_key: str = os.getenv("GROQ_API_KEY") if provider == "groq" else None


settings = Settings()
llm_settings = LLMSettings()
