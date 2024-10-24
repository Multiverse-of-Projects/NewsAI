import os
import sys
import time
from datetime import datetime
from io import BytesIO
from typing import List

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.colors as pc
import plotly.express as px
import requests
import seaborn as sns
import streamlit as st
from PIL import Image
from streamlit_echarts import st_echarts

from src.pipeline import process_articles
from src.sentiment_analysis.wordcloud import generate_wordcloud
from src.utils.dbconnector import (append_to_document,
                                   fetch_and_combine_articles, find_documents,
                                   find_one_document)
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

def download_images(image_urls, save_dir="downloaded_images"):
    """
    Downloads a list of images from the given URLs and returns a list of PIL Image objects.

    Args:
        image_urls (List[str]): List of URLs of the images to download.
        save_dir (str, optional): Directory to save the downloaded images. Defaults to "downloaded_images".

    Returns:
        List[PIL.Image.Image]: List of PIL Image objects downloaded from the URLs.
    """
    image_files = []
    for _, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            image_files.append(img)
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
    return image_files

def create_and_show_gif(image_files):
    """
    Creates a GIF from a list of PIL Image objects and displays it in Streamlit.

    Args:
        image_files (List[PIL.Image.Image]): List of PIL Image objects to create the GIF from.

    Returns:
        None
    """
    if not all(isinstance(img, Image.Image) for img in image_files):
        raise ValueError("All items in image_files must be PIL.Image objects.")
    images = [img.convert("RGBA") for img in image_files]
    frames = []
    for image in images:
        frames.append(image)
    frames[0].save(
        "mygif.gif", save_all=True, append_images=frames[1:], duration=300, loop=0
    )
    st.image("mygif.gif", use_column_width=True)

def extract_and_flatten_keywords(data) -> List[str]:
    """
    Extracts and flattens a list of lists of keywords from a dataset.

    Args:
        data (pd.DataFrame): Pandas DataFrame containing a column named 'keywords' with a list of lists of keywords.

    Returns:
        List[str]: A flattened list of all keywords.
    """
    all_keywords = []
    all_keywords = data["keywords"].tolist()
    logger.info(all_keywords)
    all_keywords = [
        item
        for sublist in all_keywords
        for item in sublist
        if isinstance(sublist, list)
    ]
    return all_keywords

def load_css(file_name):
    """
    Loads a CSS file and injects it into the Streamlit app.

    Args:
        file_name (str): Path to the CSS file to load.

    Returns:
        None
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Spiderweb chart
def generate_spiderweb(data):
    """
    Generates a spiderweb chart using Streamlit's ECharts component.

    Args:
        data (dict): Dictionary where the keys are the topic names and the values are the topic weights.

    Returns:
        None
    """
    options = {
        "title": {"text": "Spiderweb Chart Example"},
        "radar": {"indicator": [{"name": key, "max": 100} for key in data.keys()]},
        "series": [
            {
                "name": "Topics",
                "type": "radar",
                "data": [{"value": list(data.values()), "name": "Topic Distribution"}],
            }
        ],
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
fetch_till = st.slider("Fetch articles till", 5, 100, 10)

# Wait animation after submitting query
if st.button("Submit"):
    with st.spinner("Processing data, please wait..."):
        try:
            prev = find_one_document("News_Articles_Ids", {"query": query})
            if prev:
                data = prev["ids"]
            else:
                data = process_articles(query, limit=fetch_till)

            df = fetch_and_combine_articles("News_Articles", data)
            st.success("Data processed successfully!")
        except Exception as e:
            logger.error(f"Error fetching and processing articles: {e}")
            st.error(f"An error occurred: {e}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Keyword Extraction - Word Cloud")
        flattened_keywords = extract_and_flatten_keywords(df)
        wordcloud = generate_wordcloud(flattened_keywords, "Sentiments")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)

    with col2:
        sentiment_counts = df["sentiment"].value_counts()
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Sentiment Distribution",
            hole=0.5,
        )
        st.plotly_chart(fig)

    st.subheader("Time-wise Sentiment Distribution")
    df["sentiment"] = df["sentiment"].str.lower()
    df["publishedat"] = pd.to_datetime(df["publishedat"])

    time_data = df.pivot_table(
        index=df["publishedat"].dt.date,
        columns="sentiment",
        aggfunc="size",
        fill_value=0,
    )

    for sentiment in ["positive", "negative", "neutral"]:
        if sentiment not in time_data.columns:
            time_data[sentiment] = 0

    time_data = time_data.reset_index()

    fig = px.line(
        time_data,
        x="publishedat",
        y=["positive", "negative", "neutral"],
        title="Time-wise Sentiment Distribution",
        labels={"value": "Count", "variable": "Sentiment"},
    )

    fig.update_traces(line=dict(color="green"), selector=dict(name="positive"))
    fig.update_traces(line=dict(color="red"), selector=dict(name="negative"))
    fig.update_traces(line=dict(color="blue"), selector=dict(name="neutral"))

    st.plotly_chart(fig)

    with col3:
        source_distribution = df["source"].value_counts()
        fig = px.pie(
            names=source_distribution.index,
            values=source_distribution.values,
            title="Distribution of Articles by Source",
            color_discrete_sequence=pc.qualitative.Prism,
        )
        st.plotly_chart(fig)

    df["publishedat"] = pd.to_datetime(df["publishedat"])
    df["date"] = df["publishedat"].dt.date

    heatmap_data = df.pivot_table(
        index="date",
        columns="source",
        values="sentiment",
        aggfunc="count",
        fill_value=0,
    )

    fig = px.imshow(
        heatmap_data,
        color_continuous_scale="YlGnBu",
        title="Sentiment Distribution Across Sources Over Time",
    )
    fig.update_layout(xaxis_title="Source", yaxis_title="Date", xaxis_nticks=10)
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig)

    try:
        downloaded_images = download_images(df["urltoimage"].values)
        create_and_show_gif(downloaded_images)
    except Exception as e:
        logger.error(f"Error downloading or displaying images: {e}")
        st.error(f"An error occurred: {e}")

    def highlight_keywords(text, keywords):
        for keyword in keywords:
            text = text.replace(
                keyword,
                f"<span style='background-color: #ffc107; color: white'>{keyword}</span>",
            )
        return text

    with st.expander("View All Summaries with Highlighted Keywords"):
        st.subheader("Summaries")
        for index, row in df.iterrows():
            summary = row["summary"]
            keywords = row["keywords"]
            highlighted_summary = highlight_keywords(summary, keywords)
            st.markdown(highlighted_summary, unsafe_allow_html=True)

    with st.expander("View Public Reddit Data"):
        try:
            st.subheader("Reddit Keyword Extraction - Word Cloud")
            reddit_wordcloud = generate_wordcloud(data["reddit_keywords"])
            plt.figure(figsize=(10, 5))
            plt.imshow(reddit_wordcloud, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(plt)

            st.subheader("Reddit Sentiment Distribution")
            reddit_sentiment_counts = pd.Series(
                data["reddit_sentiments"]
            ).value_counts()
            fig = px.pie(
                values=reddit_sentiment_counts.values,
                names=reddit_sentiment_counts.index,
                title="Reddit Sentiment Distribution",
            )
            st.plotly_chart(fig)

            st.subheader("Hot Discussion Points from Reddit")
            st.write(
                "Placeholder for Reddit hot discussion points (to be updated with real data)."
            )
        except Exception as e:
            logger.error(f"Error loading Reddit data: {e}")
            st.error(f"An error occurred: {e}")
