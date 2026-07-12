---
tags: [MOC, AI]
created: 2026-07-12
---

# MOC · AI

> AI 知识领域入口。下方各区已接入 **Dataview** 自动汇总——新笔记只要打了对应层级标签（如 `#AI/自动化`），就会自动出现在这里，无需手动维护。
> 「⭐ 精选」区保留手动 `[[双链]]`，用于置顶重点笔记。

---

## 🏗️ 架构
```dataview
TABLE created AS 创建日期
FROM #AI/架构
SORT created DESC
```

## 🚀 部署
```dataview
TABLE created AS 创建日期
FROM #AI/部署
SORT created DESC
```

## ⚙️ 自动化 / 脚本
```dataview
TABLE created AS 创建日期
FROM #AI/自动化
SORT created DESC
```

## 💬 飞书 / 集成
```dataview
TABLE created AS 创建日期
FROM #AI/飞书
SORT created DESC
```

## 🧠 模型 / 技术
```dataview
TABLE created AS 创建日期
FROM #AI/模型
SORT created DESC
```

## 📝 工作记录
```dataview
TABLE created AS 创建日期
FROM #AI/工作记录
SORT created DESC
```

---

## ⭐ 精选（手动置顶）
- [[OpenClaw部署与配置指南]]
- [[龙虾多Agent架构部署]]
- [[飞书多Agent绑定配置(方案B)]]

---

## 📁 全部 AI 笔记（自动汇总）
```dataview
TABLE created AS 创建日期, tags AS 标签
FROM "🤖AI"
WHERE file.name != this.file.name
SORT created DESC
```
