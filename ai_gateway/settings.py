"""Application settings and configuration."""

import os
from typing import Optional, List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Fields:
        DEBUG: Enable debug mode.
        ENVIRONMENT: Deployment environment (development/production).
        JWT_SECRET: Secret key for JWT signing.
        JWT_ALGORITHM: Algorithm for JWT.
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiry in minutes.
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiry in days.
        CORS_ORIGINS: Allowed CORS origins.
        LOG_LEVEL: Logging level.
        LOG_FORMAT: Logging format string.
        DISCORD_CLIENT_ID: Discord OAuth2 client ID.
        DISCORD_CLIENT_SECRET: Discord OAuth2 client secret.
        DISCORD_REDIRECT_URI: Discord OAuth2 redirect URI.
        SUPABASE_URL: Supabase instance URL.
        SUPABASE_KEY: Supabase service key.
        OPENAI_API_KEY: OpenAI provider API key.
        ANTHROPIC_API_KEY: Anthropic provider API key.
        MISTRAL_API_KEY: Mistral provider API key.
        RATE_LIMIT: Rate limiting config string.
    """

    #: Enable debug mode.
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    #: Deployment environment (development/production).
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    #: Secret key for JWT signing.
    JWT_SECRET: str = os.getenv("JWT_SECRET", "insecure-secret-key-change-me")

    #: Algorithm for JWT.
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    #: Access token expiry in minutes.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    #: Refresh token expiry in days.
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    #: Allowed CORS origins.
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")

    #: Logging level.
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    #: Logging format string.
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    #: Discord OAuth2 client ID.
    DISCORD_CLIENT_ID: Optional[str] = os.getenv("DISCORD_CLIENT_ID", "")

    #: Discord OAuth2 client secret.
    DISCORD_CLIENT_SECRET: Optional[str] = os.getenv("DISCORD_CLIENT_SECRET", "")

    #: Discord OAuth2 redirect URI.
    DISCORD_REDIRECT_URI: str = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:3000/auth/callback")

    #: Supabase instance URL.
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL", "")

    #: Supabase service key.
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY", "")

    #: OpenAI provider API key.
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")

    #: Anthropic provider API key.
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")

    #: Mistral provider API key.
    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY", "")

    #: Rate limiting config string.
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "100/minute")

    model_config = {'extra': 'allow'}


#: Global settings instance for application-wide configuration.
#: Access fields as settings.<FIELD_NAME>.
settings: Settings = Settings()
