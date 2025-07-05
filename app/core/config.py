from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PHP Code Refactor Platform"
    PHP_TOOLS_PATH: str = "/tools"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()