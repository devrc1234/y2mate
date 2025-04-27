# Start from a slim Python image
FROM python:3.11-slim

# Install ffmpeg and other necessary tools
RUN apt-get update && apt-get install -y ffmpeg curl

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port where FastAPI app will run
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
