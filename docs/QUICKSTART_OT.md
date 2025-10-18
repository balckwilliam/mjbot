# OT 服务器快速入门 / OT Server Quick Start

## 5分钟快速开始 / Get Started in 5 Minutes

### 第一步：安装依赖 / Step 1: Install Dependencies

```bash
pip install flask requests
```

### 第二步：启动服务器 / Step 2: Start Server

```bash
cd /path/to/Mahjong-AI
python online_game/ot_server.py
```

您将看到 / You will see:
```
INFO:__main__:Starting OT server on 0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

### 第三步：测试服务器 / Step 3: Test Server

在另一个终端运行 / In another terminal, run:
```bash
python online_game/test_ot_server.py
```

如果看到 "All tests completed!"，说明服务器工作正常！
If you see "All tests completed!", the server is working correctly!

### 第四步：连接 MahjongCopilot / Step 4: Connect MahjongCopilot

1. 打开 MahjongCopilot / Open MahjongCopilot
2. 进入设置 / Go to Settings
3. 选择模型类型：**Akagi OT2** / Select Model Type: **Akagi OT2**
4. 设置 URL：`http://localhost:5000` / Set URL: `http://localhost:5000`
5. 保存并开始游戏 / Save and start playing!

## 常见问题 / Common Issues

### Q: 启动失败，提示 "Address already in use"

**A:** 端口被占用，使用其他端口：
```bash
python online_game/ot_server.py -p 8080
```
记得在 MahjongCopilot 中也修改 URL 为 `http://localhost:8080`

### Q: AI 决策是随机的

**A:** 这是正常的！如果没有安装 PyTorch 或加载模型，服务器会使用随机决策作为后备方案。

要使用真实的 AI 模型：
1. 安装 PyTorch: `pip install torch`
2. 下载模型文件（参考主 README.md）
3. 将模型放在 `model/saved/` 目录下
4. 重启服务器

### Q: MahjongCopilot 连接失败

**A:** 检查：
1. OT 服务器是否在运行？
2. URL 是否正确？
3. 防火墙是否阻止连接？

## 下一步 / Next Steps

- 📖 阅读完整文档：[OT_SERVER.md](OT_SERVER.md)
- 🔧 查看集成指南：[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- 💻 查看代码示例：`online_game/ot_client_example.py`

## 获取帮助 / Get Help

- 查看日志：使用 `-d` 参数启动调试模式
  ```bash
  python online_game/ot_server.py -d
  ```

- 在 GitHub 上提问 / Ask on GitHub:
  https://github.com/balckwilliam/Mahjong-AI/issues

## 命令速查 / Command Cheatsheet

```bash
# 启动服务器（默认端口 5000）
python online_game/ot_server.py

# 指定端口
python online_game/ot_server.py -p 8080

# 使用 API 密钥
python online_game/ot_server.py --api-key "your-key"

# 调试模式
python online_game/ot_server.py -d

# 测试服务器
python online_game/test_ot_server.py --url http://localhost:5000

# 运行示例
python online_game/ot_client_example.py
```

---

🎉 **就这么简单！现在您可以使用 MahjongCopilot 与这个项目的 AI 一起玩麻将了！**

🎉 **That's it! Now you can play Mahjong with this project's AI through MahjongCopilot!**
