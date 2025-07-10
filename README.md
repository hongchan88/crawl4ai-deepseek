# Crawl4AI API

A FastAPI web service that extracts main content and image URLs from web pages using Crawl4AI and DeepSeek LLM.

## Features

- Extract main content from web pages as markdown
- Find image URLs (≥600px width) within main content
- Exclude navigation, headers, footers, and promotional content
- RESTful API with JSON responses
- Built-in health check endpoint

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your DeepSeek API key (optional - can also be provided in requests):
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key-here"
```

## Local Development

Run the API locally:
```bash
python app.py
```

Or use uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /extract
Extract content from a webpage.

**Request:**
```json
{
  "url": "https://example.com/article",
  "deepseek_api_key": "your-api-key" // Optional if set in environment
}
```

**Response:**
```json
{
  "success": true,
  "content": "# Article Title\n\nArticle content in markdown...",
  "main_content_image_urls": ["https://example.com/image1.jpg"],
  "markdown": "Full page markdown content...",
  "processing_time": 15.2
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "crawl4ai-api"
}
```

## Testing

Test the API using curl:
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.statnews.com/2025/07/08/fda-staff-morale-departures-rfk-jr-sued-covid-shots-hospital-lobbying-trump-tax-cut-bill-dc-diagnosis-newsletter/",
    "deepseek_api_key": "your-api-key"
  }'
```

## Deployment Options

### 1. Railway (Recommended)
1. Create account at [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variable: `DEEPSEEK_API_KEY=your-key`
4. Deploy automatically

### 2. Render
1. Create account at [Render.com](https://render.com)
2. Create new Web Service from GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `DEEPSEEK_API_KEY=your-key`

### 3. Heroku
1. Create account at [Heroku.com](https://heroku.com)
2. Create new app
3. Add buildpack: `heroku/python`
4. Set config var: `DEEPSEEK_API_KEY=your-key`
5. Deploy via Git or GitHub

### 4. DigitalOcean App Platform
1. Create account at [DigitalOcean](https://digitalocean.com)
2. Use App Platform to deploy from GitHub
3. Set environment variable: `DEEPSEEK_API_KEY=your-key`

### 5. Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t crawl4ai-api .
docker run -p 8000:8000 -e DEEPSEEK_API_KEY=your-key crawl4ai-api
```

## Production Considerations

- Set up proper logging
- Add rate limiting
- Use environment variables for sensitive data
- Consider adding authentication
- Monitor API usage and costs
- Add request/response validation
- Set up health monitoring

## Error Handling

The API returns detailed error messages and appropriate HTTP status codes:
- 400: Bad Request (missing API key, invalid URL)
- 500: Internal Server Error (crawling/extraction failures)

## Performance

- Typical extraction time: 10-30 seconds
- Memory usage: ~500MB-1GB per request
- Concurrent requests: Limited by DeepSeek API rate limits 