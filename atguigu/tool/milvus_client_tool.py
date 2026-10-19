from pymilvus import MilvusClient

from atguigu.import_process.config.config import MilvusConfig

milvus_client = None

def get_milvus_client():
    global milvus_client
    if not milvus_client:
        milvus_client = MilvusClient(
            uri=MilvusConfig.milvus_url,
            # 没有配置db_name，默认使用的是default数据库，如果实现创建好了数据库，需要配置db_name
        )
    return milvus_client