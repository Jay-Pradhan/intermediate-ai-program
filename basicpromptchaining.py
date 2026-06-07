# AI CALENDER AGENT

import os
from dotenv import load_dotenv

from groq import Groq
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import logging
import time


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
    name: str = Field(description="Name of the event by checking the description")
    participants: list[str] = Field(description="List of participants")
    duration: int = Field(description="Expected duration of the event in minutes")
    date: str = Field(
        description="Date and Time of the event. Use ISO 8601 to format it"
    )


class EventConfirmation(BaseModel):
    confirmation_msg: str = Field(
        description="Natural language for a confirmation message"
    )
    calender_link: Optional[str] = Field(default=None)


def extract_event_info(user_input: str) -> EventExtraction:
    logger.info("Initialising Event Analysis.....")
    time.sleep(1)
    logger.debug(f"Input: {user_input}")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    system_prompt1 = f"""{date_context} Analyse if the text contains a calender event
                         Respond ONLY in JSON with this exact structure:
                            {{
                                "description": "description of the event"
                                "is_event": true or false,
                                "confidence_score":  "A confidence score of an event between 0 and 1"
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
    raw_json = response.choices[0].message.content
    result = EventExtraction.model_validate_json(raw_json)

    logger.info(
        f"Extraction Completed! Is an event - {result.is_event}, Confidence Score - {result.confidence_score:.2f}"
    )

    return result


def parse_event_details(description: str) -> EventDetails:

    logger.info("Initialising parsing of event details.....")
    time.sleep(1)

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    system_prompt = f"""{date_context} Extract the detailed event information.
                        NOTE:

                        -When user enters dates like 'Next Tuesday' or something like that then take reference from this current date
                        -Stick to what user has said don't relate things to somewhere else.
                        -Current date is {today.strftime("%Y-%m-%d")}. All events must be in the future.
                        -In case an event has been already completed, then schedule it for the next year. But if the event is going to come this year then don't schedule for the next year
                        -Strictly use the time mentioned by the user. DO NOT CHANGE OR ASSUME THE TIME
                        -The datetime must follow the Indian Standard Time(IST)

                            Time format examples:
                            - '9pm' -> '2026-06-10T21:00:00+05:30'
                            - '3pm' -> '2026-06-10T15:00:00+05:30'
                            - '10am'-> '2026-06-10T10:00:00+05:30'

                         Respond ONLY in JSON with this exact structure:
                            {{
                                "name": "name of the event",
                                "date": "YYYY-MM-DDTHH:MM:SS+05:30",
                                "duration": 60,
                                "participants": ["name1", "name2"]
                            }}
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
    result = EventDetails.model_validate_json(raw_json)

    logger.info(
        f"Parsed Event Details: Name-> {result.name}, Date-> {result.date}, Duration-> {result.duration}"
    )

    logger.debug(f"Participants: {', '.join(result.participants)}")
    return result


def generate_confirmation_msg(eventDetails=EventDetails) -> EventConfirmation:
    logger.info("Generating the confirmation message....")
    time.sleep(1)

    system_prompt = """Generate a natural confirmation message of the event." \

                       Respond only in JSON in this structure:
                            {
                            "confirmation_msg": natural language for a confirmation message
                            "calendar_link": null
                            } 
                    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(eventDetails.model_dump())},
        ],
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content
    result = EventConfirmation.model_validate_json(raw_json)

    logger.info("Confirmation message was successfully generated!")

    return result


def process_calendar_request(user_input: str) -> EventConfirmation:

    logger.info("Processing a Calendar Request....")
    time.sleep(1)
    logger.debug(f"Raw Input: {user_input}")

    basic_details_extraction = extract_event_info(user_input)

    # GATE CHECK
    if (
        not basic_details_extraction.is_event
        or basic_details_extraction.confidence_score < 0.6
    ):
        logger.warning(
            f"Gate Check FAILED. is_event = {basic_details_extraction.is_event}, confidence_score= {basic_details_extraction.confidence_score}"
        )
        return None
    logger.info("Gate Checked PASSED. Moving onto the calender request")

    event_details = parse_event_details(user_input)

    confirmation = generate_confirmation_msg(event_details)

    logger.info("Calendar Request Processed SUCCESSFULLY!")

    return confirmation


user_input = "Let's schedule a birthday party for Joseph Stalin on his birthday inviting Hitler and Churchill as the guest for the whole day!"
result = process_calendar_request(user_input)

if result:
    print(f"\nConfirmation Message: {result.confirmation_msg}")

else:
    print("Calendar Request FAILED!\n")
    print("Please issue a proper calendar request")
