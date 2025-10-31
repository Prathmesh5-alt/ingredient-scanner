# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all project files into container
COPY . /app

# Ensure .streamlit directory exists and is writable
RUN mkdir -p /app/.streamlit && chmod -R 777 /app/.streamlit

# Copy your Streamlit config
COPY .streamlit/config.toml /app/.streamlit/config.toml

# ✅ Set HOME to /app so Streamlit uses /app/.streamlit (not /.streamlit)
ENV HOME=/app

# Disable usage stats and telemetry
ENV STREAMLIT_BROWSER_GATHERUSAGESTATS=false

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port (Hugging Face default: 7860)
EXPOSE 7860

# ✅ Run the app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
