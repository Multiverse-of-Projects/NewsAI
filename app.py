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
import plotly.graph_objects as go
import requests
import seaborn as sns
import streamlit as st
from PIL import Image
import google.generativeai as genai
from sklearn.decomposition import PCA
from streamlit_echarts import st_echarts

# from src.pipeline import process_articles
from src.sentiment_analysis.wordcloud import generate_wordcloud
from src.utils.dbconnector import (append_to_document,
                                   fetch_and_combine_articles, find_documents,
                                   find_one_document, fetch_prefetched_queries,
                                   get_mongo_client)
from src.utils.logger import setup_logger

logger = setup_logger()
st.set_page_config(layout="wide", page_title="NewsAI Dashboard App", page_icon="🚀")

def download_images(image_urls, save_dir="downloaded_images"):
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)
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
            # img_path = os.path.join(save_dir, f'image_{idx}.png')
            # img.save(img_path)
            image_files.append(img)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

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


# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), "..", "..")))
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

def generate_article_embeddings(df):
    """
    Generates embeddings for articles using Google's embedding model.
    Prioritizes full content over summary for better semantic representation.
    
    Args:
        df (pd.DataFrame): DataFrame containing article data
        
    Returns:
        np.ndarray: Array of 3D reduced embeddings for the articles
    """
    try:
        # Make sure the DataFrame has required columns
        if 'id' not in df.columns:
            logger.error("DataFrame is missing required 'id' column")
            st.error("DataFrame is missing required 'id' column for embedding generation")
            return None
            
        api_key = st.secrets.get("GEMINI_API_KEY")
        
        if not api_key:
            st.error("Google API key not found in Streamlit secrets.")
            return None
            
        genai.configure(api_key=api_key)
        
        # Initialize the embedding model (use the stable model that's known to work)
        embedding_model = "models/embedding-001"  # Using the stable version that's supported
        
        # Generate embeddings from article content (full content preferred over summary over description)
        texts = []
        for _, row in df.iterrows():
            if pd.notna(row.get('content')) and row['content']:
                texts.append(row['content'])
            elif pd.notna(row.get('summary')) and row['summary']:
                texts.append(row['summary'])
            elif pd.notna(row.get('description')) and row['description']:
                texts.append(row['description'])
            else:
                texts.append("")
        
        # Check if embeddings already exist in the database
        article_ids = df['id'].tolist()
        
        # Handle possible NaN or None values in the ids
        article_ids = [str(article_id) for article_id in article_ids if pd.notna(article_id)]
        
        if not article_ids:
            logger.error("No valid article IDs found in DataFrame")
            st.error("No valid article IDs found for embedding generation")
            return None
            
        db = get_mongo_client()
        embeddings_collection = db["Article_Embeddings"]
        
        # Retrieve existing embeddings
        existing_embeddings = {}
        try:
            for doc in embeddings_collection.find({"article_id": {"$in": article_ids}}):
                existing_embeddings[doc["article_id"]] = doc["embedding"]
        except Exception as e:
            logger.error(f"Error retrieving existing embeddings: {e}")
            # Continue with empty existing_embeddings
        
        # Generate embeddings using Google's model for articles that don't have cached embeddings
        embeddings = []
        # Show progress bar for embedding generation
        progress_bar = st.progress(0)
        for i, (_, row) in enumerate(df.iterrows()):
            # Update progress bar
            progress_bar.progress((i + 1) / len(df))
            if 'id' not in row or pd.isna(row['id']):
                logger.warning(f"Row {i} missing ID, skipping")
                embeddings.append([0] * 768)  # Use zero vector for missing ID
                continue
                
            article_id = str(row['id'])  # Convert to string to ensure consistency
            
            # If embedding already exists in database, use it
            if article_id in existing_embeddings:
                embeddings.append(existing_embeddings[article_id])
                logger.info(f"Using cached embedding for article {article_id}")
                continue
                
            try:
                if i >= len(texts):
                    logger.error(f"Index {i} out of range for texts list of length {len(texts)}")
                    embeddings.append([0] * 768)
                    continue
                    
                # Truncate text if it exceeds the model's token limit
                text_to_embed = texts[i]
                if not text_to_embed:
                    logger.warning(f"Empty text for article {article_id}, using zero vector")
                    embeddings.append([0] * 768)
                    continue
                
                # Get title from article if available (but don't pass it as parameter for embedding-001)
                title = row.get('title', '') if pd.notna(row.get('title')) else ''
                
                # For embedding-001, we need to use simpler parameters
                result = genai.embed_content(
                    model=embedding_model,
                    content=text_to_embed[:8000],  # Google's embedding model has a token limit
                    task_type="CLUSTERING",  # Best for article content
                    # title=title  # Include title for better quality
                )
                embedding = result["embedding"]
                embeddings.append(embedding)
                
                # Store the embedding in the database for future use
                try:
                    embeddings_collection.insert_one({
                        "article_id": article_id,
                        "embedding": embedding,
                        "created_at": datetime.now()
                    })
                    logger.info(f"Generated and stored embedding for article {article_id}")
                except Exception as e:
                    logger.error(f"Error storing embedding in database: {e}")
                
            except Exception as e:
                logger.error(f"Error generating embedding for article {article_id}: {e}")
                # Add a zero vector as fallback if embedding fails
                embeddings.append([0] * 768)  # typical embedding dimension
        
        # Convert embeddings to numpy array
        if not embeddings:
            logger.error("No embeddings were generated")
            return None
            
        embeddings_array = np.array(embeddings)
        
        # Make sure we have enough embeddings for PCA
        if len(embeddings_array) < 3:
            logger.error(f"Not enough embeddings ({len(embeddings_array)}) for 3D PCA")
            return None
            
        # Reduce dimensionality to 3D for visualization
        pca = PCA(n_components=3)
        embeddings_3d = pca.fit_transform(embeddings_array)
        
        return embeddings_3d
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        st.error(f"Error generating embeddings: {e}")
        return None

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


