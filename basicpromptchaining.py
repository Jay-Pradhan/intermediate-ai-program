# AI CALENDER AGENT

import os
from dotenv import load_dotenv

from groq import Groq
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import logging
import json

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


def extract_event_info(user_input: str) -> EventDetails:
    logger.info("Initialising Event Analysis")
    logger.debug(f"Input: {user_input}")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    system_prompt1 = f"""{date_context} Analyse if the text contains a calender event
                         Respond ONLY in JSON with this exact structure:
                            {{
                                "is_event": true or false,
                                "title": "event title",
                                "date_time": "ISO 8601 datetime",
                                "duration_minutes": 60,
                                "description": "optional description"
                            }}
                        """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt1},
            {"role": "user", "content": user_input},
        ],
        response_format={"type": "json_object"},
    )
    raw_json = response.choices[0].messages.content
    result = EventExtraction.model_validate_json(raw_json)

    logger.info(
        f"Extraction Completed! Is an event - {result.is_event}, Confidence Score - {result.confidence_score}"
    )

    return result
