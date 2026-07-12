---
tags: [home]
created: 2026-07-12
---

# 🏠 我的知识库

> 个人知识中枢 · 由 Obsidian Git 每 30 分钟自动备份至 GitHub
> 提示：Dataview 区块请在「阅读模式」（Cmd + E）下查看渲染结果

---

## 🧭 领域入口

- 💰 [[MOC-金融]] — 行情、简报、个股、宏观策略
- 🤖 [[MOC-AI]] — 部署、架构、自动化、飞书集成、工作记录

## 📥 收集箱 & 工具

- 📥 **Inbox/** — 临时碎片、待处理灵感（建议每日清空归位）
- 📐 **Templates/** — 每日 / 概念 / 文献 三套模板（核心插件 Templates 调用）

---

## 🆕 最近新增（全库）

```dataview
TABLE created AS 创建日期, tags AS 标签
WHERE file.name != this.file.name
SORT created DESC
LIMIT 10
```

## 🔥 最近修改（全库）

```dataview
TABLE file.mtime AS 修改时间
WHERE file.name != this.file.name
SORT file.mtime DESC
LIMIT 10
```

---

## 🏷️ 标签地图

- #金融/新闻简报 · #金融/A股 · #金融/重大事件 · #金融/个股 · #金融/宏观 · #金融/策略
- #AI/架构 · #AI/部署 · #AI/自动化 · #AI/飞书 · #AI/模型 · #AI/工作记录

---

## 💡 使用提示

1. 新笔记先打 **层级标签**（如 `#金融/A股`），对应 MOC 会自动收录。
2. 碎片先丢进 **Inbox/**，定期回看、归类、打标签。
3. 每日笔记用 Templates 里的「每日笔记模板」。
4. 所有改动由 Obsidian Git 自动备份到 GitHub，无需手动操作。
