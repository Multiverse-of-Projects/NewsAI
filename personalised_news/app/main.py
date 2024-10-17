from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .services.sentiment_analysis import analyze_sentiment
from .models.news import articles

app = FastAPI()

# Serve static files (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve the dashboard HTML
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("app/templates/dashboard.html") as f:
        return HTMLResponse(content=f.read())

# Fetch articles based on emotion
@app.get("/articles/")
def get_articles(emotion: str = Query(..., title="Emotion")):
    filtered_articles = [article for article in articles if article["emotion"] == emotion]
    if not filtered_articles:
        raise HTTPException(status_code=404, detail="No articles found for this emotion")
    return {"articles": filtered_articles}

# Input validation model for sentiment analysis
class ArticleInput(BaseModel):
    text: str

# Sentiment analysis of an article
@app.post("/analyze/")
def analyze_article(article_input: ArticleInput):
    return analyze_sentiment(article_input.text)
