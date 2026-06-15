import os
from dotenv import load_dotenv

import asyncio
from groq import AsyncGroq
from pydantic import BaseModel, Field
import logging

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
model = "llama-3.3-70b-versatile"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.getLogger(__name__)


class Validator(BaseModel):
    is_request: bool = Field(description="Whether this a calendar request or not")
    confidence_score: float = Field(
        description="A confidence score for the request between 0 and 1"
    )


class SecurityVerifier(BaseModel):
    is_safe: bool = Field(description="Whether the request is safe or not")
    risk_flags: list[str] = Field(description="List of potential security conflicts")
