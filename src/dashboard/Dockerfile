# Add this line to set the PYTHONPATH to include the src directory
# ENV PYTHONPATH=/app/src

FROM python:3.10-slim

# Set the working directory inside the container to the dashboard folder
WORKDIR /app/src/dashboard

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file and install dependencies
COPY app.py /app/

COPY requirements.txt /app/

# Install dependencies manually
# RUN pip3 install seaborn

RUN pip3 install -r /app/requirements.txt

# Copy the entire project folder into the container
COPY . /app

# Expose the port that Streamlit uses
EXPOSE 8501

# Healthcheck to ensure the app is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set the entry point to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "/app/app.py"]
