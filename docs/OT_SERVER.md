# OT Server 使用文档 / OT Server Documentation

## 简介 / Introduction

OT (Online-Trained) Server 提供了与 [@latorc/MahjongCopilot](https://github.com/latorc/MahjongCopilot) 项目兼容的 HTTP API 接口，允许其他应用程序通过 HTTP 请求获取麻将 AI 的决策建议。

The OT (Online-Trained) Server provides an HTTP API interface compatible with the [@latorc/MahjongCopilot](https://github.com/latorc/MahjongCopilot) project, allowing other applications to obtain Mahjong AI decision recommendations via HTTP requests.

## 功能特性 / Features

- ✅ 兼容 MahjongCopilot 的 OT 服务器接口 / Compatible with MahjongCopilot's OT server interface
- ✅ 支持四人麻将和三人麻将 / Supports 4-player and 3-player Mahjong
- ✅ 支持 API 密钥认证 / Supports API key authentication
- ✅ 支持 gzip 压缩请求 / Supports gzip-compressed requests
- ✅ 提供健康检查端点 / Provides health check endpoint

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
python online_game/ot_server.py
```

默认情况下，服务器将在 `0.0.0.0:5000` 上启动。
By default, the server will start on `0.0.0.0:5000`.

### 命令行参数 / Command Line Arguments

```bash
python online_game/ot_server.py [选项/options]

选项 / Options:
  -H, --host HOST       服务器绑定的主机地址（默认: 0.0.0.0）
                        Host to bind the server to (default: 0.0.0.0)
  
  -p, --port PORT       服务器绑定的端口（默认: 5000）
                        Port to bind the server to (default: 5000)
  
  --api-key KEY         API 密钥用于认证（可选）
                        API key for authentication (optional)
  
  -d, --debug           启用调试模式
                        Enable debug mode
```

### 示例 / Examples

启动服务器在 8080 端口：
Start server on port 8080:
```bash
python online_game/ot_server.py -p 8080
```

启用 API 密钥认证：
Enable API key authentication:
```bash
python online_game/ot_server.py --api-key "your-secret-key"
```

启用调试模式：
Enable debug mode:
```bash
python online_game/ot_server.py -d
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
    "ai_loaded": true
}
```

### 2. 认证检查 / Authorization Check

**端点 / Endpoint:** `POST /check`

**描述 / Description:** 验证 API 密钥 / Verify API key

**请求头 / Headers:**
```
Authorization: your-api-key
```

**响应示例 / Response Example:**
```json
{
    "result": "success"
}
```

### 3. 四人麻将决策 / 4-Player Mahjong Decision

**端点 / Endpoint:** `POST /react_batch`

**描述 / Description:** 获取四人麻将的 AI 决策 / Get AI decisions for 4-player Mahjong

**请求头 / Headers:**
```
Content-Type: application/json
Authorization: your-api-key  (如果启用了认证 / if authentication is enabled)
Content-Encoding: gzip  (可选，用于压缩请求 / optional, for compressed requests)
```

**请求体 / Request Body:**
```json
{
    "obs": [
        [/* observation array */]
    ],
    "masks": [
        [/* action mask array */]
    ]
}
```

**响应示例 / Response Example:**
```json
{
    "actions": [0],
    "q_out": [[1.0, 0.0, 0.0, ...]],
    "masks": [[true, false, false, ...]],
    "is_greedy": [true]
}
```

### 4. 三人麻将决策 / 3-Player Mahjong Decision

**端点 / Endpoint:** `POST /react_batch_3p`

**描述 / Description:** 获取三人麻将的 AI 决策 / Get AI decisions for 3-player Mahjong

请求和响应格式与 `/react_batch` 相同。
Request and response format is the same as `/react_batch`.

## 与 MahjongCopilot 集成 / Integration with MahjongCopilot

在 MahjongCopilot 的设置中：
In MahjongCopilot settings:

1. 选择 Akagi OT2 模型 / Select Akagi OT2 model
2. 设置 URL：`http://localhost:5000` （或您的服务器地址 / or your server address）
3. 如果启用了 API 密钥，设置相应的密钥 / If API key is enabled, set the corresponding key
4. 保存设置 / Save settings

## 数据格式说明 / Data Format Description

### 观察数据 (obs) / Observation Data

观察数据是一个多维数组，包含游戏状态信息，例如：
Observation data is a multi-dimensional array containing game state information, such as:
- 手牌 / Hand tiles
- 弃牌 / Discarded tiles
- 宝牌 / Dora tiles
- 得分 / Scores
- 等等 / etc.

### 动作掩码 (masks) / Action Masks

动作掩码是一个布尔数组，指示哪些动作是有效的：
Action masks is a boolean array indicating which actions are valid:
- `true`: 该动作可以执行 / This action can be performed
- `false`: 该动作不可执行 / This action cannot be performed

### 动作 (actions) / Actions

返回的动作索引对应于可执行的游戏动作，例如：
The returned action index corresponds to executable game actions, such as:
- 0-33: 打出对应的牌 / Discard corresponding tile
- 34-36: 吃牌 / Chi
- 37: 碰牌 / Pon
- 38: 杠牌 / Kan
- 39: 立直 / Riichi
- 40: 和牌 / Tsumo/Ron
- 等等 / etc.

## 故障排除 / Troubleshooting

### 问题：服务器启动失败 / Issue: Server fails to start

**解决方案 / Solution:**
1. 确保已安装 Flask：`pip install flask>=2.0.0`
2. 检查端口是否被占用 / Check if the port is already in use
3. 尝试使用不同的端口：`python online_game/ot_server.py -p 8080`

### 问题：AI 模型未加载 / Issue: AI model not loaded

**解决方案 / Solution:**
1. 确保 PyTorch 已安装 / Ensure PyTorch is installed
2. 检查模型文件是否存在于 `model/saved/` 目录 / Check if model files exist in `model/saved/` directory
3. 查看服务器日志获取详细错误信息 / Check server logs for detailed error messages

### 问题：认证失败 / Issue: Authentication fails

**解决方案 / Solution:**
1. 确保在请求头中包含正确的 API 密钥 / Ensure correct API key is included in request headers
2. API 密钥应在 `Authorization` 头中 / API key should be in `Authorization` header
3. 检查服务器启动时是否设置了 `--api-key` 参数 / Check if `--api-key` parameter was set when starting the server

## 性能优化 / Performance Optimization

1. **使用 gzip 压缩** / Use gzip compression
   - 对于大型请求，使用 gzip 压缩可以显著减少网络传输时间
   - For large requests, using gzip compression can significantly reduce network transfer time

2. **批处理请求** / Batch requests
   - 将多个决策请求合并为一个批处理请求
   - Combine multiple decision requests into one batch request

3. **GPU 加速** / GPU acceleration
   - 如果可用，确保 PyTorch 使用 GPU 进行推理
   - If available, ensure PyTorch uses GPU for inference

## 安全建议 / Security Recommendations

1. 在生产环境中始终使用 API 密钥 / Always use API key in production
2. 使用 HTTPS 加密通信 / Use HTTPS for encrypted communication
3. 限制访问 IP 地址 / Restrict access IP addresses
4. 定期更新 API 密钥 / Regularly update API keys

## 许可证 / License

本项目使用 GNU GPL v3 许可协议。
This project is licensed under GNU GPL v3.
