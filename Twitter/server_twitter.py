import uvicorn
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import time
from typing import Dict, Any

app = FastAPI(title="Twitter Multi-Interface Hook")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础数据目录
BASE_DATA_DIR = "twitter_data"

# 允许监听的接口类型列表
ALLOWED_TYPES = ["UserTweets", "HomeTimeline", "HomeLatestTimeline"]

@app.post("/receive")
async def receive_data(payload: Dict[str, Any] = Body(...)):
    """
    接收数据并根据 source_type 分类存储
    """
    try:
        # 1. 获取来源类型
        source_type = payload.get("source_type", "Unknown")
        
        # 2. 过滤我们不关心的类型
        if source_type not in ALLOWED_TYPES:
            return {"status": "ignored", "reason": f"Type {source_type} not targeted"}

        # 3. 创建对应的子文件夹 (例如: twitter_data/HomeLatestTimeline)
        target_dir = os.path.join(BASE_DATA_DIR, source_type)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 4. 生成文件名
        timestamp = int(time.time() * 1000)
        filename = f"{target_dir}/{timestamp}.json"
        
        # 5. 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            
        print(f"✅ [{source_type}] 数据已保存: {filename}")

        # 6. 简单统计打印 (优化了解析逻辑)
        try:
            real_data = payload.get("data", {})
            instructions = []
            
            # 解析不同接口的数据结构
            if source_type == "UserTweets":
                # 用户主页
                if "user" in real_data.get("data", {}):
                    instructions = real_data['data']['user']['result']['timeline_v2']['timeline']['instructions']
            elif source_type in ["HomeTimeline", "HomeLatestTimeline"]:
                # 首页推荐 (HomeTimeline) 和 正在关注 (HomeLatestTimeline) 结构类似
                if "home" in real_data.get("data", {}):
                    instructions = real_data['data']['home']['home_timeline_urt']['instructions']
            
            # 统计推文数量
            count = 0
            for ins in instructions:
                if ins.get("type") == "TimelineAddEntries":
                    count = len(ins.get("entries", []))
                    break
            
            print(f"   -> 包含 {count} 条推文数据")
        except Exception:
            pass # 解析失败仅影响控制台打印，不影响保存

        return {"status": "success", "file": filename, "type": source_type}

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    print("🚀 服务已启动: http://127.0.0.1:5000")
    print(f"👀 监听目标: {', '.join(ALLOWED_TYPES)}")
    if not os.path.exists(BASE_DATA_DIR):
        os.makedirs(BASE_DATA_DIR)
    uvicorn.run(app, host="0.0.0.0", port=5000)

