# 龙虾自动生成「AI 周刊」并部署到公网

> 方案 B：腾讯云 CVM 上的 OpenClaw（龙虾）每天自动搜新闻 → 生成 index.html → 上传 COS 静态托管 → 固定公网 URL 每天自动更新。
> 飞书里的「liang的智能伙伴」做不到自动部署，所以由龙虾来做。

## 架构

```
龙虾 cron（每天 18:00 Asia/Shanghai，isolated session）
  ├─ agent 用 Tavily 搜本周 AI 新闻 → 整理 8 条 → 写 /home/ubuntu/ai-weekly/news.json
  ├─ python3 render_ai_weekly.py   → 生成 index.html（原样保留你的 CSS/JS，只换数据）
  └─ bash upload.sh                 → coscli 上传到 COS bucket（覆盖旧文件）
                │
                ▼
  COS 静态网站托管 → 固定公网 URL（每天自动更新，链接不变）
```

## 你（在腾讯云控制台）必须先做的 3 件事

> 控制台入口：https://console.cloud.tencent.com/ ，登录后右上角搜索框可直接搜「COS」「CAM」快速跳转。

### 第 1 件：建 COS 存储桶

1. 进入 **对象存储 COS** 控制台：https://console.cloud.tencent.com/cos
2. 左侧「存储桶列表」→ 点右上角 **「创建存储桶」**
3. 填表单：
   - **所属地域**：选离你近的，如 `广州`（对应 `ap-guangzhou`）
   - **名称**：填 `ai-weekly`（只能小写字母/数字/短横线，**不能含下划线和大写**）
     - 完整桶名系统会自动拼成 `ai-weekly-1250000000`（`1250000000` 是你的 APPID，页面会显示）
   - **访问权限**：选 **「公有读私有写」** ⚠️ 必须公有读，否则静态网站打不开
   - 其余默认，点 **「下一步」** → **「创建」**
4. 创建完成后，在「存储桶列表」点进这个桶，**记下桶名称** `ai-weekly-125xxxxxxxx`（后面配置 `.env` 要用）

### 第 2 件：开启静态网站托管

1. 进桶后，左侧菜单 **「基础配置」** → 找到 **「静态网站」** 一栏 → 点 **「编辑」**
2. **开启静态网站** 开关切到「开」
3. 索引文档（Index Document）：填 `index.html`
4. 错误文档（Error Document）：也填 `index.html`（单页应用友好）
5. 强制 HTTPS（可选）：先不勾，等绑域名+SSL 再开
6. 点 **「保存」**
7. 保存后页面会显示一个 **「访问节点」**，形如：
   ```
   https://ai-weekly-125xxxxxxxx.cos-website.ap-guangzhou.myqcloud.com
   ```
   这就是最终固定公网 URL，记下来。

### 第 3 件：拿 API 密钥（SecretId / SecretKey）

1. 进入 **访问管理 CAM** → **「API 密钥管理」**：https://console.cloud.tencent.com/cam/capi
2. 点 **「新建密钥」**（若已有密钥可直接用，点「显示」查看 SecretKey）
3. 会生成一对：
   - **SecretId**：形如 `AKIDxxxxxxxxxxxxxxxxxxxx`
   - **SecretKey**：形如 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`（只显示一次，立刻复制保存）
4. 这两个值后面要填进龙虾服务器的：
   ```bash
   coscli config set secretid <YOUR_SECRETID>
   coscli config set secretkey <YOUR_SECRETKEY>
   ```

> 安全提示：主账号密钥权限最大。当前先跑通用主账号密钥即可；若日后要更隔离，可在 CAM 建一个**只勾选 COS 只读/写权限的子账号**，用子账号密钥做上传。本方案 B 原版不强制子账号。

### 第 4 件（易漏）：确认 bucket 有公开访问权限

有些账号默认开了「禁止公有读」，需要额外确认：
1. 进桶 → **「权限管理」** → **「公有读私有写」** 是否生效
2. 若开了「存储桶防盗链」或「访问控制（ACL）」里有 `Deny` 公网读，需放行，否则外网打不开页面

## 在龙虾服务器上执行（ubuntu 账号）

> 你之前连龙虾用的是 `ubuntu@124.220.224.124`。本机这些文件需放到 `/home/ubuntu/ai-weekly/`。

### 方式 A：直接 scp（你本地有 ubuntu 的 key 时）
```bash
scp -r "/Users/Apple/Documents/file/LzgFile/🤖AI/龙虾AI周刊自动部署/" \
  ubuntu@124.220.224.124:/home/ubuntu/ai-weekly
