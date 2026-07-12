---
tags:
  - AI/飞书
created: 2026-07-12
---

# 飞书多 Agent 绑定配置（方案 B：3个独立机器人）

> 每个飞书机器人对应一个独立 Agent，无需前缀，直接对话
> 部署日期：2026-07-12 | 平台：OpenClaw @ 腾讯云 Lighthouse

---

## 架构总览

```
飞书企业
├── 投研助理💰 Bot (cli_xxx1) ──→ main Agent
├── 学习助手📚 Bot (cli_xxx2) ──→ study Agent
└── 日常问答💬 Bot (cli_xxx3) ──→ assistant Agent
        │
   OpenClaw Gateway (单进程)
   openclaw-lark 插件 (WebSocket 长连接，无需公网回调)
```

**核心原理**：同一飞书企业下创建 3 个机器人应用，每个在 OpenClaw 中作为一个 account，通过**顶层 `bindings`** 字段路由到不同 Agent（注意：`bindings` 是顶层字段，不在 `session` 下，否则会报 `session: Invalid input`）。

---

## 第 1 步：飞书开放平台创建 3 个自建应用

### 1.1 打开飞书开放平台

访问 https://open.feishu.cn/app ，登录你的飞书账号。

### 1.2 创建 3 个企业自建应用

依次创建 3 个应用，填写信息：

| 应用 | 名称 | 描述 |
|:--|:--|:--|
| 应用 1 | 投研助理 | 金融投资研究助手，提供行情分析、新闻简报 |
| 应用 2 | 学习助手 | 知识整理和笔记生成，辅助学习 |
| 应用 3 | 日常问答 | 日常快速问答，天气/翻译/百科等 |

每个应用的操作：
1. 点击「创建企业自建应用」
2. 填写名称和描述
3. 上传一个图标（可选，用默认也行）

### 1.3 添加机器人能力

每个应用都需要：
1. 进入应用 → 左侧菜单「添加应用能力」
2. 选择「机器人」，开启
3. 配置机器人名称和描述

### 1.4 复制凭证

每个应用在「凭证与基础信息」页面，复制：
- **App ID**（格式：`cli_xxx`）
- **App Secret**

❗ **重要**：App Secret 妥善保密，不要泄露。

### 1.5 配置权限

每个应用在「权限管理」中，搜索并开通以下权限：

**必需权限**：
- `im:message`（发送消息给用户）
- `im:message:send_as_bot`（以机器人身份发消息）
- `im:message:readonly`（读取消息）
- `im:chat:readonly`（读取群信息）
- `contact:user.base:readonly`（读取用户基本信息）

**可选权限**（如需飞书文档/云盘功能）：
- `docx:document`（读写文档）
- `drive:file:upload`（上传文件）
- `drive:file:download`（下载文件）
- `wiki:node:read`（读取知识库）

### 1.6 配置事件订阅（WebSocket 模式）

每个应用：
1. 进入「事件与回调」→「事件配置」
2. 添加事件：`im.message.receive_v1`（接收消息）
3. **重要**：选择「使用长连接接收事件」（WebSocket 模式）
   - 这样不需要公网回调 URL
   - 龙虾服务器主动连接飞书，无需暴露端口

### 1.7 发布应用

每个应用：
1. 在「版本管理与发布」页面，创建版本
2. 设置可用范围（可以先设自己，后续扩展）
3. 提交发布（企业自建应用通常即时生效）

---

## 第 2 步：修改龙虾配置（一键脚本）

SSH 登录服务器后，依次执行以下命令：

### 2.1 备份

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak-feishu
```

### 2.2 运行配置脚本

复制以下整段命令，粘贴到服务器终端执行（用 Python 安全修改 JSON，不会格式错误）：

```bash
python3 << 'PYEOF'
import json

path = "/home/ubuntu/.openclaw/openclaw.json"
with open(path, "r") as f:
    config = json.load(f)

# 1. 启用 openclaw-lark 插件
config["plugins"]["entries"]["openclaw-lark"]["enabled"] = True

