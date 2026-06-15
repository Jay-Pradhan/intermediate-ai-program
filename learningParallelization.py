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
