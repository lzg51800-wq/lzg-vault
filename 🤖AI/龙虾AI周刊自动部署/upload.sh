#!/usr/bin/env bash
# upload.sh — 把生成的 index.html 上传到腾讯云 COS 静态网站
set -euo pipefail

WORKDIR=/home/ubuntu/ai-weekly
cd "$WORKDIR"

# 读取 .env 里的 COS_BUCKET（含 appid 后缀，如 ai-weekly-1250000000）
if [ -f "$WORKDIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$WORKDIR/.env"
  set +a
fi

: "${COS_BUCKET:?请在 $WORKDIR/.env 中设置 COS_BUCKET=你的bucket名(含appid后缀)}"

coscli cp index.html "cos://${COS_BUCKET}/"
echo "✅ 已上传 index.html -> cos://${COS_BUCKET}/index.html"