```

### 方式 B：没有 key，手动建（在服务器上）
```bash
mkdir -p /home/ubuntu/ai-weekly
cd /home/ubuntu/ai-weekly
# 用 cat > 文件 << 'EOF' ... EOF 把下面 4 个文件内容贴进去
#   render_ai_weekly.py / upload.sh / setup_cos.sh / cron_prompt.txt
```

### Step 1：安装并配置 coscli
```bash
bash /home/ubuntu/ai-weekly/setup_cos.sh
# 按脚本提示执行：
coscli config set secretid <YOUR_SECRETID>
coscli config set secretkey <YOUR_SECRETKEY>
```

### Step 2：写 .env（bucket 名）
```bash
echo "COS_BUCKET=ai-weekly-1250000000" > /home/ubuntu/ai-weekly/.env
chmod 600 /home/ubuntu/ai-weekly/.env
```

### Step 3：手动测一次上传（先放个占位 index.html）
```bash
echo "<h1>ai-weekly placeholder</h1>" > /home/ubuntu/ai-weekly/index.html
bash /home/ubuntu/ai-weekly/upload.sh
# 看到 "已上传" 即 COS 链路通了
```

### Step 4：添加龙虾 cron 任务
```bash
cd /home/ubuntu/ai-weekly
openclaw cron add \
  --name "ai-weekly" \
  --cron "0 18 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --agent main \
  --message "$(cat cron_prompt.txt)"
```
验证：
```bash
openclaw cron list
```
应看到 `ai-weekly` 任务，下一次运行时间是今天/明天的 18:00。

### Step 5：立刻手动跑一次验证全链路
```bash
openclaw cron run ai-weekly
```
等几分钟，看 agent 是否生成了 index.html 并上传成功。然后浏览器打开你的静态网站 URL 确认。

## news.json 数据结构（agent 生成时遵循）

```json
[
  {
    "id": 1,
    "category": "模型",
    "title": "OpenAI GPT-5.6 三连发",
    "date": "2026-07-09",
    "summary": "2-3 句中文摘要",
    "source": "OpenAI 官方",
    "impact": "高",
    "tag": ["OpenAI", "GPT-5.6"]
  }
]
```
- `category` ∈ {模型, 政策, 资本, 产品, 终端}
- `impact`   ∈ {高, 中, 低}
- `tag` 是字符串数组
- `render_ai_weekly.py` 会自动补全 `id`、校验分类/影响力，并算好本周日期区间

## 上线前本地空跑自检（可选但推荐）

不想一上来就在龙虾上跑、怕出错？可以在自己 Mac（或任意 Linux）先把 `render` + `upload` 两条命令跑通，确认脚本逻辑无误、不依赖龙虾、也不需真实 COS 密钥。

原理：把脚本里的 `WORKDIR` 改成临时目录，造一份测试 `news.json`，用一个 `coscli` 桩程序模拟上传（只打印命令、不真实联网），即可全程验证。

```bash
set -e
DR=/tmp/aiweekly_dryrun
rm -rf "$DR"; mkdir -p "$DR/bin"
SRC="<本 README 所在目录>"   # 即 🤖AI/龙虾AI周刊自动部署/

# 1. 复制脚本并把 WORKDIR 重定向到测试目录
cp "$SRC/render_ai_weekly.py" "$DR/render.py"
cp "$SRC/upload.sh" "$DR/upload.sh"
sed -i '' "s#/home/ubuntu/ai-weekly#$DR#g" "$DR/render.py"   # macOS 用 sed -i ''
sed -i '' "s#/home/ubuntu/ai-weekly#$DR#g" "$DR/upload.sh"   # Linux 去掉 '' 参数：sed -i "s#...#...#g"

