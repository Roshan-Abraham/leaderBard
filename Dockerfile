FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a directory for persistent data
RUN mkdir -p /data

# Expose Streamlit port
EXPOSE 8501

# Set environment variable for database
ENV DB_PATH="/data/dashboard.db"

# Command to run the application
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
