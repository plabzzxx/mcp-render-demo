from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import json
import asyncio
from typing import AsyncGenerator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quote API with MCP Support",
    description="A simple API that fetches random quotes from quotable.io, with MCP protocol support",
    version="2.0.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径,返回API信息"""
    return {
        "message": "Welcome to Quote API with MCP Support",
        "version": "2.0.0",
        "endpoints": {
            "get_quote": "/api/v1/get-quote",
            "health": "/health",
            "mcp": "/mcp",
            "mcp_sse": "/mcp/sse"
        },
        "mcp_info": {
            "protocol_version": "2024-11-05",
            "transport": "Streamable HTTP",
            "tools": ["get_random_quote"]
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

        # 禁用SSL验证以避免证书过期问题
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
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


# ==================== MCP Protocol Implementation ====================

# MCP工具定义
MCP_TOOLS = [
    {
        "name": "get_random_quote",
        "description": "获取一条随机的名人名言。返回包含名言内容、作者、标签等信息。",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


async def handle_mcp_initialize(params: dict) -> dict:
    """处理MCP初始化请求"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "quote-api-mcp-server",
            "version": "2.0.0"
        }
    }


async def handle_mcp_tools_list(params: dict) -> dict:
    """返回可用工具列表"""
    return {
        "tools": MCP_TOOLS
    }


async def handle_mcp_tools_call(params: dict) -> dict:
    """执行工具调用"""
    tool_name = params.get("name")

    if tool_name == "get_random_quote":
        # 调用内部API获取名言
        external_api_url = "https://api.quotable.io/random"

        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                response = await client.get(external_api_url)
                response.raise_for_status()
                quote_data = response.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(quote_data, indent=2, ensure_ascii=False)
                        }
                    ]
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error fetching quote: {str(e)}"
                    }
                ],
                "isError": True
            }
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


async def handle_mcp_request(request_data: dict) -> dict:
    """处理MCP请求并返回响应"""
    method = request_data.get("method")
    params = request_data.get("params", {})

    if method == "initialize":
        result = await handle_mcp_initialize(params)
    elif method == "tools/list":
        result = await handle_mcp_tools_list(params)
    elif method == "tools/call":
        result = await handle_mcp_tools_call(params)
    else:
        raise ValueError(f"Unknown method: {method}")

    return {
        "jsonrpc": "2.0",
        "id": request_data.get("id"),
        "result": result
    }


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    MCP协议端点 (Streamable HTTP模式)
    支持标准的JSON-RPC 2.0请求
    """
    try:
        request_data = await request.json()
        logger.info(f"MCP Request: {request_data.get('method')}")

        response = await handle_mcp_request(request_data)
        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"MCP Error: {str(e)}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_data.get("id") if 'request_data' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            },
            status_code=500
        )


@app.get("/mcp/sse")
async def mcp_sse_endpoint():
    """
    MCP SSE端点 (Server-Sent Events)
    用于实时流式通信
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        # 发送初始连接事件
        yield f"data: {json.dumps({'type': 'connected', 'serverInfo': {'name': 'quote-api-mcp-server', 'version': '2.0.0'}})}\n\n"

        # 保持连接
        while True:
            await asyncio.sleep(30)
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

