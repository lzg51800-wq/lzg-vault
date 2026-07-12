# OpenClaw 本地 + 联网大模型部署指南

> 本机已完成 OpenClaw 的「本地运行 + 联网调用」双通道配置。本文档为干净版操作手册。

## 1. 概览

OpenClaw 是本地优先的 AI Agent 框架，可同时接入**本地大模型**（Ollama 引擎）与**云端模型**（OpenAI 兼容协议）。本机配置原则：**本地优先，联网兜底**——默认走本地模型（免费/隐私/离线），重任务切换云端。

## 2. 本机环境

| 项目 | 配置 |
|---|---|
| 机型 | Apple M5 Max / 18 核 / 36GB 统一内存 |
| OpenClaw | 2026.6.1（配置目录 `~/.openclaw`） |
| Ollama | 0.31.2（本地推理引擎，监听 `:11434`） |

## 3. 已配置的模型

| 模型 | 入口 | 类型 | 大小 | 说明 |
|---|---|---|---|---|
| `gemma4:26b` | `ollama`（**默认**） | 本地 | 17 GB | 质量最强，本地首选 |
| `qwen2.5:latest` | `ollama` | 本地 | 4.7 GB | 轻量，中文地道，省内存 |
| `deepseek-v4-pro` | `deepseek`（联网） | 云端 | — | 最强云端火力，按量计费 |
| `deepseek-v4-flash` | `deepseek`（联网） | 云端 | — | 更快更便宜的云端档 |

> 简选建议：日常/省内存用 `qwen2.5`；复杂代码/长文档用 `gemma4:26b`；烧脑推理/难题切 `deepseek-v4-pro`。

## 4. 配置文件

- 路径：`~/.openclaw/openclaw.json`
- 内容：所有 provider、默认模型、API key 都在此处
- 修改前会自动备份为 `openclaw.json.bak.*`

## 5. 启动与使用

### 5.1 启动 Gateway

```bash
openclaw gateway --bind loopback --port 18790
```

- 浏览器访问 **http://localhost:18790**（首次需填网关令牌，见 5.4）
- 已配置**登录自启**（见第 7 节），日常无需手动启动

### 5.2 命令行对话

```bash
# 默认本地 gemma4:26b
openclaw agent --agent main -m "帮我写个快速排序"

# 单次指定联网模型（不改默认）
openclaw agent --agent main --model deepseek/deepseek-v4-pro -m "解释注意力机制"
```

### 5.3 切换默认模型

```bash
openclaw config set agents.defaults.model.primary ollama/gemma4:26b        # 本地
openclaw config set agents.defaults.model.primary deepseek/deepseek-v4-pro # 联网
# 改完需重启 gateway 生效：
pkill -f "openclaw gateway"; sleep 1
openclaw gateway --bind loopback --port 18790
```

图形界面也可在底部模型选择器直接切换。

### 5.4 浏览器登录（网关令牌）

浏览器首次连接需填**网关令牌**，令牌存放在配置文件 `gateway.auth.token` 字段。

若想免粘贴，可用 `openclaw dashboard` 命令，会自动在 URL 中夹带一次性令牌打开浏览器。

## 6. 联网模型费用（DeepSeek V4 Pro）

- 按量计费：输入 **¥3** / 输出 **¥6**（每百万 token，永久 2.5 折）
- 注册即送**每月 100 万 token 免费额度**
- **高峰时段（9–12 点、14–18 点）价格翻倍**，重度任务错峰更省
- 官方无包月订阅；如需固定月费可选云厂商 Coding Plan（如腾讯云 ¥39.9/月，含 DeepSeek V3.2 档 + 多模型自动路由）

## 7. 开机自启（macOS launchd）

| 文件 | 作用 |
|---|---|
| `~/Library/LaunchAgents/com.openclaw.gateway.plist` | 自启任务（RunAtLoad + KeepAlive，登录自启、崩溃自拉） |
| `~/load-openclaw-gateway.command` | 一键加载脚本（Finder 双击，Terminal 运行，含重注册/端口冲突处理） |

说明：plist 放入 `~/Library/LaunchAgents/` 后，macOS 会在**下次登录自动加载**；若想当前会话立即生效，在真实 Terminal.app 中双击运行上面的 `.command` 脚本即可。

## 8. 删除本地无用模型（Ollama）

```bash
ollama list                # 1. 先查看现有模型
ollama rm 模型名:标签       # 2. 删除（同一模型多标签需逐个删）
ollama prune               # 3. 清理悬空层，真正释放磁盘
ollama list                # 4. 确认结果
```

注意：删除**默认/正在使用**的模型前，先切换默认模型或停止 gateway，否则下次请求会失败。

## 9. 常见问题

- **浏览器连不上 localhost:18790**：gateway 未运行，用 5.1 命令启动（或确认开机自启已生效）。
- **模型"自我介绍"不准确**：本地模型不知道自己是谁，问"你是哪个模型"会瞎猜；判断当前模型请看 gateway 日志的 `agent model:` 行或 UI 模型选择器。
- **DeepSeek 调用失败**：检查 API key 是否已写入 `~/.openclaw/openclaw.json`、账户余额是否充足、是否处于高峰翻倍时段。
