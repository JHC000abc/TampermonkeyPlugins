# 文件名: server.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import time

# 初始化 FastAPI 应用
app = FastAPI()

# ================================================================
# 1. 配置 CORS (跨域资源共享)
# 这是为了允许来自浏览器脚本的请求访问本地服务器
# 虽然 GM_xmlhttpRequest 可以绕过部分限制，但配置 CORS 是最稳健的做法
# ================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境请指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法 (POST, GET, OPTIONS 等)
    allow_headers=["*"],  # 允许所有请求头
)

# 确保数据保存目录存在
DATA_DIR = "xhs_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.get("/")
def read_root():
    return {"status": "running", "message": "小红书数据接收服务已启动"}

# ================================================================
# 2. 定义接收数据的接口
# ================================================================
@app.post("/receive_feed")
async def receive_feed(request: Request):
    """
    接收来自油猴脚本的 Feed 流数据
    """
    try:
        # 获取 JSON 数据
        data = await request.json()
        
        # 获取当前时间戳作为文件名，防止覆盖
        timestamp = int(time.time() * 1000)
        filename = f"{DATA_DIR}/feed_{timestamp}.json"
        
        # 将数据写入本地文件
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ [成功] 接收到数据，已保存至: {filename}")
        
        # 简单打印一下数据摘要（只打印前两项的 ID，方便在控制台确认）
        if "data" in data and "items" in data["data"]:
            count = len(data["data"]["items"])
            print(f"   📊 本次包含 {count} 条笔记")
        
        return {"status": "success", "file": filename}

    except Exception as e:
        print(f"❌ [错误] 处理数据失败: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # 启动服务器，监听 8000 端口
    # reload=True 表示修改代码后自动重启
    print("🚀 服务器启动中... 监听 http://127.0.0.1:8000")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
