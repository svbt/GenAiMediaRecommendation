# Inherit from the shared base image
FROM genaimediarecommendation-base:latest

WORKDIR /app

# Only copy the application code
COPY . .

# NOTE: The command in the docker-compose.yml file will override this CMD
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
