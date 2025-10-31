# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files into container
COPY . /app

# Make sure .streamlit exists and is writable
RUN mkdir -p /app/.streamlit && chmod -R 777 /app/.streamlit

# Copy the Streamlit config file
COPY .streamlit/config.toml /app/.streamlit/config.toml

# Tell Streamlit to use this directory
ENV STREAMLIT_CONFIG_DIR=/app/.streamlit
ENV HOME=/app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit’s default port
EXPOSE 7860

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]
