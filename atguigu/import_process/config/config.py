import os
from dotenv import load_dotenv
load_dotenv(override=True)

class MineruConfig:
    mineru_token = os.getenv('MINERU_TOKEN')

class LLMConfig:
    openai_api_key=os.getenv('OPENAI_API_KEY')
    openai_api_base=os.getenv('OPENAI_API_BASE')
    llm_default_model=os.getenv('LLM_DEFAULT_MODEL')
    # 配置文件当中拿到的所有值，类型都是字符串，拿到代码当中需要墙砖
    llm_default_temperature=float(os.getenv('LLM_DEFAULT_TEMPERATURE'))
    vl_model=os.getenv('VL_MODEL')
    item_model=os.getenv('ITEM_MODEL')

class MinioConfig:
    minio_endpoint = os.getenv('MINIO_ENDPOINT')
    minio_access_key = os.getenv('MINIO_ACCESS_KEY')
    minio_secret_key =  os.getenv('MINIO_SECRET_KEY')
    minio_bucket_name = os.getenv('MINIO_BUCKET_NAME')
    minio_img_dir = os.getenv('MINIO_IMG_DIR')

class MilvusConfig:
    milvus_url = os.getenv('MILVUS_URL')
    # 知识库切片集合名
    chunks_collection = os.getenv('CHUNKS_COLLECTION')
    # 商品名称集合名
    item_name_collection = os.getenv('ITEM_NAME_COLLECTION')

class BGEM3Config:
    bge_m3_path = os.getenv('BGE_M3_PATH')
    # BGE-M3 模型名称
    bge_m3 = os.getenv('BGE_M3')
    # 嵌入模型运行设备，cuda:0表示使用第1块GPU，cpu表示使用CPU，cuda:N表示第N+1块GPU
    bge_device = os.getenv('BGE_DEVICE')
    # 是否使用半精度（True/False）1=开启（GPU加速更高效），0=关闭（兼容低版本GPU/CPU）
    # 注意：.env 里读出来是字符串，"False" 在 Python 中也是真值，必须显式转换
    bge_fp16 = os.getenv('BGE_FP16', 'False').strip().lower() in ('1', 'true', 'yes', 'on')

class MongoConfig:
    mongo_url = os.getenv('MONGO_URL')
    # 数据库名
    mongo_db_name = os.getenv('MONGO_DB_NAME')
    mongo_host = os.getenv('MONGO_HOST')
    mongo_port = int(os.getenv('MONGO_PORT'))