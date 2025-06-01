FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
ENV LOG_LEVEL=DEBUG

WORKDIR /app

# Create logs directory
RUN mkdir -p /app/logs && chmod 777 /app/logs

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run with environment variables
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"] 