import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # AI Provider Configuration
    # Using Hugging Face (German models)
    AI_PROVIDER: str = "huggingface"
    
    # Hugging Face Configuration
    # German text generation model (for job extraction)
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "Veronika-T/mistral-german-7b")
    # German embedding model (for semantic search and analysis)
    HUGGINGFACE_EMBEDDING_MODEL: str = os.getenv("HUGGINGFACE_EMBEDDING_MODEL", "deutsche-telekom/gbert-large-paraphrase-cosine")
    # Hugging Face API token (optional, for accessing gated models)
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    
    # Application Configuration
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    # File paths
    EXCEL_FILE_PATH: str = os.getenv("EXCEL_FILE_PATH", "data/Landratsamt.xlsx")
    JSON_OUTPUT_DIR: str = os.getenv("JSON_OUTPUT_DIR", "data/output")
    
    # Processing Configuration
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Frontend Callback Configuration (deprecated - kept for backward compatibility)
    FRONTEND_CALLBACK_URL: str = os.getenv("FRONTEND_CALLBACK_URL", "http://localhost:5173/api/jobs/callback")


settings = Settings()
