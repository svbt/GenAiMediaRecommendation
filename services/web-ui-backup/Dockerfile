# Stage 1: build dependencies
FROM node:18-alpine

WORKDIR /app

# Copy only package files first for better caching
COPY package*.json ./

RUN npm install

# Copy rest of the code
COPY . .

EXPOSE 3000

# Default command for dev
CMD ["npm", "start"]
