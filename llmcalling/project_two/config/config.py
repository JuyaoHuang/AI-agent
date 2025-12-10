import os

class AppConfig:
    """App configuration"""

    # FastAPI config
    APP_TITLE = "Atri Chatbot"
    APP_DESCRIPTION = "Welcome to Atri Chatbot"
    APP_VERSION = "1.0.0"

    # server config
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8026"))

    # log config
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "logs")


# export config
app_config = AppConfig()