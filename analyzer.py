"""Reusable Gemini-based customer feedback analysis logic.

This module mirrors the logic in api.py so the Streamlit app can run
self-contained without needing a separate FastAPI server.
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()
client = genai.Client()

MODEL = "gemini-3.5-flash"


class Review(BaseModel):
    text: str


class Analysis(BaseModel):
    label: str
    score: int
    theme: str


def analyze_review(text: str) -> Analysis:
    """Analyze a single customer review and return its Analysis."""
    review = Review(text=text)
    response = client.models.generate_content(
        model=MODEL,
        contents=(
            "analyze this customer review."
            "label must 'positive', 'negative' or 'neutral'"
            "score must be a number from 1 (very bad) to 5 (very good)"
            "theme must be a short description of the main topic of the review"
            f"review: {review.text}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Analysis,
        ),
    )
    return response.parsed


def analyze_batch(texts: list[str]) -> list[dict]:
    """Analyze multiple reviews and return a list of result dicts."""
    results = []
    for text in texts:
        try:
            analysis = analyze_review(text)
            results.append(
                {
                    "review": text,
                    "label": analysis.label,
                    "score": analysis.score,
                    "theme": analysis.theme,
                }
            )
        except Exception as exc:  # noqa: BLE001 - keep going on single failures
            results.append(
                {
                    "review": text,
                    "label": "error",
                    "score": None,
                    "theme": str(exc),
                }
            )
    return results
