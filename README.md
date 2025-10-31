# MCP-Test: Quote API

一个简单的FastAPI应用,用于从quotable.io获取随机名言。

## 功能

- **GET /api/v1/get-quote**: 获取随机名言
- **GET /health**: 健康检查端点
- **GET /**: API信息

## 本地运行

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 启动服务:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. 访问API:
```bash
curl http://localhost:8000/api/v1/get-quote
```

## 部署到Render

1. 将代码推送到GitHub仓库
2. 在Render创建新的Web Service
3. 连接GitHub仓库
4. 配置构建命令: `pip install -r requirements.txt`
5. 配置启动命令: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## API响应示例

```json
{
  "_id": "H1T0-3-MZo",
  "content": "If you want to know what a man's like, take a good look at how he treats his inferiors, not his equals.",
  "author": "J.K. Rowling",
  "tags": ["Character"],
  "authorSlug": "j-k-rowling",
  "length": 102,
  "dateAdded": "2020-04-14",
  "dateModified": "2020-04-14"
}
```

