import json
import uuid

from fastapi import FastAPI, Path, BackgroundTasks, Body
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from starlette.responses import StreamingResponse

from atguigu.query_process.main_graph import QueryMainGraphRunner
from atguigu.tool.mongo_tool import get_recent_messages,clear_history
from atguigu.tool.task_utils import TASK_STATUS_PROCESSING, update_task_status, TASK_STATUS_COMPLETED, \
    TASK_STATUS_FAILED, create_queue, put_data, get_task_info, get_data

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
    history_list.sort(key=lambda item:item["ts"])
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

    # 上一个模块使用轮询去做的实时数据推送前端的效果，我们只管修改task_utils当中的各个状态数据即可
    # 数据是靠轮询接口，前端请求我们接口就把状态数据返回

    # 这个模块我们要用的是SSE后端主动推送，我们需要把修改的数据村队列，还得写SSE接口生成器流式推送
    try:
        update_task_status(task_id,TASK_STATUS_PROCESSING)
        put_data(task_id,event="progress",data=get_task_info(task_id))
        QueryMainGraphRunner.create_and_run(init_state)

        # 检索完成后，更新状态为已完成
        update_task_status(task_id, TASK_STATUS_COMPLETED)
        put_data(task_id, event="progress", data=get_task_info(task_id))
    except:
        update_task_status(task_id, TASK_STATUS_FAILED)
        put_data(task_id, event="error", data=get_task_info(task_id))
        raise

@app.post("/query")
def query(background_tasks:BackgroundTasks
        ,body_params:BodyParams = Body(...,description="检索的关键词和会话id")):
    query = body_params.query
    session_id = body_params.session_id
    # 需要自己创建task_id,给前端立即返回(从前端看)
    task_id = str(uuid.uuid4())

    # 创建队列
    create_queue(task_id)

    # 添加后台任务执行graph去检索
    background_tasks.add_task(run_main_graph, query, session_id,task_id)

    return {"task_id":task_id}

def generate_data(task_id):
    data = get_data(task_id)
    while True:
        yield f"event: {data.get("event")}\n"
        yield f"data: {json.dumps(data.get("data"))}\n\n"

# SSE的订阅请求
@app.get("/stream/{task_id}")
def stream_task(task_id:str = Path(..., description="任务ID")):
    return StreamingResponse(generate_data(task_id),media_type="text/event-stream")



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) # 与导入服务端口号不一致