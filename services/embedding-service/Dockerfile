# Use a slim Python image for a smaller final size
FROM python:3.10-slim

WORKDIR /app

# Install CPU-only PyTorch separately to avoid large GPU dependencies
# The --index-url directs pip to the specific PyTorch CPU download page
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy and install only the Embedding service's dependencies
COPY services/embedding-service/requirements.txt .
RUN pip install --no-cache-dir --timeout 3600 -r requirements.txt

# Copy only the Embedding service's code
COPY services/embedding-service/app ./app

# Create a non-root user for security
RUN useradd --create-home appuser
USER appuser

# NOTE: The command in the docker-compose.yml file will override this CMD
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
