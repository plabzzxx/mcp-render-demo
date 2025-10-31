from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quote API",
    description="A simple API that fetches random quotes from quotable.io",
    version="1.0.0"
)

@app.get("/")
async def root():
    """根路径,返回API信息"""
    return {
        "message": "Welcome to Quote API",
        "endpoints": {
            "get_quote": "/api/v1/get-quote"
        }
    }

@app.get("/api/v1/get-quote")
async def get_quote():
    """
    从quotable.io获取随机名言
    
    Returns:
        JSON: 包含名言内容、作者等信息的JSON对象
    
    Raises:
        HTTPException: 当外部API调用失败时返回500错误
    """
    external_api_url = "https://api.quotable.io/random"
    
    try:
        logger.info(f"Fetching quote from {external_api_url}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(external_api_url)
            response.raise_for_status()
            
            quote_data = response.json()
            logger.info(f"Successfully fetched quote: {quote_data.get('_id')}")
            
            return JSONResponse(content=quote_data, status_code=200)
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch quote from external API. Status: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch quote from external API."
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching the quote."
        )

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

