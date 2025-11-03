# Use a slim Python image for a smaller final size
FROM python:3.10-slim

WORKDIR /app

# Copy and install only the LLM service's dependencies
COPY services/llm-service/requirements.txt .
RUN pip install --no-cache-dir --timeout 600 -r requirements.txt

# Copy only the LLM service's code
COPY services/llm-service/app ./app

# Create a non-root user for security
RUN useradd --create-home appuser
USER appuser

# NOTE: The command in the docker-compose.yml file will override this CMD
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]