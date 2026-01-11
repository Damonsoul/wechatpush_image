import json
import os
import random
import time
from datetime import datetime

import requests

# ================= 配置区域 (每次运行前需更新) =================
# 1. 登录微信公众号后台 (mp.weixin.qq.com)
# 2. 这里的 TOKEN 是 URL 里的 token 参数 (例如: 1849283734)
TOKEN = "1457228299"

# 3. 这里的 COOKIE 是开发者工具(Network)里请求头的 Cookie
COOKIE = """appmsglist_action_3948611269=card; pgv_pvid=7684083648; ua_id=djwHyaoCnMhpXgmtAAAAABOix4NHYz231FPw-mXDzNo=; mm_lang=zh_CN; ts_uid=1057117920; pgv_pvi=297373696; rewardsn=; wxtokenkey=777; _clck=3948611269|1|g2j|0; wxuin=67878860640563; uuid=c586a1b581e778d25962f5f5e382b8f5; rand_info=CAESIGLHyIGgfZv5rPGaAy9BTZ0rMYjIRElntqShlGM6Ovdi; slave_bizuin=3948611269; data_bizuin=3948611269; bizuin=3948611269; data_ticket=mCW7emRfLqdMaN3/eRBNLSqfKI5R9i5WciZ7G1Q0waHUv+CRH/u5do8rEprgeoqM; slave_sid=ZUkyS01KTURZbEtpQkNzUXRMSUFHejJuaUdqaUFPaGl5UndaaWt2X182MV95aVlBX0IxVjVUTk1zOGJrMndHX25HVHFNZTVfeVVPOUpHXzRyenRDUDk5RWo1ZFNKbXU1NFhNUjkwX1hHa3MzUm9pN0JydDBvSkRicVdFV3RmcWdFRFZjM1U1MGJHaEIwaE4x; slave_user=gh_0573c6c51b06; xid=0667747e2cc4b0c9c695f11f2ab20697; _clsk=bqfgz3|1767881894218|5|1|mp.weixin.qq.com/weheat-agent/payload/record"""

# ===========================================================


def get_articles():
    """抓取文章并返回列表"""
    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Cookie": COOKIE,
    }

    data_list = []
    offset = 0
    count = 5  # 每次抓5篇，稳一点

    print(f"--- 开始抓取 (Token: {TOKEN}) ---")

    while True:
        params = {
            "action": "list_ex",  # 获取列表动作
            "begin": offset,  # 偏移量
            "count": count,  # 数量
            "fakeid": "",
            "type": "9",  # 9代表群发图文
            "query": "",
            "token": TOKEN,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            res_json = resp.json()

            # 检查返回状态
            if res_json.get("base_resp", {}).get("ret") != 0:
                print("\n[错误] 请求被拒绝！")
                print("可能原因：Cookie或Token过期、访问太频繁。")
                print(f"详细信息: {res_json}")
                break

            app_msg_list = res_json.get("app_msg_list")

            # 如果列表为空，说明抓完了
            if not app_msg_list:
                print("\n--- 所有文章抓取完毕 ---")
                break

            for item in app_msg_list:
                # 时间戳转换
                create_time = item.get("create_time")
                date_str = (
                    datetime.fromtimestamp(create_time).strftime("%Y-%m-%d")
                    if create_time
                    else ""
                )

                article = {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "cover": item.get("cover"),  # 封面图链接
                    "digest": item.get("digest"),  # 摘要
                    "date": date_str,  # 格式化后的日期
                    "timestamp": create_time,  # 原始时间戳(方便排序)
                }
                data_list.append(article)
                print(f"[{date_str}] {article['title']}")

            # 翻页
            offset += count

            # 随机休眠 (3-5秒)，这是本地手动爬取不封号的关键
            sleep_time = random.randint(3, 5)
            # print(f"等待 {sleep_time} 秒...")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"\n[异常] 发生错误: {e}")
            break

    return data_list


def save_to_local(data):
    """保存为 JSON 文件到当前目录"""
    if not data:
        print("没有数据，不保存。")
        return

    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "articles.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            # ensure_ascii=False 保证中文正常显示，indent=2 保证格式美观
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n成功保存 {len(data)} 篇文章！")
        print(f"文件路径: {file_path}")
    except Exception as e:
        print(f"保存文件失败: {e}")


if __name__ == "__main__":
    articles = get_articles()
    save_to_local(articles)
