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
- Git 备份：vault 已 `git init` + GitHub remote（**2026-07-13 改 HTTPS**：`https://github.com/lzg51800-wq/lzg-vault.git`，因 Mac Clash Verge TUN 拦截 SSH 22 端口；Mac keychain 已缓存 token，Obsidian Git 自动备份恢复 ✅），Obsidian Git 每 30 分钟自动 commit+push
- MOC 用法：新笔记打对应层级标签即自动出现在 MOC 的 Dataview 区；重点笔记可手动加到「⭐精选」区

## 跨工具数据环路（Codex · Obsidian · 飞书 · 龙虾）
- 设计目标：把本地（Codex+Obsidian）与云端（龙虾 OpenClaw）通过 GitHub 仓库 `lzg-vault` 打通成闭环
- **知识总线 = GitHub `lzg-vault`**：Obsidian vault 是本地 md 文件已同步；龙虾在腾讯云 `git clone` 同一仓库即可读写同一份知识
- 环路流向：龙虾 cron 产出简报 → 写 md 进 vault + git push → Obsidian Git 自动 pull 进本地 → Codex 读 vault 深加工写回 → 龙虾定时 pull 读加工结果 → 飞书贯穿当遥控器（发指令/收推送）
- **分区避冲突**：龙虾只写专属子目录（如 `💰金融/自动/`），其余由用户/Codex 写；两端都 pull-before-push
- **Codex 外挂 Obsidian**：vault = 本地文件，Codex 直接文件系统读写即可（零配置）；结构化 MCP 需先开 Obsidian「Local REST API」插件
- **极空间 NAS 备份（2026-07-13 新增）**：用户有本地极空间，作为第 3 副本（不参与实时写入，零冲突）
  - 备份拓扑 = 3-2-1：副本1 Mac 本地（Obsidian 工作副本）/ 副本2 GitHub 云（异地+版本化）/ 副本3 极空间 NAS（本地独立磁盘）；2 介质 + 1 异地（GitHub）
  - 注意：极空间与 Mac 同处本地，非真正异地副本，主防 Mac 磁盘损坏/误删；真异地仍是 GitHub
  - **挂载方式（2026-07-13 21:2x 升级为 SMB 优先）**：原「自动挂载为磁盘」= 极空间客户端基于"临时缓存目录"(/Users/Apple/Downloads) 生成的 NFS 挂载点 ZSPACE，路径可能随缓存目录设置变化，**不可写死**（用户提醒）。改用 **SMB 固定挂载**：`极空间.local` 被客户端映射成 127.0.0.1，故**只能用 IP `192.168.1.251` 连 SMB**（445 端口已确认可达）；共享名按实际（疑似 `极空间-个人`），本地挂载点 `/Volumes/极空间-个人`。路径稳定、不依赖客户端缓存机制、适合大量文件
  - **自动同步（2026-07-13 21:2x 实测 OK）**：rsync 脚本 `~/.workbuddy/scripts/sync_jizone.sh` + launchd `~/Library/LaunchAgents/com.lzg.jizone-sync.plist`，每天 23:00（RunAtLoad 加载即跑）。**SMB 优先**：查 `/Volumes/极空间-个人` → 扫 /Volumes 极空间相关 → 尝试 `mount_smbfs`（靠钥匙串已存 192.168.1.251 凭证自动挂）→ fallback 极空间 NFS 动态检测。排除 `.git`/`.DS_Store`/`._*`，保留全部内容+隐藏配置。未挂载则跳过弹通知。日志 `~/.workbuddy/logs/jizone-sync.log`。⚠️ 首次需用户在 Finder 连一次 SMB 并"记住密码"到钥匙串，自动 mount 才无需手输
  - GitHub 只读 deploy key 镜像方案保留为进阶备选（未实施）
- **当前状态（2026-07-13 21:13）**：跨工具数据环路全面打通 + 3-2-1 备份完整。① 龙虾产出→GitHub→Obsidian 自动拉取 ✅；② Codex 加工写回 vault ✅；③ Obsidian Git 备份上云 ✅；④ 龙虾读回 Codex 观点 ✅（SOUL.md 已改 + 数据就位）；⑤ 极空间第 3 副本 ✅（已升级为每天 23:00 自动 rsync 同步）。后续可升级：GitHub 只读镜像版本化（可选）。
