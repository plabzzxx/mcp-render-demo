#!/usr/bin/env python3
"""
MCP Server for Quote API
这个MCP服务器将Quote API暴露给支持MCP协议的AI助手
"""

import asyncio
import json
import sys
from typing import Any
import httpx

# MCP协议的基本实现
class MCPServer:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.tools = [
            {
                "name": "get_random_quote",
                "description": "获取一条随机的名人名言。返回包含名言内容、作者、标签等信息的JSON对象。",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    async def handle_initialize(self, params: dict) -> dict:
        """处理初始化请求"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "quote-api-server",
                "version": "1.0.0"
            }
        }
    
    async def handle_tools_list(self, params: dict) -> dict:
        """返回可用工具列表"""
        return {
            "tools": self.tools
        }
    
    async def handle_tools_call(self, params: dict) -> dict:
        """执行工具调用"""
        tool_name = params.get("name")
        
        if tool_name == "get_random_quote":
            return await self.get_random_quote()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def get_random_quote(self) -> dict:
        """调用Quote API获取随机名言"""
        url = f"{self.api_base_url}/api/v1/get-quote"
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url)
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
    
    async def handle_request(self, request: dict) -> dict:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return await self.handle_initialize(params)
        elif method == "tools/list":
            return await self.handle_tools_list(params)
        elif method == "tools/call":
            return await self.handle_tools_call(params)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def run(self):
        """运行MCP服务器(stdio模式)"""
        while True:
            try:
                # 从stdin读取JSON-RPC请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                request = json.loads(line)
                request_id = request.get("id")
                
                try:
                    result = await self.handle_request(request)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                except Exception as e:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }
                
                # 输出响应到stdout
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }), file=sys.stderr, flush=True)


async def main():
    api_base_url = "https://mcp-render-demo.onrender.com"
    server = MCPServer(api_base_url)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

