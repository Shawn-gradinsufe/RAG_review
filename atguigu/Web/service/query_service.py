import uuid

from fastapi import FastAPI, Path, BackgroundTasks, Body
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field

from atguigu.query_process.main_graph import QueryMainGraphRunner
from atguigu.tool.mongo_tool import get_recent_messages,clear_history

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]  # 允许跨域请求的头信息
)

# todo 测试接口连接成功还是不成功  健康检查
@app.get("/health")
def health():
    return {"hehe":"haha"}


# todo 获取历史记录列|表返回到前端显示
@app.get("/history/{session_id}")
def get_history(session_id:str = Path(..., description="session_id")):
    history_list = get_recent_messages(session_id)
    # 我们返回什么东西要和前端使用的时候对应，不能想当然返回history_list
    # 这里对应/history的那段代码

    # 在对数据做序列化的时候，ObjectID类型会报错，我们要转化
    history_list = [{**item,"_id":str(item.get("_id"))} for item in history_list]

    return {"items":history_list}


# todo 清空历史记录
@app.delete("/history/{session_id}")
def clear_history_messages(session_id:str = Path(..., description="会话id")):
    clear_history(session_id)
    return {"message":"ok"}



# todo 用户开始检索

class BodyParams(BaseModel):
    query:str = Field(...,description="检索的关键词")
    session_id:str = Field(...,description="会话id")

def run_main_graph(query:str, session_id:str,task_id):
    init_state = {
        "task_id": task_id,
        "session_id": session_id,
        "original_query": query,
    }
    QueryMainGraphRunner.create_and_run(init_state)

@app.post("/query")
def query(background_tasks:BackgroundTasks
        ,body_params:BodyParams = Body(...,description="检索的关键词和会话id")):
    query = body_params.query
    session_id = body_params.session_id
    # 需要自己创建task_id,给前端立即返回(从前端看)
    task_id = str(uuid.uuid4())

    # 添加后台任务执行graph去检索
    background_tasks.add_task(run_main_graph, query, session_id)

    return {"task_id":task_id}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) # 与导入服务端口号不一致