# 2. 添加 feishu channel（主机器人放顶层，其他放 accounts）
config["channels"]["feishu"] = {
    "enabled": True,
    "appId": "cli_aad9a120f4755bc0",
    "appSecret": "qxkHLJ0W8GD9hcSUpfvIhcrIS1w5J7j7",
    "dmPolicy": "allowlist",
    "allowFrom": ["ou_68688a60d7dd6691c32ecc0e82a4b760"],
    "accounts": {
        "study": {
            "appId": "cli_aad9a1b15438dbfb",
            "appSecret": "X5hJkI3vQYD7xRv7odyDtgdaPC1QZt3E"
        },
        "assistant": {
            "appId": "cli_aad9a21c6af8dbe0",
            "appSecret": "MJTt1cK7AAjYbzuQPnKOmc76qYJHy5x6"
        }
    }
}

# 3. 添加 bindings 路由规则（⚠️ 顶层字段，千万别放 session 下！）
config["bindings"] = [
    {"agentId": "study", "match": {"channel": "feishu", "accountId": "study"}},
    {"agentId": "assistant", "match": {"channel": "feishu", "accountId": "assistant"}}
]
# 默认 agent 通过 agents.list[].default: true 标记（不存在 defaultAgent 字段）

with open(path, "w") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("OK: openclaw-lark enabled + feishu channel + bindings configured")
PYEOF
```

### 2.3 配置说明

脚本只改 3 处，其余全部保持原样：

| 改动 | 位置 | 内容 |
|:--|:--|:--|
| 1 | `plugins.entries.openclaw-lark` | `enabled` 从 false 改为 true |
| 2 | `channels.feishu`（新增） | 3 个 account：主机器人(顶层) + study + assistant |
| 3 | `bindings`（顶层新增，非 session 下） | study→study agent、assistant→assistant agent、主机器人→main(default:true) |

**路由逻辑**：
- 来自投研助理机器人的消息 → main agent 处理
- 来自学习助手机器人的消息 → study agent 处理
- 来自日常问答机器人的消息 → assistant agent 处理

---

## 第 3 步：重启与验证

### 3.1 验证配置

```bash
openclaw config validate
```

### 3.2 重启网关

```bash
openclaw gateway restart
```

### 3.3 查看日志

```bash
openclaw logs --follow
```

看到飞书 3 个 account 都连接成功：
```
[feishu] account "main" connected (WebSocket)
[feishu] account "study" connected (WebSocket)
[feishu] account "assistant" connected (WebSocket)
```

### 3.4 飞书验证

在飞书中找到 3 个机器人，分别发消息测试：

| 测试 | 操作 | 期望回复 |
|:--|:--|:--|
| 投研助理 | 发「中国银行今天走势如何」 | 投研助理回复行情分析 |
| 学习助手 | 发「帮我整理二次函数知识点」 | 学习助手回复结构化笔记 |
| 日常问答 | 发「今天上海天气怎么样」 | 日常问答回复天气信息 |

---

## 第 4 步：群聊配置（可选）

如果想在飞书群里使用机器人：

```json
"feishu": {
  "enabled": true,
  "appId": "cli_xxx",
  "appSecret": "xxx",
  "groupPolicy": "allowlist",
  "groupAllowFrom": ["oc_群组ID"],
  "groups": {
    "*": {
      "enabled": true,
      "requireMention": true
    }
  },
  "accounts": { ... }
}
```

- `requireMention: true`：群里需要 @机器人 才响应
- 群组 ID（`oc_xxx`）：在群里 @机器人 后查看 `openclaw logs --follow` 中的 `chat_id`

---

## 故障排查

| 问题 | 解决方案 |
|:--|:--|
| 机器人无响应 | 检查 `openclaw logs --follow`，确认 WebSocket 连接成功 |
| 权限不足 | 检查飞书应用权限是否全部开通，应用是否已发布 |
| 消息路由错误 | 检查**顶层** `bindings`（不是 session.bindings），accountId 与 accounts 的 key 一致，agentId 与 agents.list[].id 一致 |
| App Secret 错误 | 在飞书开放平台重置 Secret，更新配置后 `openclaw gateway restart` |
| 飞书二维码无反应 | 运行 `openclaw channels login --channel feishu`，选择手动设置 |

---

## 回滚方法

```bash
cp ~/.openclaw/openclaw.json.bak-feishu ~/.openclaw/openclaw.json
openclaw gateway restart
```

---

## 附录：完整 channels + session 配置（改动后）

```json
{
  "channels": {
    "openclaw-weixin": {
      "accounts": {}
    },
    "lightclawbot": {
      "accounts": {
        "100049404376": {
          "apiKey": "8ee228a96d9355efe1c249c5eca66a4c29ec7732"
        }
      },
      "enabled": true
    },
    "feishu": {
      "enabled": true,
      "appId": "cli_投研助理AppID",
      "appSecret": "投研助理AppSecret",
      "dmPolicy": "allowlist",
      "allowFrom": ["ou_68688a60d7dd6691c32ecc0e82a4b760"],
      "accounts": {
        "study": {
          "appId": "cli_学习助手AppID",
          "appSecret": "学习助手AppSecret"
        },
        "assistant": {
          "appId": "cli_日常问答AppID",
          "appSecret": "日常问答AppSecret"
        }
      }
    }
  },
  "bindings": [
    { "agentId": "study", "match": { "channel": "feishu", "accountId": "study" } },
    { "agentId": "assistant", "match": { "channel": "feishu", "accountId": "assistant" } }
  ],
  "agents": {
    "list": [
      { "id": "main", "default": true }
    ]
  }
}
```

---

---

## 最终配置状态（2026-07-12 已验证 ✅）

### 验证结果

3 个飞书机器人全部独立运行正常：

| 机器人 | 测试消息 | 回复结果 |
|:--|:--|:--|
| 投研助理💰 | 股票类问题 | 输出中国银行完整分析报告（调用 westock-data 等金融工具） |
| 学习助手📚 | 什么是递归 | 输出递归概念讲解 + 代码示例 |
| 日常问答💬 | 1+1 等于几 | 回复 `1+1 = 2` |

### 配置验证流程（实际执行）

```bash
openclaw config validate    # 通过
openclaw gateway restart    # 重启网关
grep -i "feishu" /tmp/openclaw/openclaw-2026-07-12.log   # 看到 starting WebSocket connection
```

日志确认出现：
```
starting feishu[study] (mode: websocket)
starting feishu[assistant] (mode: websocket)
feishu[study]: starting WebSocket connection...
feishu[assistant]: starting WebSocket connection...
```

### 关键踩坑（务必记住）

1. **`bindings` 是顶层字段，不是 `session` 下的字段** —— 放 session 下会报 `session: Invalid input`
2. **默认 agent 用 `agents.list[].default: true` 标记，不存在 `defaultAgent` 字段**
3. **飞书开放平台必须添加 `im.message.receive_v1`（接收消息）事件** —— 不加则机器人收不到任何消息、全程不回复（这是最初 3 个机器人都不回复的根本原因）
4. **订阅方式选「使用长连接接收事件」** —— 无需公网回调 URL
5. **bindings 正确格式**：`{"agentId": "study", "match": {"channel": "feishu", "accountId": "study"}}`（注意是 `agentId` + `match.channel` + `match.accountId`，不是 `channel/account/agent`）
6. **日志文件**：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`（非 systemd journalctl，journalctl 无输出）
7. **重启命令**：`openclaw gateway restart` 或 `openclaw gateway run --force`
8. **Python 脚本安全改 JSON**：不要手写，避免格式错误；改前先 `cp openclaw.json openclaw.json.bak`

---

*配置指南 | 2026-07-12 | OpenClaw @ 腾讯云 Lighthouse | 方案 B：3个独立飞书机器人 | 状态：✅ 已验证*
