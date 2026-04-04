from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PORT: int = 8030
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "mediconnect_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"

    APPOINTMENT_SERVICE_URL: str = "http://appointment-service:8020"
    PATIENT_SERVICE_URL: str = "http://patient-service:8000"
    DOCTOR_SERVICE_URL: str = "http://doctor-service:8010"


settings = Settings()
