# 集成指南 / Integration Guide

## 与 MahjongCopilot 集成 / Integration with MahjongCopilot

### 快速开始 / Quick Start

#### 1. 启动 OT 服务器 / Start OT Server

```bash
# 基本启动 / Basic start
python online_game/ot_server.py

# 或指定端口 / Or specify port
python online_game/ot_server.py -p 5000

# 使用 API 密钥 / With API key
python online_game/ot_server.py --api-key "your-secret-key"
```

#### 2. 配置 MahjongCopilot

在 MahjongCopilot 设置中：
In MahjongCopilot settings:

1. **模型类型 / Model Type**: 选择 "Akagi OT2" / Select "Akagi OT2"
2. **服务器 URL / Server URL**: `http://localhost:5000` (或您的服务器地址 / or your server address)
3. **API 密钥 / API Key**: 如果服务器设置了密钥，填入对应的密钥 / If server has key, enter the key
4. **保存设置 / Save Settings**

#### 3. 开始使用 / Start Playing

启动 MahjongCopilot 并开始游戏，AI 将通过 OT 服务器提供决策建议。
Start MahjongCopilot and begin playing, the AI will provide decision recommendations through the OT server.

### 架构说明 / Architecture

```
┌─────────────────┐         HTTP API         ┌─────────────────┐
│                 │  ───────────────────────> │                 │
│  MahjongCopilot │                           │   OT Server     │
│                 │  <─────────────────────── │  (This Project) │
└─────────────────┘    JSON (可压缩/gzip)     └─────────────────┘
                                                      │
                                                      │ 调用/Calls
                                                      ▼
                                              ┌─────────────────┐
                                              │   AI Models     │
                                              │  (PyTorch)      │
                                              └─────────────────┘
```

### API 端点 / API Endpoints

| 端点 / Endpoint | 方法 / Method | 说明 / Description |
|----------------|--------------|-------------------|
| `/health` | GET | 健康检查 / Health check |
| `/check` | POST | 认证检查 / Auth check |
| `/react_batch` | POST | 四人麻将决策 / 4P decisions |
| `/react_batch_3p` | POST | 三人麻将决策 / 3P decisions |

### 数据流程 / Data Flow

1. **游戏状态 → 观察数据 / Game State → Observation**
   - MahjongCopilot 将游戏状态转换为观察数组
   - MahjongCopilot converts game state to observation array

2. **发送请求 / Send Request**
   - 通过 HTTP POST 发送观察数据和动作掩码
   - Sends observation data and action masks via HTTP POST

3. **AI 推理 / AI Inference**
   - OT 服务器使用 AI 模型计算最佳动作
   - OT server uses AI model to compute best action

4. **返回决策 / Return Decision**
   - 返回选择的动作、Q值和其他信息
   - Returns selected action, Q-values, and other info

5. **执行动作 / Execute Action**
   - MahjongCopilot 展示 AI 建议或自动执行
   - MahjongCopilot displays AI suggestion or auto-executes

### 故障排除 / Troubleshooting

#### 问题：无法连接到服务器 / Cannot connect to server

**检查清单 / Checklist:**
- [ ] OT 服务器是否正在运行？ / Is OT server running?
- [ ] 端口是否正确？ / Is the port correct?
- [ ] 防火墙是否阻止连接？ / Is firewall blocking connection?

**解决方案 / Solution:**
```bash
# 检查服务器是否运行 / Check if server is running
curl http://localhost:5000/health

# 如果没有响应，启动服务器 / If no response, start server
python online_game/ot_server.py -p 5000
```

#### 问题：认证失败 / Authentication failed

**解决方案 / Solution:**
- 确保 API 密钥匹配 / Ensure API key matches
- 服务器端：`--api-key "your-key"`
- 客户端：在 MahjongCopilot 设置中填入相同的密钥 / Enter same key in MahjongCopilot settings

#### 问题：AI 决策质量差 / Poor AI decision quality

**原因 / Reason:**
服务器日志显示 "PyTorch not available" 或 "AI not loaded"
Server log shows "PyTorch not available" or "AI not loaded"

