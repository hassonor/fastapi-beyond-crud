# Dockerfile
FROM python:3.12-slim

# Prevent Python from creating .pyc files and ensure logs are flushed
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into /app/src
COPY src/ /app/src/
# Make sure src/__init__.py has "app = FastAPI()" or similar

# Expose the port your FastAPI app will run on (internal container port)
EXPOSE 8000

# If your main app is "src/__init__.py" with "app", this works:
CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8000"]
