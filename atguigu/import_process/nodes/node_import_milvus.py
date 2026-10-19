import json

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState


class NodeImportMilvus(NodeBase):
    """
    导入向量库节点：数据持久化
    """

    name = "node_import_milvus"

    def process(self, state: ImportGraphState):
        # 从state中获取chunks

        return state

if __name__ == '__main__':
    node = NodeImportMilvus()
    with open(r"E:\Python_projects\output\hak180产品安全手册\chunks_embedding.json","w",encoding="utf-8") as f:
        chunks=json.load(f)

    init_state = {
        "chunks":chunks,
    }
    result = node(init_state)
    logger.info(json_format(result))