# AI CALENDER AGENT

import os
from dotenv import load_dotenv

from groq import Groq
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import logging

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = "llama-3.3-70b-versatile"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class EventExtraction(BaseModel):
    description: str = Field(description="Raw description of the event")
    is_event: bool = Field(description="Check if the text is an event or not")
    confidence_score: float = Field(description="A confidence score between 0 and 1")


class EventDetails(BaseModel):
    name: str = Field(description="Name of the event")
    participants: list[str] = Field(description="List of participants")
    duration: int = Field(description="Expected duration of the event in minutes")
    date: str = Field(
        description="Date and Time of the event. Use ISO 8601 to format it"
    )


class EventConfirmation(BaseModel):
    confirmation_msg: str = Field(
        description="Natural language for a confirmation message"
    )
    calender_link: Optional[str] = Field(
        description="Generate calender link if applicable"
    )
