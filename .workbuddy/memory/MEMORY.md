# 项目长期记忆

## 金融信息系统架构

### WorkBuddy 定时任务（本地 Mac）
- 每日重大新闻简报（06:30 DAILY）— WebSearch 搜全网 → 多源核实 → 写 Obsidian 💰金融/

### OpenClaw 龙虾定时任务（腾讯云 Lighthouse 7×24）
- 每日金融新闻简报（06:30 每天）— westock-data + Tavily + Infoway → 微信推送
- 每日A股早间简报（08:00 工作日）— 同上 + 推荐查询组合（SPY.US, QQQ.US 等）→ 微信推送
- 收盘复盘（17:30 工作日）— 同上 + 关注个股+主要指数K线 → 微信推送

### 龙虾数据源
- westock-data：A股核心数据、板块资金流向
- Tavily web_search：新闻资讯搜索
- Infoway REST API：全球行情实时数据、K线数据（API Key 已配置在 ~/.openclaw/.env）

### 龙虾多 Agent 架构
- main agent「投研助理💰」— 调度中枢 + 金融类消息 + 3 个 cron 任务
- study agent「学习助手📚」— 「学习：」前缀消息，workspace: ~/.openclaw/workspace-study
- assistant agent「日常问答💬」— 「问：」前缀消息，workspace: ~/.openclaw/workspace-assistant
- 路由规则在主 agent SOUL.md 中配置（关键词前缀分发）

### 关键经验
- 龙虾没有 eastmoney-finance-news / infoway-financial-data 技能，实际用 westock-data + Tavily + Infoway REST API
- 龙虾文件落在服务器 ~/.openclaw/workspace/reports/，通过微信推送，不直接写 Obsidian
- WorkBuddy 优势在全网搜索 + 直接写 Obsidian 存档；龙虾优势在 7×24 运行 + 金融数据专业 + 微信直达
- **OpenClaw 配置教训**：不能手写 `tools.agent`，schema 不允许；正确做法是让龙虾自己在微信对话中添加 agent
- **OpenClaw 启动命令**：`openclaw gateway run --force`（不是 `openclaw start`）
- **OpenClaw 验证命令**：`openclaw config validate`
- **OpenClaw 回滚**：`cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json`
- **SSH 连接**：`ssh lobster`（已配 ~/.ssh/config 别名：ed25519 密钥 `~/.ssh/lobster_key` 免密登录 ubuntu@124.220.224.124）

## Obsidian Vault
- 路径：`/Users/Apple/Documents/file/LzgFile`
- 金融笔记文件夹：`💰金融/`
- AI 配置文件夹：`🤖AI/`
- 龙虾配置文件：`🤖AI/龙虾定时任务配置.md`
- 知识库结构：`Templates/`（每日/概念/文献 3 套 Templater 模板）、`Inbox/`（碎片箱）、各主题区有 `MOC-xx.md`（已接 Dataview 动态汇总）
- **层级标签体系**（新笔记必须沿用，MOC 靠它自动汇总）：
  - 金融：`金融/{A股|新闻简报|重大事件|个股|宏观|策略}`
  - AI：`AI/{架构|部署|自动化|飞书|模型|工作记录}`
- Git 备份：vault 已 `git init` + GitHub remote `git@github.com:lzg51800-wq/lzg-vault.git`，Obsidian Git 每 30 分钟自动 commit+push
- MOC 用法：新笔记打对应层级标签即自动出现在 MOC 的 Dataview 区；重点笔记可手动加到「⭐精选」区
