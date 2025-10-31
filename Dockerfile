FROM python:3.10-slim

WORKDIR /app

# Copy all files
COPY . /app

# Copy config file properly and set permissions
COPY .streamlit/config.toml /app/.streamlit/config.toml
RUN chmod -R 777 /app/.streamlit

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 7860

# Run Streamlit with explicit config path
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--config", "/app/.streamlit/config.toml"]
