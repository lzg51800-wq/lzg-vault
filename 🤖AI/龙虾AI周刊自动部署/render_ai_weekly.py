#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_ai_weekly.py — 把 news.json 渲染为 index.html
配合 OpenClaw 龙虾的每日 cron 任务使用。

设计原则：
- 只替换 `data` 数组 + 标题/日期，CSS / JS 渲染逻辑完全保留原模板（样式零改动）
- 用占位符 __XXX__ + .replace()，避免 f-string / .format() 与 JS 模板里的 ${...} 冲突
- 读取 /home/ubuntu/ai-weekly/news.json，输出同目录 index.html

用法：
    cd /home/ubuntu/ai-weekly && python3 render_ai_weekly.py
"""

import json
import sys
from datetime import datetime, timedelta

WORKDIR = "/home/ubuntu/ai-weekly"
NEWS_JSON = f"{WORKDIR}/news.json"
OUT_HTML = f"{WORKDIR}/index.html"

CATEGORIES = {"模型", "政策", "资本", "产品", "终端"}
IMPACTS = {"高", "中", "低"}

# 完整 HTML 模板（CSS/JS 与原 index.html 完全一致，仅留占位符）
TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>本周 AI 热点速览 · __TITLE_DATE__</title>
<meta name="description" content="__DESC_RANGE__ 本周 AI / 科技行业重要新闻精选：模型发布、政策动态、资本信号、产品突破、终端硬件。" />
<meta name="generator" content="aily-pusher v0.2 (openclaw cron)" />
<style>
  :root {
    --bg: #f6f7f9;
    --surface: #ffffff;
    --border: #e5e7eb;
    --text: #111827;
    --text-muted: #6b7280;
    --accent: #2563eb;
    --accent-soft: #eff6ff;
    --radius: 12px;
    --shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 4px 12px rgba(15, 23, 42, 0.04);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }
  .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 40px 24px 80px;
  }
  header.hero {
    text-align: left;
    margin-bottom: 28px;
  }
  header.hero .eyebrow {
    display: inline-block;
    font-size: 12px;
    letter-spacing: 0.08em;
    color: var(--accent);
    background: var(--accent-soft);
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 14px;
  }
  header.hero h1 {
    font-size: 36px;
    line-height: 1.2;
    margin: 0 0 10px;
    font-weight: 700;
    letter-spacing: -0.01em;
  }
  header.hero p {
    color: var(--text-muted);
    font-size: 15px;
    margin: 0;
  }
  .filter-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: center;
    margin-bottom: 24px;
    box-shadow: var(--shadow);
  }
  .filter-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .filter-label {
    font-size: 13px;
    color: var(--text-muted);
    margin-right: 4px;
  }
  .chip {
    border: 1px solid var(--border);
    background: #fff;
    color: var(--text);
    font-size: 13px;
    padding: 5px 12px;
    border-radius: 999px;
    cursor: pointer;
    transition: all 0.15s ease;
  }
  .chip:hover { border-color: var(--accent); color: var(--accent); }
  .chip.active {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 18px;
  }
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 20px 18px;
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    gap: 10px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(15,23,42,0.05), 0 12px 24px rgba(15,23,42,0.06);
  }
  .card-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
  }
  .card-num {
    font-size: 12px;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
  }
  .impact {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    letter-spacing: 0.04em;
  }
  .impact-高 { background: #fef2f2; color: #b91c1c; }
  .impact-中 { background: #fffbeb; color: #b45309; }
  .impact-低 { background: #f0fdf4; color: #15803d; }
  .category {
    display: inline-block;
    font-size: 12px;
    padding: 2px 10px;
    border-radius: 4px;
    font-weight: 500;
  }
  .cat-模型 { background: #eef2ff; color: #4338ca; }
  .cat-政策 { background: #ecfdf5; color: #047857; }
  .cat-资本 { background: #fef3c7; color: #92400e; }
  .cat-产品 { background: #fce7f3; color: #9d174d; }
  .cat-终端 { background: #e0f2fe; color: #0369a1; }
  .card h2 {
    font-size: 17px;
    margin: 2px 0 4px;
    line-height: 1.45;
    font-weight: 600;
  }
  .card-date {
    font-size: 12px;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
  }
  .card p {
    margin: 0;
    font-size: 14px;
    color: #374151;
  }
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 4px;
  }
  .tag {
    font-size: 12px;
    color: var(--text-muted);
    background: #f3f4f6;
    padding: 2px 8px;
    border-radius: 4px;
  }
  .empty {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 0;
    color: var(--text-muted);
    font-size: 14px;
  }
  footer {
    margin-top: 50px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 12px;
    line-height: 1.8;
  }
  footer a { color: var(--text-muted); }
  @media (max-width: 640px) {
    header.hero h1 { font-size: 26px; }
    .container { padding: 28px 16px 60px; }
    .grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="container">

  <header class="hero">
    <span class="eyebrow">AI / TECH WEEKLY</span>
    <h1>本周 AI 热点速览</h1>
    <p>__HEADER_RANGE__ · 共 __COUNT__ 条 · 截止 __CUTOFF__</p>
  </header>

  <section class="filter-bar" aria-label="筛选">
    <div class="filter-group">
      <span class="filter-label">分类</span>
      <button class="chip active" data-filter="category" data-value="all">全部</button>
      <button class="chip" data-filter="category" data-value="模型">模型</button>
      <button class="chip" data-filter="category" data-value="政策">政策</button>
      <button class="chip" data-filter="category" data-value="资本">资本</button>
      <button class="chip" data-filter="category" data-value="产品">产品</button>
      <button class="chip" data-filter="category" data-value="终端">终端</button>
    </div>
    <div class="filter-group">
      <span class="filter-label">影响力</span>
      <button class="chip active" data-filter="impact" data-value="all">全部</button>
      <button class="chip" data-filter="impact" data-value="高">高</button>
      <button class="chip" data-filter="impact" data-value="中">中</button>
      <button class="chip" data-filter="impact" data-value="低">低</button>
    </div>
  </section>

  <main id="grid" class="grid" aria-live="polite"></main>

  <footer>
    <p>数据来源：OpenAI 官方、马斯克社交平台、人社部官网、券商中国、CSDN、科技媒体等公开渠道。<br>
    排序逻辑：影响力 × 时效性。模型 &gt; 政策 &gt; 资本 &gt; 终端。<br>
    本页由 aily 自动整理生成 · 仅作信息聚合，不构成投资建议。</p>
  </footer>

</div>

<script>
  const data = __DATA_JSON__;

  const grid = document.getElementById("grid");
  const state = { category: "all", impact: "all" };

  function render() {
    const filtered = data.filter(item => {
      const catOk = state.category === "all" || item.category === state.category;
      const impOk = state.impact === "all" || item.impact === state.impact;
      return catOk && impOk;
    });
    if (filtered.length === 0) {
      grid.innerHTML = '<div class="empty">没有匹配的结果</div>';
      return;
    }
    grid.innerHTML = filtered.map(item => `
      <article class="card" data-id="${item.id}">
        <div class="card-head">
          <span class="card-num">No.${String(item.id).padStart(3, '0')}</span>
          <span class="impact impact-${item.impact}">影响 ${item.impact}</span>
        </div>
        <span class="category cat-${item.category}">${item.category}</span>
        <h2>${item.title}</h2>
        <div class="card-date">📅 ${item.date}</div>
        <p>${item.summary}</p>
        <div class="tags">
          ${item.tag.map(t => `<span class="tag">#${t}</span>`).join('')}
        </div>
      </article>
    `).join('');
  }

  document.querySelectorAll('.chip').forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      const value = btn.dataset.value;
      document.querySelectorAll(`.chip[data-filter="${filter}"]`).forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      state[filter] = value;
      render();
    });
  });

  render();
</script>
</body>
</html>
"""


