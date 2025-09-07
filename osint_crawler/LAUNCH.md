# OSINT Crawler Launch Manual

## Overview
This OSINT (Open Source Intelligence) crawler is a Flask-based web application that performs automated intelligence gathering using DuckDuckGo search and web crawling. It can search for information about names, emails, usernames, or companies.

## Prerequisites
- Docker installed and running
- Terminal/command line access
- Internet connection

## Project Structure
```
osint_crawler/
├── Dockerfile
├── requirements.txt
├── run.py
├── app/
│   ├── .env          # Configuration file
│   ├── __init__.py
│   ├── config.py
│   ├── controllers/
│   ├── models/
│   ├── services/
│   └── views/
└── crawler/
```

## 1. Build the Docker Container

Navigate to the project directory and build the container:

```bash
cd /path/to/your/crawler/project
docker build -t osint-crawler osint_crawler
```

**Expected output:**
```
[+] Building 20.0s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 228B
 => [internal] load metadata for docker.io/library/python:3.11-slim
 => [internal] load .dockerignore
 => => transferring context: 6.89kB
 => [1/5] FROM docker.io/library/python:3.11-slim
 => [2/5] WORKDIR /app
 => [3/5] COPY requirements.txt ./
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt
 => [5/5] COPY . .
 => exporting to image
 => => exporting layers
 => => exporting manifest sha256:...
 => => naming to docker.io/library/osint-crawler:latest
```

## 2. Run the Container

Start the container in detached mode with port mapping:

```bash
docker run -d -p 5000:5000 --name osint-container osint-crawler
```

**Parameters explained:**
- `-d`: Run in detached mode (background)
- `-p 5000:5000`: Map host port 5000 to container port 5000
- `--name osint-container`: Name the container for easy reference

**Expected output:**
```
08f372a3d59acc76f31789a2a92ea7e0a58e5315503e7a5b1960c39a3b19014e
```

## 3. Verify Container is Running

Check if the container is running:

```bash
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                    NAMES
08f372a3d59a   osint-crawler  "python run.py"          2 minutes ago   Up 2 minutes   0.0.0.0:5000->5000/tcp  osint-container
```

## 4. Test the API

### Health Check
Test if the server is responding:

```bash
curl http://localhost:5000/
```

### Single Domain Crawl
Crawl a specific domain:

```bash
curl "http://localhost:5000/crawl/domain?url=https://example.com"
```

**Expected output:**
```json
{
  "discovered_at": "2025-09-07T21:05:49.652175",
  "domain": "https://example.com",
  "ip": "93.184.216.34",
  "registrar": "N/A",
  "risk_score": 0.1,
  "title": "Example Domain"
}
```

### Full OSINT Pipeline
Run the complete OSINT analysis using the target from `.env`:

```bash
curl "http://localhost:5000/osint"
```

**Expected output:**
```json
{
  "seed": "Ernests Smalikis",
  "seed_type": "name",
  "results": {
    "general": [...],
    "documents": [...],
    "company": [...]
  }
}
```

## 5. Configure Target

Edit the `osint_crawler/app/.env` file to change the target:

```env
# For a name
TARGET_SEED=John Doe
TARGET_TYPE=name

# For an email
TARGET_SEED=john.doe@example.com
TARGET_TYPE=email

# For a username
TARGET_SEED=johndoe123
TARGET_TYPE=username

# For a company
TARGET_SEED=Example Corp
TARGET_TYPE=company
```

After changing the target, rebuild and restart the container:

```bash
docker build -t osint-crawler osint_crawler
docker stop osint-container
docker rm osint-container
docker run -d -p 5000:5000 --name osint-container osint-crawler
```

## 6. View Container Logs

Monitor the application logs:

```bash
docker logs osint-container
```

Or follow logs in real-time:

```bash
docker logs -f osint-container
```

## 7. Stop the Container

Stop the running container:

```bash
docker stop osint-container
```

## 8. Remove the Container

Remove the stopped container:

```bash
docker rm osint-container
```

## 9. Clean Up (Optional)

Remove the Docker image:

```bash
docker rmi osint-crawler
```

## Troubleshooting

### Container Won't Start
Check if port 5000 is already in use:

```bash
lsof -i :5000
```

Use a different port:

```bash
docker run -d -p 5001:5000 --name osint-container osint-crawler
```

### Build Fails
Ensure you're in the correct directory and have proper permissions:

```bash
cd /path/to/crawler
ls -la
```

### API Returns Errors
Check container logs:

```bash
docker logs osint-container
```

### No Search Results
- The target may have limited online presence
- Try a more common name like "John Doe" for testing
- Check your internet connection

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/crawl/domain?url=<url>` | GET | Crawl a single domain |
| `/osint` | GET | Run full OSINT pipeline |

## Security Notes
- The application runs on `0.0.0.0:5000` inside the container
- For production use, consider adding authentication
- Be mindful of rate limits when using search engines
- Respect robots.txt and terms of service of target websites

## Performance Tips
- The full OSINT pipeline may take 30-60 seconds due to web crawling
- Results are cached per query during execution
- Consider the ethical implications of OSINT gathering
