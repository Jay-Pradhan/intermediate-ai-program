import os
from dotenv import load_dotenv

import asyncio
from groq import AsyncGroq
from pydantic import BaseModel, Field
import logging
