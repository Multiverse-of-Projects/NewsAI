<p align="center">
   <a href="https://your_project_link_here">
      <img src="https://github.com/user-attachments/assets/b825468e-515c-45e8-9b81-a4f1b033ab0c" alt="logo" width="200">
   </a>
</p>


## GitHub Repository Stats
[![Prototype Video](https://img.shields.io/badge/Watch-Prototype_Video-red)](https://www.youtube.com/watch?v=j4-efJYhnzs)

| 🌟 **Stars** | 🍴 **Forks** | 🐛 **Issues** | 🔔 **Open PRs** | 🔕 **Closed PRs** |
|--------------|--------------|---------------|-----------------|------------------|
| ![GitHub stars](https://img.shields.io/badge/stars-0-blue) | ![GitHub forks](https://img.shields.io/badge/forks-0-brightgreen) | ![GitHub issues](https://img.shields.io/badge/issues-0-red) | ![Open PRs](https://img.shields.io/badge/pull%20requests-0-yellow) | ![Closed PRs](https://img.shields.io/badge/pull%20requests-0-lightgrey) |


```markdown
| 🌟 **Stars** | 🍴 **Forks** | 🐛 **Issues** | 🔔 **Open PRs** | 🔕 **Closed PRs** |
|--------------|--------------|---------------|-----------------|------------------|
| ![GitHub stars](https://img.shields.io/github/stars/username/repository?style=social) | ![GitHub forks](https://img.shields.io/github/forks/username/repository?style=social) | ![GitHub issues](https://img.shields.io/github/issues/username/repository) | ![Open PRs](https://img.shields.io/github/issues-pr/username/repository) | ![Closed PRs](https://img.shields.io/github/issues-pr-closed/username/repository) |
```

Make sure to replace `username` and `repository` with your actual GitHub username and repository name!

---

# Welcome to the News AI Dashboard Project! 🎉

## Overview
This project aims to create a comprehensive news dashboard that aggregates articles from multiple APIs, performs sentiment analysis, and provides a user-friendly interface for exploration.

[![Watch the video](https://img.youtube.com/vi/stTXgljJVPQ/0.jpg)](https://www.youtube.com/watch?v=stTXgljJVPQ)

*Click the image to watch the demo on YouTube.*

---

## Directory Structure
The project is organized into the following directories:

- **`data/`**: Contains raw and processed data.
  - `raw/`: Raw JSON files from APIs.
  - `processed/`: Preprocessed and structured data.
  
- **`src/`**: Contains source code for the project.
  - `ingestion/`: Code for data ingestion from multiple APIs.
  - `preprocessing/`: Code for data formatting and structuring.
  - `sentiment_analysis/`: Code for sentiment analysis and topic modeling.
  - `summarization/`: Code for summarization logic.
  - `api/`: FastAPI implementation.
  - `dashboard/`: Streamlit dashboard code.
  
- **`notebooks/`**: Jupyter notebooks for experiments and EDA.

- **`requirements.txt`**: Python packages required for the project.

- **`README.md`**: Project overview and setup instructions.

- **`.gitignore`**: Git ignore file.

<details>
<summary>Folder Structure for the News AI Dashboard</summary>

```plaintext
news_ai_dashboard/
│
├── data/
│   ├── raw/                   # Raw JSON files if needed as a fallback
│   └── processed/             # Preprocessed and structured data
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

---

## Branching Strategy
The project follows a simplified branching strategy:

- **`main`**: The stable branch where all working features are merged.
- **`feature/*`**: Branches created for new code additions.
- **`bug/*`**: Branches dedicated to fixing existing code issues.
- If your branch does not fit any of the above categories, please create a new branch with an appropriate name.

---

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone https://github.com/your_username/your_repository.git
   ```
   
2. **Install required Python packages**
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Create a new branch for your feature**
   ```bash
   git checkout -b feature/your-feature-name
   ```
   
4. **Work on your feature and commit changes regularly**
   
5. **Merge your branch into `main` after peer review**

---

## Our Valuable Contributors ❤️✨
[![Contributors](https://contrib.rocks/image?repo=Multiverse-of-Projects/NewsAI)](https://github.com/Multiverse-of-Projects/NewsAI/graphs/contributors)

---

This structure highlights the essential parts of your project, provides clarity, and maintains an inviting tone. Feel free to adjust any sections to better match your style!
