import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

async def main():
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
        api_token=""
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
        # Replace with your target URL
        url = "https://www.statnews.com/2025/07/08/fda-staff-morale-departures-rfk-jr-sued-covid-shots-hospital-lobbying-trump-tax-cut-bill-dc-diagnosis-newsletter/"  # Change this to {{ $json.url }} in your actual implementation
        
        result = await crawler.arun(url=url, config=run_conf)

        if result.success:
            print("Extraction successful!")
            print("Markdown content:", result.markdown[:500] + "..." if len(result.markdown) > 500 else result.markdown)
            print("Raw HTML length:", len(result.html))
            print("Links found:", len(result.links))
            
            if result.extracted_content:
                print("\nExtracted JSON content:")
                print(result.extracted_content)
            else:
                print("No extracted content found")
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
     asyncio.run(main())
