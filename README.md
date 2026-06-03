# 🚀 Freemchost 服务器全自动续期助手

[注册地址](https://freemchost.com)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-GitHub%20Actions-orange)

本脚本用于自动化管理 **Freemchost** 游戏/应用服务器（基于 Pterodactyl 翼龙面板）的续期流程。针对免费微型套餐（Free mini）**每 48 小时需手动续期一次**的限制，通过本脚本配合 GitHub Actions，实现每日定时全自动登录、派发续期指令、提取最新到期时间，并通过 Telegram 实时通知续期状态。

---

## ✨ 核心特性

* **全自动链式运行**：自动模拟登录获取个人专属 Token，并动态注入续期接口。
* **自适应数据解包**：独创自适应动态键值对对齐解析器，能自动从复杂的网络压缩映射流中精准提取出到期时间、服务器名称和运行状态，拒绝冗长日志。
* **零本地依赖托管**：完全基于 GitHub Actions 虚拟环境运行，无需本地服务器或常驻后台。
* **多维度 TG 状态推送**：无论续期成功或失败，Telegram 机器人都会准时将精简的服务器状态及直达工作流链接推送到你的手机。
* **安全凭证防护**：敏感数据（账户、密码、密钥）全线接入 GitHub Secrets 加密存储，拒绝源码泄露风险。

---

## 🔍 核心参数获取指引（抓包教程）

当网站升级或你更换了新的服务器时，脚本中的 `RENEW_URL` 和 `SERVER_ID` 需要同步更新。请按照以下步骤获取最新值：

### 步骤 1：开启浏览器开发者工具
1. 使用电脑浏览器（推荐 Chrome 或 Edge）打开并登录 [Freemchost 官网](https://new.freemchost.com)。
2. 进入你的服务器控制台管理页面（此时地址栏通常会显示为 `https://new.freemchost.com/app/servers/xxxxx`）。
3. 按下键盘上的 **F12** 键（或右键点击页面选择“检查”），切换到 **Network（网络）** 标签页。
4. 在过滤框中输入 `_serverFn` 锁定目标请求，并确保清空了旧的抓包记录。

### 步骤 2：触发续期动作并抓包
1. 在网页上点击 **"Renew"（续期）** 按钮。
2. 此时网络面板中会弹出一个全新的网络请求：
   * **获取 `RENEW_URL`**：点击这个请求，在右侧的 **Headers（标头）** -> **General（常规）** 中找到 **Request URL（请求 URL）**。将其完整复制出来，替换掉脚本中的 `RENEW_URL`。
   * **获取 `SERVER_ID`**：点击该请求右侧的 **Payload（负载）** 标签页（或 Preview/Response），寻找形如 `c1487010-5680-43b7...` 的 36 位长字符串（带连字符的 UUID）；或者最简单的方法，直接在**浏览器地址栏**的 URL 尾部（`/app/servers/` 后面那一串）复制该 ID。将其替换掉脚本中的 `SERVER_ID`。

---

## 🛠️ 快速部署指南

### 1. 准备 Telegram 通知凭证（可选）
1. 在 Telegram 中私聊 [@BotFather](https://t.me/BotFather) 发送 `/newbot`，按提示创建机器人并获取 `TG_BOT_TOKEN`。
2. 私聊 [@getmyid_bot](https://t.me/getmyid_bot) 发送任意消息，获取你个人的纯数字 `TG_USER_ID`。

### 2. 配置 GitHub Secrets
将本仓库 Fork 或推送到你的 GitHub 后，点击仓库顶部的 **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**，依次添加以下加密变量：

| Secret 名称 | 填入的值 / 示例 | 说明 |
| :--- | :--- | :--- |
| `MY_EMAIL` | `your_email@gmail.com` | 你的 Freemchost 登录邮箱 |
| `MY_PASSWORD` | `your_password` | 你的 Freemchost 登录密码 |
| `ANON_KEY` | `eyJhbGciOiJIUzI1NiIs...` | 前端固定的 Supabase 公钥 |
| `TG_BOT_TOKEN` | `123456789:ABCdef...` | （可选）Telegram 机器人 Token |
| `TG_USER_ID` | `987654321` | （可选）你的 Telegram 个人数字 ID |

### 3. 文件结构说明
请确保你的 GitHub 仓库中包含以下核心文件且路径正确：
```text
├── .github/
│   └── workflows/
│       └── auto_renew.yml      # GitHub Actions 工作流配置文件（内含定时与TG通知逻辑）
├── renew1.py                   # 完善后的核心 Python 续期与压缩流解析脚本（修改 RENEW_URL 与 SERVER_ID 处）
└── README.md                   # 本说明文件
