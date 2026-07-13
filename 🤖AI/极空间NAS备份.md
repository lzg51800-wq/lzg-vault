---
tags: [AI/部署, AI/工作记录]
created: 2026-07-13
---

# 极空间 NAS 备份接入（第 3 备份副本）

> 作用：把 GitHub 仓库 `lzg-vault` 镜像到本地极空间 NAS，作为**第 3 份备份**。
> 备份拓扑 = 标准 3-2-1：① Mac 本地（工作副本）· ② GitHub 云（异地+版本化）· ③ 极空间 NAS（本地独立磁盘+版本化）。

## 设计原则

- **只读镜像**：极空间只 `git pull`，绝不直接写 vault，因此和 Mac / 龙虾**零冲突**。
- **独立 deploy key**：用一把**只读**密钥（不用 Mac 的 `github_key`、也不用龙虾的读写 key），服务器出问题时可单独吊销。
- **版本化**：走 git，不是文件夹拷贝，可回滚到任意历史版本。

## 已准备（服务器端）

- 腾讯云龙虾服务器已生成只读 deploy key：`lzgvault-readonly-jizone`
- 公钥（需你加到 GitHub）：
  ```
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE63Wvlo2mXRxQyzPO6MZpbmz12E+NBGcuV8IQtj/ZNU lzgvault-readonly-jizone
  ```

## 第 1 步：GitHub 加只读公钥（你做，1 分钟）

1. 打开 👉 `https://github.com/lzg51800-wq/lzg-vault/settings/keys`
2. 点 **Add deploy key**
3. Title 填：`jizone-nas`
4. Key 框粘贴上面那把公钥
5. ⚠️ **不要勾选** `Allow write access`（只读镜像，防误写）
6. 点 **Add key**

## 第 2 步：极空间侧拉取（二选一）

### 方式 A：极空间能跑命令（Docker / SSH 终端，推荐）
在极空间可执行的 shell（Docker 容器或设备 SSH）里：

```bash
# 装 git（容器内 Debian/Ubuntu 系）
apt-get update && apt-get install -y git openssh-client

# 把只读私钥放进来（内容从龙虾服务器 ~/.ssh/id_ed25519_lzgvault_ro 拷过来）
mkdir -p ~/.ssh && chmod 700 ~/.ssh
# 用 scp 从龙虾服务器拷： scp lobster:/home/ubuntu/.ssh/id_ed25519_lzgvault_ro ~/.ssh/
chmod 600 ~/.ssh/id_ed25519_lzgvault_ro

# 首次 clone（放在 NAS 存储卷路径下，如 /volume1/backup/lzg-vault）
git -c core.sshCommand="ssh -i ~/.ssh/id_ed25519_lzgvault_ro" \
  clone git@github.com:lzg51800-wq/lzg-vault.git /volume1/backup/lzg-vault

# 定时镜像：每天 03:30 拉一次（crontab -e 加入）
# 30 3 * * * cd /volume1/backup/lzg-vault && git -c core.sshCommand="ssh -i ~/.ssh/id_ed25519_lzgvault_ro" pull --ff-only origin main >> /volume1/backup/sync.log 2>&1
```

### 方式 B：极空间桌面客户端同步（零命令，非版本化）
若设备不支持跑命令，用极空间 App 的「同步 / 备份」功能，把 **Mac 上 `LzgFile` vault 文件夹**加为备份源 → 实时镜像到 NAS。
- 优点：不用命令
- 缺点：依赖 Mac 开机 + 客户端运行；不是 git 版本化（删错会跟着删）

> 真双保险：A + B 都上。A 是带历史的真备份，B 是实时镜像兜底。

## 验证

- 方式 A：隔天看 `/volume1/backup/sync.log` 有 `Already up to date` 或新提交 = 成功
- 方式 B：极空间 App 里能看到 vault 文件 = 成功

## 状态

- [x] 只读 deploy key 已生成（龙虾服务器）
- [ ] GitHub 加 `jizone-nas` 公钥（待你操作）
- [ ] 极空间侧首次 clone（待你按设备型号执行）
- [ ] 定时镜像 crontab 就位（待执行）
