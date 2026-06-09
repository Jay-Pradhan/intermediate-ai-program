import os
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from groq import Groq
from typing import Optional, Literal
import logging

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = "llama-3.3-70b-versatile"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.getLogger(__name__)


class CalendarRequestType(BaseModel):
    request_type: Literal["new_request", "modified_request", "other"] = Field(
        description="Type of the calendar request"
    )
    confidence_score: float = Field(
        description="A confidence score for the event between 0 & 1"
    )
    description: str = Field(description="A clean description of the event")


class NewCalendarRequest(BaseModel):
    name: str = Field(
        description="Name of the event by taking reference from the description"
    )
    date: str = Field(
        description="Date and Time of the event taking place. Use ISO 8601 to format it"
    )
    duration: int = Field(description="Duration of the event in minutes")
    participants: list[str] = Field(description="List of the participants")
