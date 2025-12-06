import os
import dataclasses


@dataclasses.dataclass
class GeneralConfig:
    ERP_DB_SCHEMA_NAME: str = os.getenv("ERP_DB_SCHEMA_NAME", "erp_schema")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    SECRET_KEY: str = str(os.getenv("SECRET_KEY"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    SESSION_COOKIE_NAME: str = str(os.getenv("SESSION_COOKIE_NAME", "session_token"))
