---
tags:
  - AI/架构
created: 2026-07-12
---

# OpenClaw 多 Agent 架构部署指南

> 主 Agent 调度子 Agent 模式 | 部署日期：2026-07-12

---

## 架构总览

```
微信（1个账号）
    ↓ 所有消息
主 Agent「投研助理💰」
    ├── 金融类 → 自己处理
    ├── 「学习：」开头 → 派给子Agent「学习助手📚」
    └── 「问：」开头 → 派给子Agent「日常问答💬」
    ↓
微信回复用户
```

---

## 第 1 步：创建子 Agent 工作区（SSH 命令）

在服务器终端依次执行以下命令：

```bash
# 创建学习助手工作区
mkdir -p ~/.openclaw/workspace-study

cat > ~/.openclaw/workspace-study/SOUL.md << 'EOF'
# 学习助手

你是学习助手，专注于知识整理和笔记生成。

## 职责
- 搜集资料、整理结构化笔记
- 知识点梳理、概念解释
- 练习题生成与解答

## 风格
清晰有条理，注重理解而非死记。先给结论，再展开细节。
EOF


# 创建日常问答工作区
mkdir -p ~/.openclaw/workspace-assistant

cat > ~/.openclaw/workspace-assistant/SOUL.md << 'EOF'
# 日常问答助手

你是日常问答助手，快速回答用户的日常问题。

## 职责
- 查天气、翻译、算汇率、查航班
- 百科知识问答
- 日程提醒、单位换算

## 风格
简洁直接，先给答案再补充说明。不超过3句话能说清的不展开。
EOF
```

---

## 第 2 步：更新主 Agent 的 SOUL.md（追加调度规则）

```bash
cat >> ~/.openclaw/workspace/SOUL.md << 'EOF'

## 调度规则

你是主管家，收到用户消息后先判断类型：

1. 消息以「学习：」开头 → 派给学习助手处理，把用户完整需求转过去，结果回传后转述给用户
2. 消息以「问：」开头 → 派给日常问答助手处理，把用户完整需求转过去，结果回传后转述给用户
3. 其他消息 → 你自己处理（金融投资相关）

派发任务时，去掉前缀「学习：」或「问：」，把后面的实际内容转给子 agent。
子 agent 返回结果后，你直接转述给用户，不需要加额外解释。
EOF
```

---

## 第 3 步：覆盖 openclaw.json

**⚠️ 先备份再覆盖！**

```bash
# 备份
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# 覆盖（见下方完整配置）
```

将下方完整 JSON 内容写入 `~/.openclaw/openclaw.json`：

**用这条命令写入（推荐，避免粘贴问题）**：

```bash
cat > ~/.openclaw/openclaw.json << 'JSONEOF'
（见下方"完整配置文件"部分，整段粘贴到这里）
JSONEOF
```

---

## 第 4 步：重启生效

```bash
# 重启 OpenClaw
openclaw restart

# 如果上面命令不存在，直接重启服务器
sudo reboot
```

---

## 第 5 步：验证

重启后在微信分别测试：

| 测试 | 发送内容 | 期望 |
|:--|:--|:--|
| 学习助手 | `学习：帮我整理一下初中数学函数知识点` | 学习助手处理 |
| 日常问答 | `问：今天北京天气怎么样` | 日常问答处理 |
| 金融（主agent） | `中国银行今天走势如何` | 主agent自己处理 |

---

## 完整配置文件

> 以下是对原始 `openclaw.json` 的修改版。**仅改动了 2 处**：
> 1. `agents.list`：从 1 个 agent 扩展为 3 个
> 2. `tools`：显式添加 `agent` 调度配置
>
> 其他所有配置（gateway、channels、models、plugins 等）完全保持原样。

