import os
from datetime import datetime
import json
import requests

# ==================== 🔧 核心配置区 ====================
# 1. 登录配置（完全从 GitHub Secrets 读取，不留任何默认值兜底）
LOGIN_URL = "https://laehfeigoiycigkfknfn.supabase.co/auth/v1/token?grant_type=password"
EMAIL = os.getenv("MY_EMAIL")
PASSWORD = os.getenv("MY_PASSWORD")

# 2. 网页前端固定死公钥（完全从 GitHub Secrets 读取）
SUPABASE_ANON_KEY = os.getenv("ANON_KEY")

# 3. 续期配置
RENEW_URL = "https://new.freemchost.com/_serverFn/c3a45c08362f2f613bbb6d511a3733a9e85e561709d48bec9280e82a4aa4f47d"
SERVER_ID = "c1487010-5680-43b7-932b-f6b6de2d893c"

# 4. 消息推送配置（可选，不需要保持 None）
SCKEY = None

# 🚨 安全校验：如果必备的环境变量为空，直接中断运行并报错提示
if not all([EMAIL, PASSWORD, SUPABASE_ANON_KEY]):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] 🛑 错误: 未能在环境中检测到必要的凭证 (MY_EMAIL, MY_PASSWORD 或 ANON_KEY)。")
    print(f"[{now}] 请检查你的本地环境变量或 GitHub Secrets 是否配置正确！")
    sys.exit(1) # 退出程序，并将 GitHub Action 标记为失败状态
# =====================================================


def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")

def notify(title, content):
    if SCKEY:
        try:
            requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data={"title": title, "desp": content}, timeout=5)
        except Exception as e:
            log(f"🔔 推送通知失败: {e}")

def parse_compressed_data(res_json):
    """
    自适应动态键值对对齐解析器
    精准定位复杂的压缩对齐映射格式，安全提取到期时间、服务器名称和状态
    """
    result = {"expires_at": None, "name": None, "status": None}
    try:
        # 1. 第一层：进入外层的 p -> v 列表
        outer_v = res_json.get("p", {}).get("v", [])
        if not outer_v:
            return result

        # 2. 第二层：寻找包含 server、panel_url 键名的层级
        mid_node = outer_v[0]
        mid_v = mid_node.get("p", {}).get("v", [])
        if not mid_v:
            return result

        # 3. 第三层：进入具体存放 server 属性的节点
        server_node = mid_v[0]
        keys = server_node.get("p", {}).get("k", [])
        values = server_node.get("p", {}).get("v", [])

        # 4. 动态通过 key 找对应的索引位置，防止后端微调位置
        target_keys = ["expires_at", "name", "status"]
        for key in target_keys:
            if key in keys:
                idx = keys.index(key)
                if idx < len(values):
                    # 获取该索引位置下包含数据值的 "s" 字段
                    result[key] = values[idx].get("s")
    except Exception as e:
        log(f"解析内核捕获到轻微异常: {e}")
    return result

def get_new_token():
    """第一步：通过模拟登录，动态换取最新的个人专属 Access Token"""
    log("🔑 正在尝试模拟登录以获取个人 Token...")

    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "apikey": SUPABASE_ANON_KEY,
        "authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "origin": "https://new.freemchost.com",
        "referer": "https://new.freemchost.com/",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    }

    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "gotrue_meta_security": {}
    }

    try:
        response = requests.post(
            LOGIN_URL,
            headers=headers,
            data=json.dumps(payload).encode('utf-8'),
            timeout=10
        )

        if response.status_code == 200:
            res_json = response.json()
            token = res_json.get("access_token")
            if token:
                log("✅ 成功模拟登录，已捕获最新专属 Token！")
                return token
        log(f"❌ 登录失败，状态码: {response.status_code}")
    except Exception as e:
        log(f"💥 登录请求引发异常: {e}")
    return None

def run_auto_renew():
    log("▶️ 开始全自动登录+续期流程...")

    # 1. 获取专属 Token
    token = get_new_token()
    if not token:
        log("🛑 未能取得有效 Token，流程被迫中断。")
        notify("服务器自动续期失败", "模拟登录未成功获取 Token，请查看本地日志。")
        return

    # 2. 组装续期请求头
    renew_headers = {
        "accept": "application/x-tss-framed, application/x-ndjson, application/json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "origin": "https://new.freemchost.com",
        "referer": f"https://new.freemchost.com/app/servers/{SERVER_ID}",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "x-tsr-serverfn": "true"
    }

    # 3. 构造续期 Payload
    renew_payload = {
        "t": {"t": 10, "i": 0, "p": {"k": ["data"], "v": [{"t": 10, "i": 1, "p": {"k": ["id"], "v": [{"t": 1, "s": SERVER_ID}]}, "o": 0}]}}, "f": 63, "m": []
    }

    # 4. 发送续期请求
    log("⚡ 正在向后端发送续期指令...")
    try:
        response = requests.post(RENEW_URL, headers=renew_headers, json=renew_payload, timeout=15)

        if response.status_code == 200:
            res_json = response.json()

            # --- 🌟 核心改进：调用自适应提取器，不再乱打印 JSON 🌟 ---
            info = parse_compressed_data(res_json)

            if info["expires_at"]:
                log("🎉【续期成功】------------------------------------")
                log(f" 服务器名称: {info['name'] or '未知'}")
                log(f" 当前状态  : {info['status'] or '未知'}")
                log(f" 到期时间  : {info['expires_at']}")
                log("--------------------------------------------------")
                notify("服务器自动续期成功", f"服务器 [{info['name']}] 续期成功，新到期时间：{info['expires_at']}")
            else:
                log("⚠️ 接口响应成功，但未能直接压缩提取出到期日期，可能返回了其他业务数据。")
        else:
            log(f"❌ 续期接口返回异常，状态码: {response.status_code}")
            notify("服务器自动续期失败", f"登录成功了，但续期接口返回状态码: {response.status_code}")

    except Exception as e:
        log(f"💥 续期请求发生异常: {e}")
        notify("服务器自动续期异常", f"异常详情: {e}")

if __name__ == "__main__":
    run_auto_renew()
