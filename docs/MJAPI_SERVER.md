# MJAPI Server 使用文档 / MJAPI Server Documentation

## 简介 / Introduction

MJAPI Server 提供了与 [@latorc/MahjongCopilot](https://github.com/latorc/MahjongCopilot) 项目兼容的 MJAPI HTTP API 接口，使用 mjai 协议进行游戏通信，允许其他应用程序通过 HTTP 请求获取麻将 AI 的决策建议。

The MJAPI Server provides an HTTP API interface compatible with the [@latorc/MahjongCopilot](https://github.com/latorc/MahjongCopilot) project, using the mjai protocol for game communication, allowing other applications to obtain Mahjong AI decision recommendations via HTTP requests.

## 功能特性 / Features

- ✅ 兼容 MahjongCopilot 的 MJAPI 接口 / Compatible with MahjongCopilot's MJAPI interface
- ✅ 使用 mjai 协议进行游戏通信 / Uses mjai protocol for game communication
- ✅ 支持用户注册、登录和认证 / Supports user registration, login, and authentication
- ✅ 支持多个 AI 模型 / Supports multiple AI models
- ✅ 提供使用量和限额管理 / Provides usage and quota management
- ✅ 支持单个和批量消息处理 / Supports single and batch message processing

## 安装依赖 / Installation

```bash
pip install flask>=2.0.0
```

或安装完整依赖 / Or install all dependencies:

```bash
pip install -r requirements.txt
```

## 启动服务器 / Starting the Server

### 基本用法 / Basic Usage

```bash
python online_game/mjapi_server.py
```

默认情况下，服务器将在 `0.0.0.0:5001` 上启动。
By default, the server will start on `0.0.0.0:5001`.

### 命令行参数 / Command Line Arguments

```bash
python online_game/mjapi_server.py [选项/options]

选项 / Options:
  -H, --host HOST       服务器绑定的主机地址（默认: 0.0.0.0）
                        Host to bind the server to (default: 0.0.0.0)
  
  -p, --port PORT       服务器绑定的端口（默认: 5001）
                        Port to bind the server to (default: 5001)
  
  -d, --debug           启用调试模式
                        Enable debug mode
```

### 示例 / Examples

启动服务器在 8080 端口：
Start server on port 8080:
```bash
python online_game/mjapi_server.py -p 8080
```

启用调试模式：
Enable debug mode:
```bash
python online_game/mjapi_server.py -d
```

## API 接口 / API Endpoints

### 1. 健康检查 / Health Check

**端点 / Endpoint:** `GET /health`

**描述 / Description:** 检查服务器运行状态 / Check server status

**响应示例 / Response Example:**
```json
{
    "status": "healthy",
    "torch_available": true,
    "models": ["mjbot-default"]
}
```

### 2. 用户注册 / User Registration

**端点 / Endpoint:** `POST /user/register`

**描述 / Description:** 注册新用户 / Register a new user

**请求体 / Request Body:**
```json
{
    "name": "username"
}
```

**响应示例 / Response Example:**
```json
{
    "name": "username",
    "secret": "generated-secret-uuid"
}
```

### 3. 用户登录 / User Login

**端点 / Endpoint:** `POST /user/login`

**描述 / Description:** 用户登录并获取令牌 / User login and get token

**请求体 / Request Body:**
```json
{
    "name": "username",
    "secret": "secret-from-registration"
}
```

**响应示例 / Response Example:**
```json
{
    "id": "token-uuid",
    "name": "username"
}
```

### 4. 获取用户信息 / Get User Info

**端点 / Endpoint:** `GET /user`

**描述 / Description:** 获取当前用户信息 / Get current user information

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**响应示例 / Response Example:**
```json
{
    "name": "username",
    "usage": 42,
    "limit": 10000
}
```

### 5. 用户登出 / User Logout

**端点 / Endpoint:** `POST /user/logout`

**描述 / Description:** 用户登出 / User logout

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**响应示例 / Response Example:**
```json
{
    "result": "success"
}
```

### 6. 列出可用模型 / List Models

**端点 / Endpoint:** `GET /mjai/list`

**描述 / Description:** 获取可用的 AI 模型列表 / Get list of available AI models

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**响应示例 / Response Example:**
```json
{
    "models": ["mjbot-default"]
}
```

### 7. 获取使用量 / Get Usage

**端点 / Endpoint:** `GET /mjai/usage`

**描述 / Description:** 获取当前使用量 / Get current usage

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**响应示例 / Response Example:**
```json
{
    "used": 42
}
```

### 8. 获取使用限额 / Get Limit

**端点 / Endpoint:** `GET /mjai/limit`

**描述 / Description:** 获取使用限额信息 / Get usage limit information

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**响应示例 / Response Example:**
```json
{
    "limit": 10000,
    "used": 42
}
```

### 9. 启动机器人 / Start Bot

**端点 / Endpoint:** `POST /mjai/start`

**描述 / Description:** 启动 mjai 机器人会话 / Start mjai bot session

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**请求体 / Request Body:**
```json
{
    "id": 0,
    "bound": 256,
    "model": "mjbot-default"
}
```

**响应示例 / Response Example:**
```json
{
    "result": "success"
}
```

### 10. 单个消息查询 / Single Action Query

**端点 / Endpoint:** `POST /mjai/act`

**描述 / Description:** 发送单个 mjai 消息并获取 AI 反应 / Send single mjai message and get AI reaction

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**请求体 / Request Body:**
```json
{
    "seq": 0,
    "data": {
        "type": "tsumo",
        "actor": 0,
        "pai": "5p",
        "can_act": true
    }
}
```

**响应示例 / Response Example:**
```json
{
    "act": {
        "type": "dahai",
        "pai": "9m",
        "actor": 0
    }
}
```

### 11. 批量消息查询 / Batch Actions Query

**端点 / Endpoint:** `POST /mjai/batch`

**描述 / Description:** 发送多个 mjai 消息并获取最后的 AI 反应 / Send multiple mjai messages and get last AI reaction

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**请求体 / Request Body:**
```json
[
    {
        "seq": 0,
        "data": {
            "type": "start_game",
            "id": 0
        }
    },
    {
        "seq": 1,
        "data": {
            "type": "start_kyoku",
            "bakaze": "E",
            "kyoku": 1,
            "honba": 0,
            "oya": 0,
            "scores": [25000, 25000, 25000, 25000],
            "dora_marker": "5z",
            "tehais": [...]
        }
    },
    {
        "seq": 2,
        "data": {
            "type": "tsumo",
            "actor": 0,
            "pai": "5p",
            "can_act": true
        }
    }
]
```

**响应示例 / Response Example:**
```json
{
    "act": {
        "type": "dahai",
        "pai": "9m",
        "actor": 0
    }
}
```

### 12. 停止机器人 / Stop Bot

**端点 / Endpoint:** `POST /mjai/stop`

**描述 / Description:** 停止 mjai 机器人会话 / Stop mjai bot session

**请求头 / Headers:**
```
Authorization: Bearer {token}
```

**响应示例 / Response Example:**
```json
{
    "result": "success"
}
```

## MJAI 协议说明 / MJAI Protocol Description

MJAPI 服务器使用 [mjai 协议](https://mjai.app/docs/mjai-protocol) 进行游戏通信。

The MJAPI server uses the [mjai protocol](https://mjai.app/docs/mjai-protocol) for game communication.

### 主要消息类型 / Main Message Types

- **start_game**: 游戏开始 / Game start
- **start_kyoku**: 局开始 / Round start
- **tsumo**: 摸牌 / Draw tile
- **dahai**: 打牌 / Discard tile
- **reach**: 立直 / Riichi declaration
- **pon**: 碰 / Pon (triplet)
- **chi**: 吃 / Chi (sequence)
- **daiminkan**: 大明杠 / Open kan
- **ankan**: 暗杠 / Closed kan
- **kakan**: 加杠 / Added kan
- **hora**: 和牌 / Win
- **ryukyoku**: 流局 / Draw
- **end_kyoku**: 局结束 / Round end
- **none**: 无操作 / No action

### 牌表示法 / Tile Notation

- **数牌 / Number tiles**: `1m`-`9m` (万), `1p`-`9p` (筒), `1s`-`9s` (索)
- **字牌 / Honor tiles**: `1z`-`7z` (东南西北白发中)
- **赤牌 / Red tiles**: `5mr`, `5pr`, `5sr` (赤5)

#### 备选字牌表示法 / Alternate Honor Tile Notation

服务器也支持以下单字符字牌表示法（自动转换为标准 mjai 格式）：
The server also supports the following single-character honor tile notation (automatically converted to standard mjai format):

- **E** → `1z` (东风 / East wind)
- **S** → `2z` (南风 / South wind)
- **W** → `3z` (西风 / West wind)
- **N** → `4z` (北风 / North wind)
- **P** → `5z` (白板 / White dragon)
- **F** → `6z` (发财 / Green dragon)
- **C** → `7z` (红中 / Red dragon)

## 与 MahjongCopilot 集成 / Integration with MahjongCopilot

在 MahjongCopilot 的设置中：
In MahjongCopilot settings:

1. 选择 MJAPI 作为 bot 类型 / Select MJAPI as bot type
2. 设置 URL：`http://localhost:5001` （或您的服务器地址 / or your server address）
3. 注册用户并使用返回的用户名和密钥进行配置 / Register a user and configure with the returned username and secret
4. 保存设置 / Save settings

## 测试服务器 / Testing the Server

运行测试脚本：
Run the test script:

```bash
python online_game/test_mjapi_server.py --url http://localhost:5001
```

测试脚本将验证所有 API 端点的功能。
The test script will verify the functionality of all API endpoints.

## 故障排除 / Troubleshooting

### 问题：服务器启动失败 / Issue: Server fails to start

**解决方案 / Solution:**
1. 确保已安装 Flask：`pip install flask>=2.0.0`
2. 检查端口是否被占用 / Check if the port is already in use
3. 尝试使用不同的端口：`python online_game/mjapi_server.py -p 8080`

### 问题：AI 模型未加载 / Issue: AI model not loaded

**解决方案 / Solution:**
1. 确保 PyTorch 已安装 / Ensure PyTorch is installed
2. 检查模型文件是否存在于 `model/saved/` 目录 / Check if model files exist in `model/saved/` directory
3. 查看服务器日志获取详细错误信息 / Check server logs for detailed error messages

### 问题：认证失败 / Issue: Authentication fails

**解决方案 / Solution:**
1. 确保在请求头中包含正确的令牌 / Ensure correct token is included in request headers
2. 令牌应在 `Authorization: Bearer {token}` 头中 / Token should be in `Authorization: Bearer {token}` header
3. 检查用户是否已登录 / Check if user is logged in

## 安全建议 / Security Recommendations

1. 在生产环境中使用 HTTPS / Use HTTPS in production
2. 实现速率限制以防止滥用 / Implement rate limiting to prevent abuse
3. 定期更新用户密钥 / Regularly update user secrets
4. 限制访问 IP 地址 / Restrict access IP addresses
5. 使用防火墙保护服务器 / Use firewall to protect server

## 性能优化 / Performance Optimization

1. **使用批量请求** / Use batch requests
   - 将多个消息合并为一个批量请求可以减少网络开销
   - Combining multiple messages into one batch request reduces network overhead

2. **GPU 加速** / GPU acceleration
   - 如果可用，确保 PyTorch 使用 GPU 进行推理
   - If available, ensure PyTorch uses GPU for inference

3. **缓存** / Caching
   - 考虑缓存常见的游戏状态和决策
   - Consider caching common game states and decisions

## 许可证 / License

本项目使用 GNU GPL v3 许可协议。
This project is licensed under GNU GPL v3.

## 参考资料 / References

- [MJAI Protocol Specification](https://mjai.app/docs/mjai-protocol)
- [MahjongCopilot Repository](https://github.com/latorc/MahjongCopilot)
- [API Documentation](https://pastebin.com/wks80EsZ) (Password: EaSXeZycr4)
