---
tags: [MOC, 金融]
created: 2026-07-12
---

# MOC · 金融

> 金融知识领域入口。下方各区已接入 **Dataview** 自动汇总——新笔记只要打了对应层级标签（如 `#金融/A股`），就会自动出现在这里，无需手动维护。
> 「⭐ 精选」区保留手动 `[[双链]]`，用于置顶重点笔记。

---

## 📊 A股 / 早间简报
```dataview
TABLE created AS 创建日期
FROM #金融/A股
SORT created DESC
```

## 📰 新闻简报
```dataview
TABLE created AS 创建日期
FROM #金融/新闻简报
SORT created DESC
```

## 🚨 重大事件
```dataview
TABLE created AS 创建日期
FROM #金融/重大事件
SORT created DESC
```

## 📈 个股分析
```dataview
TABLE created AS 创建日期
FROM #金融/个股
SORT created DESC
```

## 🌐 宏观 / 策略
```dataview
TABLE created AS 创建日期
FROM #金融/宏观 OR #金融/策略
SORT created DESC
```

---

## ⭐ 精选（手动置顶）
- [[A股早间简报-2026-07-11]]
- [[金融新闻简报-2026-07-11]]
- [[2026-07-10-重大新闻事件简报]]

---

## 📁 全部金融笔记（自动汇总）
```dataview
TABLE created AS 创建日期, tags AS 标签
FROM "💰金融"
WHERE file.name != this.file.name
SORT created DESC
```
