from functools import lru_cache
import os
from dotenv import load_dotenv
from roboflow import Roboflow

# Load environment variables from api.env
load_dotenv('api.env')

API_KEY = os.getenv("API_KEY")
MODEL_ENDPOINT = os.getenv("PROJECT_NAME")
VERSION = 3


rf = Roboflow(api_key=API_KEY)
project = rf.workspace().project(MODEL_ENDPOINT)
Roboflow_model = project.version(VERSION).model
    
