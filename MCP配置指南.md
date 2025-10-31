# MCP配置指南 - Quote API

## 📋 项目信息

- **服务名称**: Quote API MCP Server
- **部署URL**: https://mcp-render-demo.onrender.com
- **API端点**: `/api/v1/get-quote`
- **功能**: 获取随机名人名言

---

## 🚀 方法一: 使用Claude Desktop (推荐)

### 1. 安装依赖

确保你的系统已安装Python 3.10+和httpx:

```bash
pip install httpx
```

### 2. 配置Claude Desktop

找到Claude Desktop的配置文件:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 3. 添加MCP服务器配置

在配置文件中添加以下内容:

```json
{
  "mcpServers": {
    "quote-api": {
      "command": "python",
      "args": [
        "C:/Users/jason/Desktop/plabmcp/mcp-server.py"
      ],
      "env": {}
    }
  }
}
```

**注意**: 请将路径替换为你的实际路径。

### 4. 重启Claude Desktop

关闭并重新打开Claude Desktop,你应该能在工具列表中看到 `get_random_quote` 工具。

### 5. 测试使用

在Claude中输入:

```
请帮我获取一条随机名言
```

Claude会自动调用MCP工具获取名言。

---

## 🔧 方法二: 使用其他支持MCP的AI助手

### Cline (VS Code扩展)

1. 安装Cline扩展
2. 打开设置 → MCP Servers
3. 添加配置:

```json
{
  "quote-api": {
    "command": "python",
    "args": ["C:/Users/jason/Desktop/plabmcp/mcp-server.py"]
  }
}
```

### Continue.dev

1. 打开 `~/.continue/config.json`
2. 添加MCP服务器:

```json
{
  "mcpServers": [
    {
      "name": "quote-api",
      "command": "python",
      "args": ["C:/Users/jason/Desktop/plabmcp/mcp-server.py"]
    }
  ]
}
```

---

## 🌐 方法三: 直接HTTP调用 (不使用MCP)

如果AI助手不支持MCP,可以直接调用HTTP API:

### cURL示例

```bash
curl https://mcp-render-demo.onrender.com/api/v1/get-quote
```

### Python示例

```python
import requests

response = requests.get("https://mcp-render-demo.onrender.com/api/v1/get-quote")
quote = response.json()

print(f"名言: {quote['content']}")
print(f"作者: {quote['author']}")
```

### JavaScript示例

```javascript
fetch('https://mcp-render-demo.onrender.com/api/v1/get-quote')
  .then(response => response.json())
  .then(data => {
    console.log(`名言: ${data.content}`);
    console.log(`作者: ${data.author}`);
  });
```

---

## 📝 API响应格式

```json
{
  "_id": "ALcsEfDR7FL",
  "content": "The cautious seldom err.",
  "author": "Confucius",
  "tags": ["Wisdom"],
  "authorSlug": "confucius",
  "length": 24,
  "dateAdded": "2021-03-28",
  "dateModified": "2023-04-14"
}
```

### 字段说明

- `_id`: 名言的唯一标识符
- `content`: 名言内容
- `author`: 作者名称
- `tags`: 标签数组
- `authorSlug`: 作者的URL友好标识
- `length`: 名言字符长度
- `dateAdded`: 添加日期
- `dateModified`: 修改日期

---

## 🔍 测试MCP服务器

### 手动测试

```bash
# 运行MCP服务器
python mcp-server.py

# 发送测试请求(在另一个终端)
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python mcp-server.py
```

### 验证工具列表

```bash
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python mcp-server.py
```

### 调用工具

```bash
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_random_quote"}}' | python mcp-server.py
```

---

## 🛠️ 故障排查

### 问题1: MCP服务器无法启动

**解决方案**:
- 检查Python版本: `python --version` (需要3.10+)
- 安装依赖: `pip install httpx`
- 检查文件路径是否正确

### 问题2: Claude Desktop看不到工具

**解决方案**:
- 确认配置文件路径正确
- 检查JSON格式是否有效
- 完全重启Claude Desktop
- 查看Claude Desktop日志

### 问题3: API调用失败

**解决方案**:
- 检查网络连接
- 确认Render服务状态: https://dashboard.render.com
- 查看服务日志

---

## 📊 服务监控

### 查看服务状态

访问: https://dashboard.render.com/web/srv-d42198jipnbc73buvf1g

### 查看日志

```bash
# 使用Render CLI
render logs -s srv-d42198jipnbc73buvf1g
```

### 健康检查

```bash
curl https://mcp-render-demo.onrender.com/health
```

---

## 🔐 安全注意事项

1. **当前配置**: API是公开的,无需认证
2. **生产环境建议**:
   - 添加API密钥认证
   - 实施速率限制
   - 启用HTTPS(已启用)
   - 添加CORS配置

---

## 🚀 未来扩展

### 集成LangChain

```python
from langchain.tools import Tool

quote_tool = Tool(
    name="get_random_quote",
    description="获取随机名人名言",
    func=lambda x: requests.get(
        "https://mcp-render-demo.onrender.com/api/v1/get-quote"
    ).json()
)
```

### 添加更多端点

- `/api/v1/quotes/author/{author}` - 按作者查询
- `/api/v1/quotes/tag/{tag}` - 按标签查询
- `/api/v1/quotes/random?count=5` - 获取多条名言

---

## 📞 支持

- **GitHub仓库**: https://github.com/plabzzxx/mcp-render-demo
- **Render Dashboard**: https://dashboard.render.com
- **API文档**: https://mcp-render-demo.onrender.com/docs (FastAPI自动生成)

---

## ✅ 验收标准检查

- [x] Render服务状态显示为 "Live"
- [x] 公开服务URL可访问: https://mcp-render-demo.onrender.com
- [x] API端点返回正确的JSON数据
- [x] MCP配置文件已生成
- [x] 文档完整

**项目状态**: ✅ 已完成并成功部署!

