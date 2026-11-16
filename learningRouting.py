import logging
import os
from datetime import date
from typing import Literal, Optional

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

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
    request_type: Literal["new_request", "modification_request", "other"] = Field(
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


class ChangeOfRequest(BaseModel):
    field: str = Field(description="Field to be changed")
    new_value: str = Field(description="New value for the field")


class ModifyCalendarRequest(BaseModel):
    identifier: str = Field(description="Description to identify the existing event")
    change: list[ChangeOfRequest] = Field(description="List of the changes made")
    new_participants: list[str] = Field(description="New participants to be added")
    old_participants: list[str] = Field(description="Old participants to be removed")


class CalendarResponse(BaseModel):
    success: bool = Field(description="Check whether the operation was successful")
    message: str = Field(
        description="An user-friendly response for event confirmation or modification"
    )


def route_calender_event(user_input: str) -> CalendarRequestType:
    logging.info("Routing the Calender Request....")

    system_prompt = """
                    Determine whether the calender request made by the user is a new request or modification of an existing one.

                    Respond only in this JSON format:
                    {
                    "request_type": "new_request, modification_request or other",
                    "confidence_score": "a confidence score of the event between 0 and 1",
                    "description": "a clean description of the event" 
                    }

                    request_type MUST be "new_request", "modification_request" or other
                    Do not determine any value of your own

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


def new_calendar_request(description: str) -> CalendarResponse:
    logging.info("Issuing a new Calendar Request....")

    system_prompt = f"""
                    Extract the details for creating a new calendar request
                    Today's date is {date.today()}.
                    Respond only in this JSON format:
                    {{
                    "name": "name of the event by taking reference from the description",
                    "date": "ISO 8601 formatted date and time e.g. 2025-07-04T10:00:00",
                    "duration": 60,
                    "participants": ["participant1", "participant2"]
                    }}
                    Rules:
                    - Extract participant names EXACTLY as mentioned by the user, do not invent or substitute names
                    - "participants" MUST be a list of strings (use [] if none mentioned)
                    - "duration" MUST be an integer (minutes), not a string
                    - CRITICAL: Copy participant names EXACTLY and ONLY from the user's message. 
                                The participants in this request are ONLY the names the user explicitly mentioned.
                                Do NOT add, remove, or substitute any names whatsoever.
                    - Extract the event name EXACTLY as described by the user                                

                    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": description},
        ],
        response_format={"type": "json_object"},
    )
    raw_json = response.choices[0].message.content
    result = NewCalendarRequest.model_validate_json(raw_json)

    logging.info(f"New Event Processed! event details: {result.model_dump_json()}")

    return CalendarResponse(
        success=True,
        message=f"A new event regarding {result.name} has been scheduled on {result.date} for {result.duration} mins with {', '.join(result.participants)}",
    )


def modify_calendar_request(description: str) -> CalendarResponse:
    logging.info("Modifying an existing calendar request....")

    system_prompt = """
                    Extract the details for modifying an existing calendar request

                    Respond only in this JSON format:
                    {
                    "identifier": "description to identify the existing event",
                    "change": [{"field": "date", "new_value": "2025-07-05T10:00:00"}],
                    "old_participants":["name1", "name2"],
                    "new_participants": ["name3"],

                    Rules:
                    - "change" MUST be a list of objects, each with "field" and "new_value" keys
                    - "new_participants" MUST be a list of strings (use empty list [] if none)
                    - "old_participants" MUST be a list of strings (use empty list [] if none)
                    - Never use empty strings "" for list fields, always use []
                    }
                    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": description},
        ],
        response_format={"type": "json_object"},
    )
    raw_json = response.choices[0].message.content
    result = ModifyCalendarRequest.model_validate_json(raw_json)

    logging.info(
        f"Modification Successful: Modified {result.model_dump_json()} as per the required changes"
    )
    changes_summary = ", ".join([
        f"{c.field} changed to {c.new_value}" for c in result.change
    ])

    return CalendarResponse(
        success=True,
        message=f"Event '{result.identifier}' has been updated: {changes_summary}"
        + (
            f". Added: {', '.join(result.new_participants)}"
            if result.new_participants
            else ""
        )
        + (
            f". Removed: {', '.join(result.old_participants)}"
            if result.old_participants
            else ""
        ),
    )


def process_calendar_request(user_input: str) -> Optional[CalendarResponse]:
    logging.info("Processing a calendar request....")

    request_route = route_calender_event(user_input)

    if request_route.confidence_score < 0.6:
        logging.warning(
            f"CONFIDENCE SCORE OF THE EVENT IS LOW! {request_route.confidence_score}<0.6"
        )
        return None

    # ROUTING
    if request_route.request_type == "new_request":
        return new_calendar_request(user_input)
    elif request_route.request_type == "modification_request":
        return modify_calendar_request(user_input)
    else:
        logging.warning("REQUEST TYPE NOT SUPPORTED")
        return None


user_input = (
    "Schedule a team meeting on 4th of July at 10AM with Steve and Stark for 1 hour"
)
result = process_calendar_request(user_input)

if result:
    print(f"Confirmation Message: {result.message}")
else:
    print("Please type in a valid calendar request!")

test_input = "Reschedule the meeting to 5th of July with Golu and Molu"
result = process_calendar_request(test_input)

if result:
    print(f"Confirmation Message: {result.message}")
else:
    print("Please type in a valid calendar request")
