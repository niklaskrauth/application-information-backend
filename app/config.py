import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # AI Provider Configuration
    # Using Ollama (local AI)
    AI_PROVIDER: str = "ollama"
    
    # Ollama Configuration (remote AI server)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://45.93.251.180:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Application Configuration
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    # File paths
    EXCEL_FILE_PATH: str = os.getenv("EXCEL_FILE_PATH", "data/Landratsamt.xlsx")
    
    # Processing Configuration
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))


settings = Settings()
