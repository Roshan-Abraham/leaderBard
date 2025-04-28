FROM python:3.9-slim

WORKDIR /app

# Install dependencies including curl for healthcheck and wait-for-it for postgres waiting
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wait-for-it \
    gnupg2 \
    lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PostgreSQL client tools from official repository
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-client-14 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a directory for persistent data
RUN mkdir -p /data

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for database
# PostgreSQL connection config
ENV DB_TYPE="postgres" \
    POSTGRES_HOST="db" \
    POSTGRES_PORT="5432" \
    POSTGRES_USER="dashboard_user" \
    POSTGRES_PASSWORD="dashboard_password" \
    POSTGRES_DB="dashboard" \
    DB_PATH="/data/dashboard.db"

# Set up healthcheck to ensure app is running properly
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:8501/ || exit 1

# Command to run the application
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
