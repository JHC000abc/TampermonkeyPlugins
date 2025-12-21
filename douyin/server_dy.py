import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 数据模型 ===

# 1. 单条评论模型
class CommentSchema(BaseModel):
    username: str
    content: str
    ts: int
    viewers: str = "0"


# 2. [新增] 主播信息模型
class StreamerSchema(BaseModel):
    name: str
    url: str


# 3. [新增] 整体请求包模型 (包含主播信息 + 评论列表)
class PayloadSchema(BaseModel):
    streamer: StreamerSchema
    data: List[CommentSchema]


@app.post("/api/receive_comments")
async def receive_comments(payload: PayloadSchema):
    """
    接收复合数据包：主播信息 + 评论列表
    """
    # 1. 如果没有数据，直接返回
    if not payload.data:
        return {"status": "empty"}

    prt_flag = False
    comments = []
    # 3. 打印评论详情
    for item in payload.data:
        if "为主播点赞" in item.content or "送出了" in item.content or "来了" == item.content:
            continue
        comments.append(f"[{item.username}:{item.ts}]: {item.content}")
        prt_flag = True

    if prt_flag:
        # 2. 打印主播信息 (每次请求打印一次即可)
        print(f"\n{'=' * 40}")
        print(f"📺 直播间: {payload.streamer.name}")
        print(f"🔗 主页: {payload.streamer.url}")
        print(f"👥 在线: {payload.data[0].viewers}")  # 取第一条数据的人数
        print(f"{'-' * 40}")
        for comment in comments:
            print(comment)

    return {
        "status": "success",
        "count": len(payload.data),
        "streamer": payload.streamer.name
    }


if __name__ == "__main__":
    # 监听所有IP，方便局域网访问
    uvicorn.run(app, host="0.0.0.0", port=8000,log_level="error")
