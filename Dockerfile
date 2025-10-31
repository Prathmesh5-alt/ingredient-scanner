FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Create .streamlit directory with proper permissions
RUN mkdir -p /app/.streamlit && chmod -R 777 /app/.streamlit

# Copy config file explicitly (important!)
COPY .streamlit /app/.streamlit

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 7860

# Run Streamlit app with correct config path
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--config", "/app/.streamlit/config.toml"]
