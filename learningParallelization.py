import os
from dotenv import load_dotenv

import asyncio
from groq import AsyncGroq
from pydantic import BaseModel, Field
import logging

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
model = "llama-3.3-70b-versatile"