**解决方案 / Solution:**
1. 安装 PyTorch / Install PyTorch:
   ```bash
   pip install torch
   ```

2. 下载并放置模型文件 / Download and place model files:
   - 将训练好的模型放在 `model/saved/` 目录
   - Place trained models in `model/saved/` directory
   - 参考 README.md 获取模型下载链接
   - Refer to README.md for model download links

3. 重启 OT 服务器 / Restart OT server

### 性能优化 / Performance Optimization

#### 1. 使用 GPU 加速 / Use GPU Acceleration

如果有 NVIDIA GPU：
If you have NVIDIA GPU:

```bash
# 安装 CUDA 版本的 PyTorch / Install CUDA version of PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 启动服务器 / Start server
python online_game/ot_server.py
```

服务器将自动使用 GPU 进行推理。
Server will automatically use GPU for inference.

#### 2. 批处理优化 / Batch Processing

OT 服务器支持批处理多个决策请求：
OT server supports batching multiple decision requests:

```python
# 一次处理多个观察 / Process multiple observations at once
data = {
    'obs': [obs1, obs2, obs3],
    'masks': [mask1, mask2, mask3]
}
```

#### 3. 压缩传输 / Compressed Transfer

对于大型数据，使用 gzip 压缩可以减少网络延迟：
For large data, gzip compression reduces network latency:

```python
import gzip
import json

# 压缩请求 / Compress request
data = json.dumps(post_data)
compressed = gzip.compress(data.encode('utf-8'))

# 发送压缩数据 / Send compressed data
headers = {'Content-Encoding': 'gzip'}
requests.post(url, data=compressed, headers=headers)
```

### 高级配置 / Advanced Configuration

#### 使用生产级 WSGI 服务器 / Use Production WSGI Server

开发时可以使用 Flask 内置服务器，但生产环境建议使用 Gunicorn 或 uWSGI：
For development, Flask's built-in server is fine, but use Gunicorn or uWSGI in production:

```bash
# 安装 Gunicorn / Install Gunicorn
pip install gunicorn

# 启动 / Start
gunicorn -w 4 -b 0.0.0.0:5000 online_game.ot_server:app
```

#### 使用 NGINX 反向代理 / Use NGINX Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 启用 HTTPS / Enable HTTPS

```bash
# 使用 Let's Encrypt 获取证书 / Get certificate with Let's Encrypt
certbot --nginx -d your-domain.com

# 或使用自签名证书（仅测试）/ Or use self-signed cert (testing only)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365
```

### 监控和日志 / Monitoring and Logging

#### 启用调试日志 / Enable Debug Logging

```bash
python online_game/ot_server.py -d
```

#### 监控性能 / Monitor Performance

查看服务器日志以监控：
Check server logs to monitor:
- 请求响应时间 / Request response time
- 错误率 / Error rate
- AI 模型加载状态 / AI model load status

### 安全建议 / Security Recommendations

1. **生产环境必须使用 API 密钥 / Always use API key in production**
   ```bash
   python online_game/ot_server.py --api-key "$(openssl rand -hex 32)"
   ```

2. **使用 HTTPS 加密通信 / Use HTTPS for encrypted communication**

3. **限制访问 IP / Restrict access IPs**
   - 使用防火墙规则 / Use firewall rules
   - 或在 NGINX 中配置 / Or configure in NGINX

4. **定期更新依赖 / Regularly update dependencies**
   ```bash
   pip install --upgrade flask requests
   ```

### 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！
Issues and Pull Requests are welcome!

如果您发现 bug 或有功能建议，请：
If you find bugs or have feature suggestions, please:
1. 在 GitHub 上开 Issue / Open an issue on GitHub
2. 描述问题和复现步骤 / Describe the problem and steps to reproduce
3. 如果可能，提供修复的 PR / If possible, provide a PR with a fix

### 许可证 / License

本项目使用 GNU GPL v3 许可协议。
This project is licensed under GNU GPL v3.
