from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import asyncio
import os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import uvicorn

app = FastAPI(title="Crawl4AI API", description="Extract content and images from web pages", version="1.0.0")

class CrawlRequest(BaseModel):
    url: HttpUrl
    deepseek_api_key: Optional[str] = None

class CrawlResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    main_content_image_urls: List[str] = []
    markdown: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None

@app.get("/")
async def root():
    return {"message": "Crawl4AI API is running! Use POST /extract to crawl a webpage."}

@app.post("/extract", response_model=CrawlResponse)
async def extract_content(request: CrawlRequest):
    import time
    start_time = time.time()
    
    try:
        # Use API key from request or environment variable
        api_key = request.deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="DeepSeek API key is required. Provide it in the request or set DEEPSEEK_API_KEY environment variable.")
        
        # Browser config: headless, bigger viewport
        browser_conf = BrowserConfig(
            headless=True,
            viewport_width=1280,
            viewport_height=720
        )

        # JSON schema for extracting main content and image URLs
        extraction_schema = {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The exact verbatim main text content of the web page in markdown format."
                },
                "main_content_image_urls": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "An image url that appears within the main content of the web page. This image must be inside the main content of the page so you must exclude small logo images, icons, avatars and other images which aren't a core part of the main content. The image should be at least 600px in width."
                    },
                    "description": "An array of the exact image urls that appear within the main content of the web page. Extra images such as icons and images not relevant to the main content MUST be excluded."
                }
            },
            "required": ["content", "main_content_image_urls"]
        }

        # LLM config for DeepSeek
        llm_config = LLMConfig(
            provider="deepseek/deepseek-chat",
            api_token=api_key
        )

        # LLM extraction strategy with the specified prompt
        extraction_strategy = LLMExtractionStrategy(
            llm_config=llm_config,
            schema=extraction_schema,
            extraction_type="schema",
            instruction="""
            Identify the main content of the text (i.e., the article or newsletter body). 
            Provide the exact text for that main content verbatim, without summarizing or rewriting any part of it. 
            Exclude all non-essential elements such as banners, headers, footers, calls to action, ads, or purely navigational text. 
            Format this output as markdown using appropriate '#' characters as heading levels. 
            Exclude any promotional or sponsored content on your output. 
            
            Additionally, you must identify and extract the image urls within this main content. 
            These images must be inside the main content of the page so you must exclude small logo images, icons, avatars and other images which aren't a core part of the main content. 
            The images you extract should at least have a width of 600 pixels (px) so it can be included on our content.
            """
        )

        # Crawler run config
        run_conf = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            cache_mode=CacheMode.BYPASS,
            excluded_tags=["iframe", "nav", "header", "footer"]
        )

        async with AsyncWebCrawler(config=browser_conf) as crawler:
            result = await crawler.arun(url=str(request.url), config=run_conf)

            processing_time = time.time() - start_time

            if result.success:
                # Parse the extracted content
                extracted_data = {}
                content_text = ""
                image_urls = []
                
                if result.extracted_content:
                    try:
                        if isinstance(result.extracted_content, str):
                            # Try to parse as JSON string
                            import json
                            parsed_content = json.loads(result.extracted_content)
                            if isinstance(parsed_content, list) and len(parsed_content) > 0:
                                extracted_data = parsed_content[0]
                            elif isinstance(parsed_content, dict):
                                extracted_data = parsed_content
                        elif isinstance(result.extracted_content, list) and len(result.extracted_content) > 0:
                            extracted_data = result.extracted_content[0]
                        elif isinstance(result.extracted_content, dict):
                            extracted_data = result.extracted_content
                        
                        # Extract content and images safely
                        if isinstance(extracted_data, dict):
                            content_text = extracted_data.get("content", "")
                            image_urls = extracted_data.get("main_content_image_urls", [])
                            
                    except (json.JSONDecodeError, TypeError):
                        # If parsing fails, treat as empty
                        extracted_data = {}
                
                return CrawlResponse(
                    success=True,
                    content=content_text,
                    main_content_image_urls=image_urls,
                    markdown=result.markdown,
                    processing_time=processing_time
                )
            else:
                raise HTTPException(status_code=500, detail=result.error_message)

    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "crawl4ai-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, access_log=True, log_level="info") 