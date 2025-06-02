from setuptools import setup, find_packages

setup(
    name="ai-gateway",
    version="0.1.0",
    description="AI Gateway FastAPI service for Discord bot integration",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "httpx",
        "pydantic-settings",
        "supabase",
        "python-jose[cryptography]",
        "pytest",
        "pytest-asyncio",
        "ruff",
        "openai",
        "python-multipart"
    ],
    python_requires=">=3.11",
)
