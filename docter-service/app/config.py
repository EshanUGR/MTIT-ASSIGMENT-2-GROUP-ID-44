from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PORT: int = 8010
    NODE_ENV: str = "development"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "doctor_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""


settings = Settings()
