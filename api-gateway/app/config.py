from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PORT: int = 8050
    PATIENT_SERVICE_URL: str = "http://patient-service:8000"
    DOCTOR_SERVICE_URL: str = "http://doctor-service:8010"
    APPOINTMENT_SERVICE_URL: str = "http://appointment-service:8020"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8030"
    REQUEST_TIMEOUT_SECONDS: int = 15


settings = Settings()
