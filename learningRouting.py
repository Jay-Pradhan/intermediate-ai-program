import os
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from groq import Groq
from typing import Optional, Literal
import logging

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = "llama-3.3-70b-versatile"