def load_news():
    with open(NEWS_JSON, "r", encoding="utf-8") as f:
        items = json.load(f)
    if not isinstance(items, list):
        raise ValueError("news.json 顶层必须是 JSON 数组")
    return items


def validate(items):
    cleaned = []
    for idx, it in enumerate(items, start=1):
        if not isinstance(it, dict):
            print(f"[WARN] 第 {idx} 条不是对象，已跳过")
            continue
        cat = it.get("category", "")
        if cat not in CATEGORIES:
            print(f"[WARN] 第 {idx} 条 category='{cat}' 不在 {CATEGORIES}，已设为'其他'之外的默认值，请检查")
        imp = it.get("impact", "")
        if imp not in IMPACTS:
            print(f"[WARN] 第 {idx} 条 impact='{imp}' 不在 {IMPACTS}，已设为'中'")
            imp = "中"
        tags = it.get("tag", [])
        if not isinstance(tags, list):
            tags = [str(tags)]
        cleaned.append({
            "id": idx,
            "category": cat if cat in CATEGORIES else "模型",
            "title": str(it.get("title", "无标题")),
            "date": str(it.get("date", "")),
            "summary": str(it.get("summary", "")),
            "source": str(it.get("source", "")),
            "impact": imp,
            "tag": [str(t) for t in tags],
        })
    if not cleaned:
        raise ValueError("没有有效的新闻条目，请检查 news.json")
    return cleaned


def main():
    items = load_news()
    items = validate(items)

    today = datetime.now()
    week_start = today - timedelta(days=6)
    title_date = today.strftime("%Y-%m-%d")
    rng = f"{week_start.strftime('%Y-%m-%d')} 至 {title_date}"
    cutoff = today.strftime("%Y-%m-%d %H:%M")

    data_json = json.dumps(items, ensure_ascii=False, indent=2)

    html = (TEMPLATE
            .replace("__TITLE_DATE__", title_date)
            .replace("__DESC_RANGE__", rng)
            .replace("__HEADER_RANGE__", rng)
            .replace("__COUNT__", str(len(items)))
            .replace("__CUTOFF__", cutoff)
            .replace("__DATA_JSON__", data_json))

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"index.html generated: {len(items)} 条, 区间 {rng}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
