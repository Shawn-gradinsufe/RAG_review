# 案例1
# 1.客户前端发ajax请求要发邮件并携带session_id,服务端直接回复收到,制造邮件开始
# 第一步就是发送一个普通http请求,后端需要写接口处理这个请求返回响应

# 2.服务端就开始执行backgroundtask当中造邮件的函数,造的邮件全部放在队列当中
# 队列必须按照session_id 每人创建一个,后期多个用户访问,各自是各自的队列

# 3.客户端想直接拿到造的邮件内容,造一个拿一个,那么客户端需要去发送订阅SSE请求
# 客户端在发送完第一个普通请求拿到响应后,打印到数据,立即发送订阅SSE的请求(建立长连接)

# 4.服务端需要写SSE回复接口,流式返回,流式返回就是把一个生成器对象返回
# 生成器函数当中就是从queue_dict当中获取自己session_id的队列,从队列当中一个一个yield邮件

import time
import uvicorn

from fastapi import FastAPI, Query, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from queue import Queue

from starlette.responses import StreamingResponse

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # *代表允许所有域名访问
    allow_credentials=True, # 允许跨域请求携带凭证cookie
    allow_methods=["*"], # 允许跨域请求使用的HTTP方法
    allow_headers=["*"], # 允许跨域请求携带的头信息
)


q_dict = {}

def make_email(session_id:str):
    # 创建队列
    if session_id not in q_dict:
        q_dict[session_id] = Queue()

    q = q_dict.get(session_id)

    q.put(f"邮件1{session_id}")
    q.put(f"邮件2{session_id}")
    q.put(f"邮件3{session_id}")
    q.put(f"邮件4{session_id}")
    q.put(f"邮件5{session_id}")
    q.put(None)



@app.get("/sse01")
def sse01(
        background_tasks: BackgroundTasks,
        session_id:str = Query(..., description="会话ID")
):
    background_tasks.add_task(make_email, session_id=session_id)
    return {"msg": "收到邮件请求,制造邮件开始", "session_id": session_id}


def generate_data(session_id:str):
    # 从队列当中获取邮件 一个一个yield数据,只是要符合sse的数据规范
    while q_dict.get(session_id) is None:
        time.sleep(1)


    q = q_dict.get(session_id)
    while True:
        data = q.get()
        time.sleep(1)
        yield f"data: {data}\n\n"
        # 这里yield必须符合sse的规范,数据必须是字符串"data: 数据\n\n";(\n\n代表一次推送结束)开头,中间必须有空格
        # 推送数据必须符合SSE规范
        if data is None:
            break

@app.get("/hanlesse01")
def handlesse01(
        session_id:str = Query(...,description="会话ID")
):
    return StreamingResponse(generate_data(session_id=session_id),media_type="text/event-stream")
    # 第一个参数是生成器对象,第二个参数是media_type


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
