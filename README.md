<p align="center">
   <a href ="https://your_project_link_here">
      <img src="https://github.com/user-attachments/assets/b825468e-515c-45e8-9b81-a4f1b033ab0c" alt="logo" width="200">
   </a>
</p>

<p align="center">
    <a href="https://www.youtube.com/watch?v=stTXgljJVPQ" target="_blank">
       <img alt="YouTube Channel Subscribers" src="https://img.shields.io/youtube/channel/subscribers/UCz_32Uvk_5rrrQVmrkektag">
    </a>&nbsp
    <a href="https://discord.gg/ZRabqqxp">
        <img src="https://img.shields.io/discord/your_discord_id?color=5865F2&logo=discord&logoColor=white&style=flat-square" alt="Join us on Discord">
    </a>&nbsp
   <a href ="https://www.youtube.com/watch?v=stTXgljJVPQ">
       <img alt="demo" src="https://www.youtube.com/watch?v=stTXgljJVPQ" width="800" />
   </a>
</p>

---

# Welcome to the News AI Dashboard Project! 🎉

## Overview
-----------
This project aims to create a comprehensive news dashboard that aggregates news articles from multiple APIs, performs sentiment analysis, and provides a user-friendly interface for exploration.

[![Watch the video](https://img.youtube.com/vi/stTXgljJVPQ/0.jpg)](https://www.youtube.com/watch?v=stTXgljJVPQ)

*Click the image to watch the demo on YouTube.*

## Directory Structure
----------------------
The project is organized into the following directories:

* `data/`: contains raw and processed data
	+ `raw/`: raw JSON files from APIs
	+ `processed/`: preprocessed and structured data
* `src/`: contains source code for the project
	+ `ingestion/`: code for data ingestion from multiple APIs
	+ `preprocessing/`: code for data formatting and structuring
	+ `sentiment_analysis/`: code for sentiment analysis and topic modeling
	+ `summarization/`: code for summarization logic
	+ `api/`: FastAPI implementation
	+ `dashboard/`: Streamlit dashboard code
* `notebooks/`: Jupyter notebooks for experiments and EDA
* `requirements.txt`: Python packages required for the project
* `README.md`: project overview and setup instructions
* `.gitignore`: Git ignore file

<details>
<summary>Folder Structure for the NewsAI</summary>

```txt
news_ai_dashboard/
│
├── data/
│   ├── raw/                   # Raw JSON files if needed as a fallback
│   └── processed/             # Preprocessed and structured data (can be MongoDB backup)
│
├── src/
│   ├── ingestion/             # Code for data ingestion from multiple APIs
│   │   ├── newsapi.py         # Ingestion from NewsAPI
│   │   ├── praw.py            # Ingestion from Reddit using PRAW
│   │   ├── gnews.py           # Ingestion from GNews API
│   │   └── fetch_full_articles.py # Fetch full articles from URLs
│   │
│   ├── preprocessing/         # Data formatting and structuring
│   │   ├── format_data.py     # Formatting scripts using BS and NLTK
│   │   └── structure_data.py  # Structuring the data for analysis
│   │
│   ├── sentiment_analysis/    # Sentiment analysis module
│   │   ├── sentiment_model.py # Sentiment analysis using LLM/BERT
│   │   ├── classify.py        # Positive/Negative classification
│   │   └── wordcloud.py       # Generate word cloud
│   │
│   ├── summarization/         # Summarization logic for dashboard
│   │   └── summarize.py       # Summarization logic
│   │
│   ├── api/                   # FastAPI implementation
│   │   ├── main.py            # API entry point
│   │   ├── endpoints.py       # API endpoints
│   │   └── utils.py           # Utility functions for the API
│   │
│   └── dashboard/             # Streamlit dashboard
│       ├── app.py             # Main dashboard application
│       └── components/        # Reusable components for Streamlit
│
├── notebooks/                 # Jupyter notebooks for experiments and EDA
│   └── sentiment_analysis.ipynb
│
├── requirements.txt           # Python packages required
├── README.md                  # Project overview and setup instructions
└── .gitignore                 # Git ignore file
```
</details> 

## Branching Strategy
--------------------
The project uses a simplified branching strategy:

* `main`: The final branch where all working features are merged.
* `feature/*`: Branches created for new code additions.
* `bug/*`: Branches dedicated to fixing existing code issues.
* If your branch does not fit any of the above categories, you may create a new branch. However, please ensure that you give it an appropriate and relevant name.

## Setup Instructions
---------------------
1. Clone the repository
2. Install required Python packages using `pip install -r requirements.txt`
3. Create a new branch for your feature using `git checkout -b feature/your-feature-name`
4. Work on your feature and commit changes regularly
5. Merge your branch into `main` after peer review or pair programming sessions

<h1>Our Valuable Contributors ❤️✨</h1>

[![Contributors](https://contrib.rocks/image?repo=Multiverse-of-Projects/NewsAI)](https://github.com/Multiverse-of-Projects/NewsAI/graphs/contributors)
 
