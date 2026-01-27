# Docker Setup for Backend

Quick setup using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations:**
   ```bash
   docker-compose exec backend npm run migrate
   ```

3. **Seed database (optional):**
   ```bash
   docker-compose exec backend npm run seed
   ```

4. **Check logs:**
   ```bash
   docker-compose logs -f backend
   ```

## Docker Compose File

Create `docker-compose.yml` in the backend directory:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: llm-scan-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: llm_scan_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    container_name: llm-scan-backend
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      PORT: 3000
      DB_HOST: mysql
      DB_PORT: 3306
      DB_USER: root
      DB_PASSWORD: rootpassword
      DB_NAME: llm_scan_db
    depends_on:
      mysql:
        condition: service_healthy
    volumes:
      - ./src:/app/src
    command: npm start

volumes:
  mysql_data:
```

## Dockerfile

Create `Dockerfile` in the backend directory:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```
