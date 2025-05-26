from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment
MONGO_URI = os.getenv("MONGO_URI")

# Connect to Mongo Atlas
client = MongoClient(MONGO_URI)
db = client["test"]
users_collection = db["Test User"]

print("Connecting to:", MONGO_URI)  # DEBUG LINE

# Initialize FastAPI
app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://github.com/theresechristine/ClientSignalEQ.git"],  # React frontend connect to GitHub
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model
class LoginData(BaseModel):
    email: str
    password: str

# Normalize email functions
def normalize_email(email: str) -> str:
    return email.strip().lower()

def is_email_existing(email: str) -> bool:
    normalized_email = normalize_email(email)
    return users_collection.find_one({"email": normalized_email}) is not None

# Route
@app.post("/api/login")
async def login(data: LoginData):
    normalized_email = normalize_email(data.email)

    if is_email_existing(normalized_email):
        return {"success": False, "message": "Email already exists."}

    user = {
        "email": normalized_email,
        "password": data.password 
    }

    result = users_collection.insert_one(user)
    return {
    "success": True,
    "message": "Register successfully",
    "id": str(result.inserted_id)
}
