import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from typing import List
import time
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from src.pipeline import process_articles
from src.utils.dbconnector import find_documents, find_one_document, append_to_document, fetch_and_combine_articles
from src.sentiment_analysis.wordcloud import generate_wordcloud
from streamlit_echarts import st_echarts

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), "..", "..")))
def extract_and_flatten_keywords(data) -> List[str]:
    all_keywords = []
    all_keywords = data["keywords"].tolist()
    all_keywords = [item for sublist in all_keywords for item in sublist]
    return all_keywords

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# Function to simulate data processing (replace with actual processing functions)


# Function to create a word cloud

# Function to create a spiderweb chart
def generate_spiderweb(data):
    options = {
        "title": {"text": "Spiderweb Chart Example"},
        "radar": {"indicator": [{"name": key, "max": 100} for key in data.keys()]},
        "series": [{
            "name": "Topics",
            "type": "radar",
            "data": [{"value": list(data.values()), "name": "Topic Distribution"}]
        }]
    }
    st_echarts(options=options)

# Load external CSS
# load_css("styles.css")
# Layout Configuration
# st.set_page_config(layout="wide")

# Title and User Input
st.title("News AI Dashboard")
st.subheader("Enter your query to generate insights:")
query = st.text_input("Query", "Enter a keyword or phrase")

# Wait animation after submitting query
if st.button("Submit"):
    with st.spinner('Processing data, please wait...'):
        prev = find_one_document("News_Articles_Ids", {"query": query})
    # st.write(prev)
        if prev:
            data = prev["ids"]
        else:
            data = process_articles(query)
    # st.write(data)
    df = fetch_and_combine_articles("News_Articles", data)
    st.success("Data processed successfully!")
    st.write(df)
    # Column Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Keyword Extraction - Word Cloud")
        flattened_keywords = extract_and_flatten_keywords(df)
        wordcloud = generate_wordcloud(flattened_keywords, "Sentiments")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)
    # Pie Chart with topic-wise distribution
    with col2:
        st.subheader("Sentiment Distribution")
        sentiment_counts = df["sentiment"].value_counts()
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title='Sentiment Distribution')
        st.plotly_chart(fig)

    # Line chart for time-wise distribution
    st.subheader("Time-wise Sentiment Distribution")
    df['publishedat'] = pd.to_datetime(df['publishedat'])

    # Extract dates and sentiments
    time_data = df.pivot_table(index=df['publishedat'].dt.date, 
                           columns='sentiment', 
                           aggfunc='size', 
                           fill_value=0)
   # Reset the index to turn the dates into a column and rename the columns
    time_data = time_data.reset_index().rename_axis(None, axis=1)

    # Ensure the columns are in the correct order and all sentiments are present
    # time_data = time_data[['publishedat', 'positive', 'neutral', 'negative']].fillna(0)
    # st.write(time_data)
    # Rename columns for clarity
    # time_data.columns = ['Date', 'Positive', 'Neutral', 'Negative']

    # Plotting the line chart
    # Plotting the line chart for all sentiments
    for sentiment in ["POSITIVE", "NEGATIVE", "UNKNOWN"]:
        if sentiment not in time_data.columns:
            time_data[sentiment] = 0
        fig = px.line(time_data, x='publishedat', y=sentiment, title=f'Time-wise {sentiment} Sentiment Distribution')
        st.plotly_chart(fig)

    # Ratio of Positive, Neutral, Negative News
    st.subheader("Sentiment Ratio")
    sentiment_ratio = pd.DataFrame({
        "Sentiment": ["Negative", "Unknown", "Positive"],
        "Count": [sum(data["negative"]), sum(data["unknown"]), sum(data["positive"])]
    })
    fig = px.bar(sentiment_ratio, x="Sentiment", y="Count", color="Sentiment", barmode="stack", 
                 color_discrete_map={"Negative": "red", "Unknown": "blue", "Positive": "green"},
                 title="Ratio of Positive, Neutral, and Negative News")
    st.plotly_chart(fig)

   
    # Reddit Word Cloud
    st.subheader("Reddit Keyword Extraction - Word Cloud")
    reddit_wordcloud = generate_wordcloud(data["reddit_keywords"])
    plt.figure(figsize=(10, 5))
    plt.imshow(reddit_wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

    # Reddit Sentiment Analysis
    st.subheader("Reddit Sentiment Distribution")
    reddit_sentiment_counts = pd.Series(data["reddit_sentiments"]).value_counts()
    fig = px.pie(values=reddit_sentiment_counts.values, names=reddit_sentiment_counts.index, title='Reddit Sentiment Distribution')
    st.plotly_chart(fig)

    # Hot Discussion Points from Reddit
    st.subheader("Hot Discussion Points from Reddit")
    st.write("Placeholder for Reddit hot discussion points (to be populated with real data).")
