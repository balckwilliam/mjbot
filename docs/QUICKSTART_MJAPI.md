# MJAPI 服务器快速入门 / MJAPI Server Quick Start

本指南将帮助您快速启动并测试 MJAPI 服务器。

This guide will help you quickly start and test the MJAPI server.

## 快速开始 / Quick Start

### 第一步：安装依赖 / Step 1: Install Dependencies

```bash
pip install flask>=2.0.0
```

或者安装完整依赖（推荐）：
Or install all dependencies (recommended):

```bash
pip install -r requirements.txt
```

### 第二步：启动 MJAPI 服务器 / Step 2: Start MJAPI Server

```bash
python online_game/mjapi_server.py
```

服务器将在 `http://0.0.0.0:5001` 上启动。
The server will start on `http://0.0.0.0:5001`.

您应该看到类似的输出：
You should see output similar to:

```
WARNING:root:PyTorch not available. MJAPI server will use random decisions.
2025-10-18 15:59:44,971 - __main__ - INFO - Starting MJAPI server on 0.0.0.0:5001
2025-10-18 15:59:44,971 - __main__ - INFO - Available models: ['mjbot-default']
```

### 第三步：测试服务器 / Step 3: Test Server

在另一个终端窗口中运行测试：
Run tests in another terminal window:

```bash
python online_game/test_mjapi_server.py
```

或者运行客户端示例：
Or run the client example:

```bash
python online_game/mjapi_client_example.py
```

如果一切正常，您应该看到测试通过的消息！
If everything works, you should see messages indicating tests passed!

### 第四步：连接 MahjongCopilot / Step 4: Connect MahjongCopilot

1. 打开 MahjongCopilot / Open MahjongCopilot
2. 进入设置 / Go to settings
3. 选择 MJAPI 作为 bot 类型 / Select MJAPI as bot type
4. 设置 URL 为 `http://localhost:5001`
5. 注册用户并配置用户名和密钥 / Register user and configure username and secret
   ```bash
   # 使用客户端快速注册
   python -c "
   from online_game.mjapi_client_example import MJAPIClient
   client = MJAPIClient('http://localhost:5001')
   secret = client.register('your_username')
   print(f'Username: your_username')
   print(f'Secret: {secret}')
   "
   ```
6. 保存设置并开始游戏！/ Save settings and start playing!

## 常见问题 / FAQ

### Q: 服务器启动失败

**A:** 检查以下几点：
1. 是否安装了 Flask：`pip install flask>=2.0.0`
2. 端口 5001 是否被占用：`lsof -i :5001` (Linux/Mac) 或 `netstat -ano | findstr :5001` (Windows)
3. 尝试使用其他端口：`python online_game/mjapi_server.py -p 8080`

### Q: MahjongCopilot 连接失败

**A:** 确认以下几点：
1. MJAPI 服务器正在运行
2. URL 配置正确（默认 `http://localhost:5001`）
3. 用户名和密钥正确
4. 防火墙没有阻止连接

### Q: AI 不工作或只是随机选择

**A:** 
1. 检查 PyTorch 是否安装：`pip install torch`
2. 确保模型文件存在于 `model/saved/` 目录
3. 查看服务器日志以获取详细错误信息

### Q: 如何更改端口？

**A:** 使用 `-p` 参数：
```bash
python online_game/mjapi_server.py -p 8080
```

记得在 MahjongCopilot 中也修改 URL 为 `http://localhost:8080`

### Q: 如何启用调试模式？

**A:** 使用 `-d` 参数：
```bash
python online_game/mjapi_server.py -d
```

### Q: 如何查看使用量？

**A:** 使用客户端查询：
```python
from online_game.mjapi_client_example import MJAPIClient
client = MJAPIClient('http://localhost:5001')
client.login('your_username', 'your_secret')
info = client.get_user_info()
print(f"Usage: {info['usage']}/{info['limit']}")
```

## 高级配置 / Advanced Configuration

### 多个服务器实例 / Multiple Server Instances

您可以同时运行多个服务器实例在不同端口：
You can run multiple server instances on different ports:

```bash
# 终端 1 / Terminal 1
python online_game/mjapi_server.py -p 5001

# 终端 2 / Terminal 2
python online_game/mjapi_server.py -p 5002
```

### 自定义模型 / Custom Models

要添加自定义模型，修改 `mjapi_server.py` 中的 `available_models` 列表：
To add custom models, modify the `available_models` list in `mjapi_server.py`:

```python
available_models = ["mjbot-default", "my-custom-model"]
```

### 生产环境部署 / Production Deployment

对于生产环境，建议：
For production, it's recommended to:

1. 使用 WSGI 服务器（如 gunicorn）：
   Use a WSGI server (like gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 online_game.mjapi_server:app
   ```

2. 配置 HTTPS / Configure HTTPS
3. 设置速率限制 / Set up rate limiting
4. 使用负载均衡器 / Use a load balancer

## 下一步 / Next Steps

- 阅读完整文档：[docs/MJAPI_SERVER.md](MJAPI_SERVER.md)
- 查看客户端示例：[online_game/mjapi_client_example.py](../online_game/mjapi_client_example.py)
- 了解 mjai 协议：https://mjai.app/docs/mjai-protocol
- 参与项目开发：https://github.com/balckwilliam/mjbot

---

🎉 **就这么简单！现在您可以使用 MahjongCopilot 与这个项目的 AI 一起玩麻将了！**

🎉 **That's it! Now you can play Mahjong with this project's AI through MahjongCopilot!**
