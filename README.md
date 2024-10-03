# News AI Dashboard Project
=====================================

## Overview
-----------

This project aims to create a comprehensive news dashboard that aggregates news articles from multiple APIs, performs sentiment analysis, and provides a user-friendly interface for exploration.

## Directory Structure
----------------------

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

## Branching Strategy
--------------------

The project uses a simplified branching strategy:

* `main`: the final branch where all working features are merged
* `feature/*`: each feature branch is focused on a specific module or task

## Demo Video


[![Watch the video](https://img.youtube.com/vi/stTXgljJVPQ/0.jpg)](https://www.youtube.com/watch?v=stTXgljJVPQ)

*Click the image to watch the demo on YouTube.*

## Setup Instructions
---------------------

1. Clone the repository
2. Install required Python packages using `pip install -r requirements.txt`
3. Create a new branch for your feature using `git checkout -b feature/your-feature-name`
4. Work on your feature and commit changes regularly
5. Merge your branch into `main` after peer review or pair programming sessions

#Contribution Guidelines
We welcome contributions from everyone! To ensure a smooth collaboration, please follow these guidelines:

## Fork the Repository:
Create a personal fork of the repository on GitHub.

## Create a New Branch:
Always create a new branch for your feature or bug fix:
```bash
git checkout -b feature/your-feature-name
```

## Write Clear Commit Messages:
Use clear and descriptive commit messages to explain your changes. Follow this format:
```markdown
[type]: [short description]
```
## Update Documentation:
If your changes affect the functionality, please update the relevant documentation in the README.md or add comments to the code.

## Run Tests:
If applicable, ensure that all tests pass before submitting your changes. You can add new tests for new features as necessary.

## Submit a Pull Request:
Once your feature is complete, submit a pull request (PR) from your branch to the main branch of the original repository. Provide a clear description of your changes and reference any relevant issues.

<h1>Our Valuable Contributors ❤️✨</h1>

[![Contributors](https://contrib.rocks/image?repo=Multiverse-of-Projects/NewsAI)](https://github.com/Multiverse-of-Projects/NewsAI/graphs/contributors)

# MIT License

Copyright (c)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

 
## Summary of the MIT License
Permission is granted to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software.
Attribution: The original license notice must be included in all copies or substantial portions of the software.
Warranty Disclaimer: The software is provided "as is", without warranty of any kind. The authors are not liable for any damage or loss arising from the use of the software.