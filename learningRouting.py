import os
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from groq import Groq
from typing import Optional, Literal
import logging

load_dotenv()

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
    duration: Optional[int] = Field(description="Duration of the event in minutes")
    participants: list[str] = Field(description="List of the participants")


class ChangeOfRequest(BaseModel):
    field: str = Field(description="Field to be changed")
    new_value: str = Field(description="New value for the field")


class ModifyCalendarRequest(BaseModel):
    identifier: str = Field(description="Description to identify the existing event")
    change: list[ChangeOfRequest] = Field(description="List of the changes made")
    new_partcipants: list[str] = Field(description="New participants to be added")
    old_participants: list[str] = Field(description="Old participants to be removed")


class CalendarResponse(BaseModel):
    success: bool = Field(description="Check whether the operation was successful")
    message: str = Field(
        description="An user-friendly response for event confirmation or modification"
    )


def route_calender_event(user_input: str) -> CalendarRequestType:
    logging.info("Routing the Calender Request")

    system_prompt = """
                    Determine whether the calender request made by the user is a new request or modify an existing one.

                    Respond only in this JSON format:
                    {
                    "request_type": "the type of the calendar",
                    "confidence_score": "a confidence score of the event between 0 and 1",
                    "description": "a clean description of the event" 
                    } 
                    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        response_format={"type": "json_object"},
    )
    raw_json = response.choices[0].message.content
    result = CalendarRequestType.model_validate_json(raw_json)

    logging.info(
        f"Request routed as {result.request_type} with a confidence score of {result.confidence_score}"
    )

    return result
