FROM python:3.10-slim

WORKDIR /app

# Copy everything into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI (Uvicorn)
CMD ["python", "app.py"]
