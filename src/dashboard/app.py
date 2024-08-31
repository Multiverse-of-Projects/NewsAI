import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
from src.pipeline import process_query
from src.sentiment_analysis.wordcloud import generate_wordcloud
from streamlit_echarts import st_echarts


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
load_css("styles.css")
# Layout Configuration
# st.set_page_config(layout="wide")

# Title and User Input
st.title("News AI Dashboard")
st.subheader("Enter your query to generate insights:")
query = st.text_input("Query", "Enter a keyword or phrase")

# Wait animation after submitting query
if st.button("Submit"):
    with st.spinner('Processing data, please wait...'):
        data = process_query(query)
    
    st.success("Data processed successfully!")

    # Column Layout
    col1, col2 = st.columns(2)

    # Word Cloud or Heatmap
    with col1:
        st.subheader("Keyword Extraction - Word Cloud")
        wordcloud = generate_wordcloud(data["keywords"])
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)

    # Pie Chart with topic-wise distribution
    with col2:
        st.subheader("Sentiment Distribution")
        sentiment_counts = pd.Series(data["sentiment"]).value_counts()
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title='Sentiment Distribution')
        st.plotly_chart(fig)

    # Line chart for time-wise distribution
    st.subheader("Time-wise Sentiment Distribution")
    time_data = pd.DataFrame({
        "Date": data["dates"],
        "Positive": data["positive"],
        "Neutral": data["neutral"],
        "Negative": data["negative"]
    })
    fig = px.line(time_data, x='Date', y=['Positive', 'Neutral', 'Negative'], title='Time-wise Sentiment Distribution')
    st.plotly_chart(fig)

    # Ratio of Positive, Neutral, Negative News
    st.subheader("Sentiment Ratio")
    sentiment_ratio = pd.DataFrame({
        "Sentiment": ["Positive", "Neutral", "Negative"],
        "Count": [sum(data["positive"]), sum(data["neutral"]), sum(data["negative"])]
    })
    fig = px.bar(sentiment_ratio, x="Sentiment", y="Count", title="Ratio of Positive, Neutral, and Negative News")
    st.plotly_chart(fig)

    # Choropleth Map with State-wise distribution
    st.subheader("State-wise News Distribution (India)")
    state_data = pd.DataFrame({
        "State": data["states"],
        "Count": data["count"]
    })
    state_counts = state_data.groupby("State").sum().reset_index()
    fig = px.choropleth(state_counts, locations="State", locationmode='geojson-id',
                        color="Count", title="State-wise News Distribution (India)",
                        geojson="https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson",
                        featureidkey="properties.ST_NM",
                        scope="india",
                        color_continuous_scale=px.colors.sequential.Plasma)
    st.plotly_chart(fig)

    # Spiderweb Chart
    st.subheader("Spiderweb Chart Example")
    sample_data = {"Topic A": 90, "Topic B": 70, "Topic C": 50, "Topic D": 30, "Topic E": 80}
    generate_spiderweb(sample_data)

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
