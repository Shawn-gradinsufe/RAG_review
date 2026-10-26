import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import Path as Fpath
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi import BackgroundTasks
from starlette.middleware.cors import CORSMiddleware

from atguigu.import_process.config.config import MinioConfig
from atguigu.import_process.main_graph import MainGraphRunner
from atguigu.tool.logger import logger
from atguigu.tool.minio_client_tool import get_minio_client
from atguigu.tool.task_utils import get_task_info, update_task_status, TASK_STATUS_PROCESSING, TASK_STATUS_COMPLETED, \
    TASK_STATUS_FAILED, add_running_task, add_done_task, add_node_duration

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def run_main_graph(task_id:str,local_dir:str,local_file_path:str):
    init_state = {
        "local_file_path": local_file_path,
        "local_dir": local_dir,
        "task_id": task_id,
    }

    try:
        #修改全局状态的位置在这里
        update_task_status(task_id,TASK_STATUS_PROCESSING)
        MainGraphRunner.create_and_run(init_state)
        update_task_status(task_id, TASK_STATUS_COMPLETED)
    except Exception as e:
        update_task_status(task_id, TASK_STATUS_FAILED)
        raise e


@app.post("/upload")
def upload(background_tasks: BackgroundTasks,file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())

    add_running_task(task_id, "upload_file")
    start_time = time.time()
    #暂存
    local_dir = fr"D:\output\{datetime.now().strftime('%Y%m%d')}"
    local_dir_obj = Path(local_dir)
    if not local_dir_obj.exists():
        local_dir_obj.mkdir(parents=True, exist_ok=True)

    local_file_path_obj = local_dir_obj / file.filename
    # print(local_file_path_obj)
    with open(local_file_path_obj, "wb") as f:
        shutil.copyfileobj(file.file,f,1024*1024)


    #转储
    minio_client = get_minio_client()
    minio_client.fput_object(
        bucket_name=MinioConfig.minio_bucket_name,
        object_name=f"upload_file/{datetime.now().strftime('%Y%m%d')}/{file.filename}",
        file_path=str(local_file_path_obj)
    )

    add_done_task(task_id, "upload_file")
    end_time = time.time()
    add_node_duration(task_id,"upload_file",end_time - start_time)

    #添加后台任务跑graph
    background_tasks.add_task(run_main_graph,task_id,local_dir,str(local_file_path_obj))

    return {"task_id": task_id }




@app.get("/status/{task_id}")
def get_task_status(task_id: str = Fpath(...,description="任务id")):
    return get_task_info(task_id)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)


