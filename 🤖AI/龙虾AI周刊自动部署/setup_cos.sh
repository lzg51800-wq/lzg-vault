#!/usr/bin/env bash
# setup_cos.sh — 在龙虾服务器(ubuntu)上安装 coscli 并给出配置说明
set -euo pipefail

echo "== 1. 安装 coscli (Linux x86_64) =="
if command -v coscli >/dev/null 2>&1; then
  echo "coscli 已存在: $(command -v coscli)"
else
  TMP=$(mktemp -d)
  curl -fsSL -o "$TMP/coscli" \
    https://cosbrowser.cloud.tencent.com/software/coscli/coscli-linux-amd64
  chmod +x "$TMP/coscli"
  install -m 0755 "$TMP/coscli" /usr/local/bin/coscli
  rm -rf "$TMP"
  echo "coscli 安装完成 -> /usr/local/bin/coscli"
fi
coscli --version

echo
echo "== 2. 配置 COS 凭证 =="
echo "在腾讯云控制台 CAM 拿到 SecretId / SecretKey 后执行："
echo "  coscli config set secretid <YOUR_SECRETID>"
echo "  coscli config set secretkey <YOUR_SECRETKEY>"
echo "（会写入 ~/.cos.yaml）"
echo

echo "== 3. 写入 bucket 名 =="
echo "  编辑 /home/ubuntu/ai-weekly/.env ，写入（注意 bucket 名含 appid 后缀）："
echo "  COS_BUCKET=ai-weekly-1438898998"
echo
echo "== 4. 测试上传 =="
echo "  bash /home/ubuntu/ai-weekly/upload.sh"
