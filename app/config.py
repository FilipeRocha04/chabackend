from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str

    jwt_secret: str
    jwt_expire_minutes: int = 60 * 24 * 7

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