# Function to simulate data processing (replace with actual processing functions)


# Function to create a word cloud


# Function to create a spiderweb chart
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
st.title("News AI Open to all Dashboard")
st.subheader("Select your query to view insights:")
query = st.selectbox("Select query", fetch_prefetched_queries())
# fetch_till = st.slider("Fetch articles till", 5, 100, 10)
fetch_till=5

# Wait animation after submitting query
if st.button("Submit"):
    with st.spinner("Processing data, please wait..."):
        prev = find_one_document("News_Articles_Ids", {"query": query})
        # st.write(prev)
        if prev:
            data = prev["ids"]
        else:
            pass
            # data = process_articles(query, limit=fetch_till)
    # st.write(data)
    df = fetch_and_combine_articles("News_Articles", data)
    st.success("Data processed successfully!")
    # st.write(df)
    # Column Layout
    col1, col2, col3 = st.columns(3)

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
        # st.subheader("Sentiment Distribution")
        sentiment_counts = df["sentiment"].value_counts()
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Sentiment Distribution",
            hole=0.5,
        )
        st.plotly_chart(fig)

    # Line chart for time-wise distribution
    st.subheader("Time-wise Sentiment Distribution")
    # Normalize the sentiment values to lowercase
    df["sentiment"] = df["sentiment"].str.lower()
    df["publishedat"] = pd.to_datetime(df["publishedat"])

    # Extract dates and aggregate sentiment counts
    time_data = df.pivot_table(
        index=df["publishedat"].dt.date,
        columns="sentiment",
        aggfunc="size",
        fill_value=0,
    )

    # Ensure all sentiments (positive, negative, neutral) are included
    for sentiment in ["positive", "negative", "neutral"]:
        if sentiment not in time_data.columns:
            time_data[sentiment] = 0

    # Reset the index to turn dates into a column
    time_data = time_data.reset_index()

    # Create the line plot
    fig = px.line(
        time_data,
        x="publishedat",
        y=["positive", "negative", "neutral"],
        title="Time-wise Sentiment Distribution",
        labels={"value": "Count", "variable": "Sentiment"},
    )

    # Customize line colors for each sentiment
    fig.update_traces(line=dict(color="green"), selector=dict(name="positive"))
    fig.update_traces(line=dict(color="red"), selector=dict(name="negative"))
    fig.update_traces(line=dict(color="blue"), selector=dict(name="neutral"))

    # Display the plot
    st.plotly_chart(fig)

    with col3:
        source_distribution = df["source"].value_counts()

        # Plot the pie chart
        fig = px.pie(
            names=source_distribution.index,
            values=source_distribution.values,
            title="Distribution of Articles by Source",
            color_discrete_sequence=pc.qualitative.Prism,
        )
        st.plotly_chart(fig)

    df["publishedat"] = pd.to_datetime(df["publishedat"])

    # Extract date only (without time) for grouping
    df["date"] = df["publishedat"].dt.date

    # Pivot the DataFrame to create a matrix for the heatmap
    # Count sentiment occurrences for each source per day
    heatmap_data = df.pivot_table(
        index="date",
        columns="source",
        values="sentiment",
        aggfunc="count",
        fill_value=0,
    )

    # Plot the heatmap
    fig = px.imshow(
        heatmap_data,
        color_continuous_scale="YlGnBu",
        title="Sentiment Distribution Across Sources Over Time",
    )
    fig.update_layout(xaxis_title="Source",
                      yaxis_title="Date", xaxis_nticks=10)
    fig.update_xaxes(tickangle=-45)

    st.plotly_chart(fig)

    downloaded_images = download_images(df["urltoimage"].values)

    create_and_show_gif(downloaded_images)

    # Display summaries with highlighted keywords in an expander
    def highlight_keywords(text, keywords):
        for keyword in keywords:
            text = text.replace(
                keyword,
                f"<span style='background-color: #ffc107; color: white'>{keyword}</span>",
            )
        return text

    # 3D Cluster visualization of article embeddings
    st.header("3D Article Embedding Clusters")
    st.write("This visualization shows articles clustered by their semantic similarity. Similar articles appear closer together in 3D space.")
    
    # Generate embeddings for articles
    with st.spinner("Generating article embeddings..."):
        embeddings_3d = generate_article_embeddings(df)
        
    if embeddings_3d is not None and len(embeddings_3d) > 0:
        # Create 3D scatter plot with hover data showing article information
        fig = go.Figure(data=[go.Scatter3d(
            x=embeddings_3d[:, 0],
            y=embeddings_3d[:, 1],
            z=embeddings_3d[:, 2],
            mode='markers',
            marker=dict(
                size=5,
                color=pd.Categorical(df['sentiment']).codes,  # Color by sentiment
                colorscale='Viridis',
                opacity=0.8,
                colorbar=dict(title="Sentiment")
            ),
            text=[f"<b>{row['title']}</b><br>Source: {row['source']}<br>URL: <a href='{row['url']}' target='_blank'>{row['url']}</a>" 
                  for _, row in df.iterrows()],
            hoverinfo='text'
        )])
        
        # Update layout for better visualization
        fig.update_layout(
            title="3D Cluster Visualization of Article Embeddings",
            autosize=True,
            height=800,
            scene=dict(
                xaxis_title='Component 1',
                yaxis_title='Component 2',
                zaxis_title='Component 3',
                aspectmode='cube'
            ),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.info("Hover over points to see article details and click on URLs to read the original articles. Articles with similar content appear closer together in the 3D space.")
    else:
        st.error("Could not generate embeddings for visualization.")

    with st.expander("View All Summaries with Highlighted Keywords"):
        st.subheader("Summaries")
        for index, row in df.iterrows():
            summary = row["summary"]
            keywords = row["keywords"]
            highlighted_summary = highlight_keywords(summary, keywords)
            st.markdown(highlighted_summary, unsafe_allow_html=True)

    with st.expander("View Public Reddit Data"):
        # Reddit Word Cloud
        try:
            st.subheader("Reddit Keyword Extraction - Word Cloud")
            reddit_wordcloud = generate_wordcloud(data["reddit_keywords"])
            plt.figure(figsize=(10, 5))
            plt.imshow(reddit_wordcloud, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(plt)

            # Reddit Sentiment Analysis
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

            # Hot Discussion Points from Reddit
            st.subheader("Hot Discussion Points from Reddit")
            st.write(
                "Placeholder for Reddit hot discussion points (to be populated with real data)."
            )

        except Exception as e:
            st.error(f"Error: {e}")