```json
{
  "agents": {
    "defaults": {
      "workspace": "/home/ubuntu/.openclaw/workspace",
      "sandbox": {
        "browser": {
          "enabled": false
        }
      },
      "models": {
        "minimax-portal/MiniMax-M2.7": {
          "alias": "minimax-m2.7"
        },
        "minimax-portal/MiniMax-M2.7-highspeed": {
          "alias": "minimax-m2.7-highspeed"
        }
      },
      "model": {
        "primary": "deepseek/deepseek-v4-flash"
      },
      "memorySearch": {
        "enabled": true,
        "provider": "local",
        "model": "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf"
      },
      "mediaMaxMb": 200
    },
    "list": [
      {
        "id": "main",
        "identity": {
          "name": "投研助理",
          "emoji": "💰",
          "avatar": "https://cloudcache.tencent-cloud.com/qcloud/ui/static/aisite_wxapp/0cd07d91-c3f4-48d2-b526-03f6813f3aa8.png"
        }
      },
      {
        "id": "study",
        "identity": {
          "name": "学习助手",
          "emoji": "📚"
        },
        "workspace": "/home/ubuntu/.openclaw/workspace-study"
      },
      {
        "id": "assistant",
        "identity": {
          "name": "日常问答",
          "emoji": "💬"
        },
        "workspace": "/home/ubuntu/.openclaw/workspace-assistant"
      }
    ]
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "64991b08fc6cc56ef5dbf67d61a3369a4ca892eceab3f64a"
    },
    "port": 29083,
    "bind": "lan",
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    },
    "controlUi": {
      "allowedOrigins": [
        "http://124.220.224.124:29083"
      ],
      "allowInsecureAuth": true,
      "dangerouslyDisableDeviceAuth": true,
      "basePath": "/gspgz0"
    }
  },
  "session": {
    "dmScope": "per-channel-peer"
  },
  "tools": {
    "profile": "full",
    "deny": [],
    "agent": {
      "enabled": true,
      "allowDispatch": true
    }
  },
  "skills": {
    "install": {
      "nodeManager": "npm"
    },
    "entries": {
      "1password": { "enabled": false },
      "apple-notes": { "enabled": false },
      "apple-reminders": { "enabled": false },
      "bear-notes": { "enabled": false },
      "blogwatcher": { "enabled": false },
      "blucli": { "enabled": false },
      "camsnap": { "enabled": false },
      "coding-agent": { "enabled": false },
      "discord": { "enabled": false },
      "eightctl": { "enabled": false },
      "gemini": { "enabled": false },
      "gh-issues": { "enabled": false },
      "gifgrep": { "enabled": false },
      "gog": { "enabled": false },
      "goplaces": { "enabled": false },
      "himalaya": { "enabled": false },
      "imsg": { "enabled": false },
      "mcporter": { "enabled": false },
      "model-usage": { "enabled": false },
      "nano-pdf": { "enabled": false },
      "obsidian": { "enabled": false },
      "openai-whisper": { "enabled": false },
      "openai-whisper-api": { "enabled": false },
      "openhue": { "enabled": false },
      "oracle": { "enabled": false },
      "ordercli": { "enabled": false },
      "peekaboo": { "enabled": false },
      "sag": { "enabled": false },
      "session-logs": { "enabled": false },
      "sherpa-onnx-tts": { "enabled": false },
      "slack": { "enabled": false },
      "songsee": { "enabled": false },
      "sonoscli": { "enabled": false },
      "spotify-player": { "enabled": false },
      "summarize": { "enabled": false },
      "tencent-cloud-cos": { "enabled": false },
      "tencent-meeting-mcp": { "enabled": false },
      "things-mac": { "enabled": false },
      "trello": { "enabled": false },
      "voice-call": { "enabled": false },
      "wacli": { "enabled": false },
      "xurl": { "enabled": false }
    }
  },
  "wizard": {
    "lastRunAt": "2026-06-07T12:13:04.556Z",
    "lastRunVersion": "2026.5.27",
    "lastRunCommand": "doctor",
    "lastRunMode": "local"
  },
  "meta": {
    "lastTouchedVersion": "2026.6.11",
    "lastTouchedAt": "2026-07-12T00:24:35.175Z"
  },
  "messages": {
    "groupChat": {
      "visibleReplies": "automatic"
    }
  },
  "plugins": {
    "entries": {
      "discord": { "enabled": false },
      "whatsapp": { "enabled": false },
      "slack": { "enabled": false },
      "tavily": {
        "enabled": true,
        "config": {
          "webSearch": {
            "apiKey": "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"
          }
        }
      },
      "minimax": { "enabled": true },
      "browser": { "enabled": true },
      "qqbot": { "enabled": false },
      "openclaw-lark": { "enabled": false },
      "wecom-openclaw-plugin": { "enabled": false },
      "dingtalk-connector": { "enabled": false },
      "openclaw-plugin-yuanbao": { "enabled": false },
      "openclaw-weixin": { "enabled": true },
      "lightclawbot": { "enabled": true },
      "memory-tencentdb": { "enabled": false }
    },
    "installs": {
      "lightclawbot": {
        "source": "npm",
        "spec": "lightclawbot",
        "installPath": "/home/ubuntu/.openclaw/npm/projects/lightclawbot/node_modules/lightclawbot",
        "version": "1.2.10",
        "installedAt": "2026-07-12T00:24:50.000Z"
      }
    }
  },
  "browser": {
    "enabled": true,
    "executablePath": "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome",
    "noSandbox": true,
    "defaultProfile": "user",
    "profiles": {
      "user": {
        "cdpUrl": "http://localhost:9222",
        "driver": "existing-session",
        "attachOnly": true,
        "color": "#4285F4",
        "userDataDir": "/home/ubuntu/.openclaw/browser-existing-session"
      }
    },
    "ssrfPolicy": {
      "dangerouslyAllowPrivateNetwork": true
    }
  },
  "models": {
    "providers": {
      "minimax-portal": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "MiniMax-M2.7",
            "name": "MiniMax M2.7",
            "contextWindow": 256000,
            "maxTokens": 32000
          },
          {
            "id": "MiniMax-M2.7-highspeed",
            "name": "MiniMax M2.7 Highspeed",
            "contextWindow": 256000,
            "maxTokens": 32000
          }
        ]
      },
      "deepseek": {
        "baseUrl": "https://api.deepseek.com/v1",
        "apiKey": "sk-c16d0ab52ffc4a9b9d97c556ebcdd424",
        "api": "openai-completions",
        "models": [
          {
            "id": "deepseek-v4-flash",
            "name": "DeepSeek V4 Flash"
          },
          {
            "id": "deepseek-v4-pro",
            "name": "DeepSeek V4 Pro"
          }
        ]
      }
    },
    "mode": "merge"
  },
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
    }
  },
  "commands": {
    "ownerAllowFrom": [
      "feishu:ou_68688a60d7dd6691c32ecc0e82a4b760"
    ]
  }
}
```

---

## 改动说明（只改了 2 处）

### 改动 1：agents.list（第 39-52 行附近）

**原配置**：只有 1 个 main agent

**修改后**：新增 2 个子 agent

```json
{
  "id": "study",
  "identity": { "name": "学习助手", "emoji": "📚" },
  "workspace": "/home/ubuntu/.openclaw/workspace-study"
},
{
  "id": "assistant",
  "identity": { "name": "日常问答", "emoji": "💬" },
  "workspace": "/home/ubuntu/.openclaw/workspace-assistant"
}
```

### 改动 2：tools（第 68 行附近）

**原配置**：
```json
"tools": {
  "profile": "full",
  "deny": []
}
```

**修改后**：
```json
"tools": {
  "profile": "full",
  "deny": [],
  "agent": {
    "enabled": true,
    "allowDispatch": true
  }
}
```

---

## 回滚方法

如果出问题，一键回滚：

```bash
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
openclaw restart
```

---

*部署指南 | 2026-07-12 | OpenClaw @ 腾讯云 Lighthouse*