# 2. 造几条测试 news.json（字段同上一节）
cat > "$DR/news.json" <<'EOF'
[
  {"category":"模型","title":"测试模型发布","date":"2026-07-12","summary":"本地空跑测试摘要。","source":"测试源","impact":"高","tag":["测试"]},
  {"category":"政策","title":"测试政策出台","date":"2026-07-11","summary":"第二条测试摘要。","source":"测试源","impact":"中","tag":["政策"]}
]
EOF

echo "COS_BUCKET=ai-weekly-1250000000" > "$DR/.env"

# 3. coscli 桩：只打印将要执行的命令，不真实上传
cat > "$DR/bin/coscli" <<'EOF'
#!/bin/bash
echo "[coscli-shim] 将执行: coscli $*"
exit 0
EOF
chmod +x "$DR/bin/coscli"

# 4. 跑 render
/usr/bin/python3 "$DR/render.py"          # Mac；Linux 用 python3

# 5. 校验输出
grep -o "const data = \[" "$DR/index.html"     # 应出现
grep -o "测试模型发布" "$DR/index.html"         # 数据已注入
grep -c "__DATA_JSON__" "$DR/index.html"       # 应为 0（无残留占位符）

# 6. 跑 upload（用桩模拟）
PATH="$DR/bin:$PATH" bash "$DR/upload.sh"
# 应打印: [coscli-shim] 将执行: coscli cp index.html cos://ai-weekly-1250000000/
```

**校验点：**
- `index.html` 生成成功、大小约 10KB
- 测试标题出现在页面里、JS 里的 `${item.id}` 等占位符完好
- `grep -c "__DATA_JSON__"` 返回 **0**（没残留模板占位符）
- upload 打印的 `coscli cp index.html cos://<bucket>/` 命令正确

全部通过 = 脚本逻辑 OK，上龙虾只需替换真实 bucket 名 + 真实 `coscli` 即可。

> ⚠️ 注意：`grep -c` 在**匹配数为 0** 时返回退出码 1，若用 `set -e` 包裹会"误报失败"，属正常现象，不代表脚本出错（这恰恰是我们想要的"无残留"结果）。

## 静态网站 URL

开启托管后，COS 给的默认地址形如：
```
https://ai-weekly-1250000000.cos-website.ap-guangzhou.myqcloud.com
```
这就是每天自动更新的固定公网链接。

**可选进阶**：在 COS 桶「自定义源站域名」绑自己的域名 + 腾讯云免费 SSL 证书上 HTTPS。需要的话我再给步骤。

## 故障排查

| 现象 | 原因 | 处理 |
|------|------|------|
| `openclaw cron` 命令不存在 | 版本差异 | 用 `openclaw cron --help` 看子命令；或直接改 `~/.openclaw/openclaw.json` 的 `cron` 字段 |
| cron 跑了但没生成文件 | agent 无 shell 权限 | 确认 main agent 允许执行命令；或在 cron message 里强调「必须用 shell 工具运行 python3」 |
| `coscli: command not found` | 没装 | 重跑 `setup_cos.sh` |
| 上传报 403 | SecretId/Key 错或无 COS 权限 | 重新 `coscli config set` |
| 上传报 NoSuchBucket | bucket 名/appid 错 | 核对 `.env` 里的 `COS_BUCKET` |
| 页面打开是旧内容 | 浏览器缓存 | 强刷 Ctrl/Cmd+Shift+R；COS 默认不缓存，通常立即可见 |

## 文件清单

| 文件 | 作用 |
|------|------|
| `render_ai_weekly.py` | 读 news.json → 渲染 index.html（样式零改动） |
| `upload.sh` | 读 .env 的 COS_BUCKET → coscli 上传 |
| `setup_cos.sh` | 安装 coscli + 打印配置说明 |
| `cron_prompt.txt` | 交给龙虾 agent 的定时任务提示词 |
| `.env` | 仅存 `COS_BUCKET=xxx`（服务器上自建，不上传） |
| `news.json` | agent 每次运行生成，不要手建 |
| `README.md` | 本文件 |

*配置指南 | 2026-07-12 | OpenClaw @ 腾讯云 CVM + 腾讯云 COS 静态托管*
