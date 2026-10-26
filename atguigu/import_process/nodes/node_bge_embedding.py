import json

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.json_format import json_format
from atguigu.tool.get_bge_embeddings import get_bge_embedding
from atguigu.tool.logger import logger
class NodeBGEEmbedding(NodeBase):
    """
    混合向量化节点：使用 BGE-M3 模型将文本转换为向量
    """

    name = "node_bge_embedding"

    def process(self, state: ImportGraphState):
        # 从state中获取chunks
        chunks = state.get("chunks")
        if not chunks:
            logger.error("没有获取到chunks的内容，无法进行向量化")
            raise ValueError("没有获取到chunks的内容，无法进行向量化")


        # 对chunks进行向量化
        # 自己手动实现批处理
        for i in range(0,len(chunks),3):
            chunk_k_list = chunks[i:i+3]
            # 整理双向量化的字符串列表
            chunk_k_str_list = [f"{item.get('item_name')}\n{item.get('content')}" for item in chunk_k_list]
            embeddings = get_bge_embedding(chunk_k_str_list)

            # 我们向量化结束主要就是把每个内容对应的向量回填到对应的chunk中
            for idx, chunk in enumerate(chunk_k_list):
                chunk['dense_vector']=embeddings.get('dense')[idx] # 和get_bge_embedding的输出有关系
                chunk['sparse_vector']=embeddings.get('sparse')[idx] # 和get_bge_embedding的输出有关系


        with open(r"E:\Python_projects\output\hak180产品安全手册\chunks_embedding.json", 'w', encoding='utf-8') as f:
            f.write(json_format(chunks))

        return {
            "chunks":chunks
        }

if __name__ == '__main__':
    node = NodeBGEEmbedding()
    with open(r"E:\Python_projects\output\hak180产品安全手册\chunks_item_name.json", 'r', encoding='utf-8') as f:
        data = f.read() # 拿到的还是json串

    init_state = {
        "chunks":json.loads(data)
    }
    result = node(init_state)
    logger.info(json_format(result))