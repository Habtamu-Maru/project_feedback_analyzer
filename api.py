from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()
app = FastAPI() 

#what the caller must send using the request body
class Review(BaseModel):
    text: str
class Analysis(BaseModel):
    label: str
    score: int
    theme: str

@app.post("/analyze")
def analyze(review:Review):
    response = client.models.generate_content(
        model = "gemini-3.5-flash",
        contents =(
            "analyze this customer review."
             "label must 'positive', 'negative' or 'neutral'"
             "score must be a number from 1 (very bad) to 5 (very good)"
             "theme must be a short description of the main topic of the review"
             f"review: {review.text}"

        ),
        config = types.GenerateContentConfig(
            response_mime_type = "application/json",
            response_schema = Analysis,
        ),

    )
    return response.parsed