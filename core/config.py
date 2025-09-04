from urllib.parse import quote

from fastapi import HTTPException
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mysql_user: str
    mysql_password: str
    mysql_database: str
    mysql_root_password: str
    db_host: str = "db"
    db_port: int = 3306
    echo_query: bool = True

    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    @property
    def db_connection_uri(self) -> str:
        required = [
            "mysql_database",
            "mysql_user",
            "mysql_password",
            "db_host",
            "db_port",
        ]
        missing = [name for name in required if getattr(self, name, None) in (None, "")]
        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Missing required setting(s): {', '.join(missing)}",
            )

        user = quote(self.mysql_user)
        password = quote(self.mysql_password)
        host = self.db_host
        port = self.db_port
        database = self.mysql_database

        db_con_url = f"mysql+asyncmy://{user}:{password}" f"@{host}:{port}/{database}"
        return db_con_url


settings = Settings()
