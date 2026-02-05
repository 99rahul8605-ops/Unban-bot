FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make run.py executable
RUN chmod +x run.py

# Create non-root user
RUN useradd -m -u 1000 botuser
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import requests; r=requests.get('http://localhost:10000/health', timeout=2); exit(0 if r.status_code==200 else 1)"

# Run the application
CMD ["python", "app.py"]
