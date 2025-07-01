from fastapi import FastAPI
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize FastAPI app
app = FastAPI()

# Initialize Vader sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Define input schema
class SentimentRequest(BaseModel):
    text: str

# Define API route
@app.post("/predict")
def predict_sentiment(data: SentimentRequest):
    text = data.text
    scores = analyzer.polarity_scores(text)
    return {
        "model": "vader",
        "compound": scores["compound"],
        "positive": scores["pos"],
        "neutral": scores["neu"],
        "negative": scores["neg"]
    }

# Curl example:
# curl -X POST http://localhost:8001/predict -H "Content-Type: application/json" -d '{"text": "Great service!"}'