# atguigu/query_process/nodes/node_search_embedding.py
from atguigu.import_process.config.config import MilvusConfig
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.get_bge_embeddings import get_bge_embedding
from atguigu.tool.json_format import json_format
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import get_search_reqs, hybrid_search


class NodeSearchEmbedding(NodeBase):
    """
    节点功能：基于已确认主体名+改写后的用户问题，执行Milvus向量数据库混合检索
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_search_embedding"

    def process(self, state: QueryGraphState):
        """
        节点逻辑
        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """
        rewritten_query = state.get("rewritten_query")
        item_names=state.get("item_names") # 是一个字典,里面是前一步意图识别节点大模型识别出的用户问题中关联的商品名称
        if not rewritten_query:
            logger.error("改写后的用户问题不能为空")
            raise ValueError("改写后的用户问题不能为空")

        if not item_names: # 这里是否还需要进行防御性判断？item_names为空,应该已经在前一个节点被拦截了
            logger.error("模型未能识别您的问题")
            raise ValueError("模型未能识别您的问题")



        # 问题向量化
        embeddings = get_bge_embedding([rewritten_query])
        dense_data = embeddings.get("dense")[0]
        sparse_data = embeddings.get("sparse")[0]

        # 混合检索
        # 为了milvus解析时,发生错误
        item_names = [
            item_name.replace("\\","\\\\").replace("\'","\\'").replace('\"','\\"')
            for item_name in item_names
        ]
        #
        expr = f"item_name in {json_format(item_names)}"
        # expr = f"item_name in {item_names}"# 也可以,但是json_format的好处是防止万一里面有特殊字符导致解析出错
        # 告诉milvus检索时应该过滤哪些数据的查询表达式，代表一个标量过滤条件，类似Mysql的where

        reqs = get_search_reqs(
            dense_data = [dense_data],
            dense_anns_field= "dense_vector",
            sparse_data = [sparse_data],
            sparse_anns_field= "sparse_vector",
            expr = expr,
        ) # 返回两个检索请求的实例组成的列表，是混合检索的参数

        # 混合检索
        res = hybrid_search(
            collection_name = MilvusConfig.chunks_collection, # 检索的是商品名称的集合，标量判断过滤商品名
            reqs = reqs,
            output_fields=["id","title","file_title","content","part","item_name"],
            # 检索结果中需要返回的字段，这和之前在向量数据库中存了什么字段有关系，因为现在检索的是chunks_collection集合，所以这里要和存的时候对应
            ranker=(0.6,0.4) 
        )

        # print(res,type(res))
        # res是一个SearchResult对象,继承了list,
        # 源码:class SearchResult(list):
        # 因此可以使用切片/for循环遍历,里面包含了检索结果
        # print(res[0],type(res[0]))
        # SearchResult返回有几个结果由查询的次数决定,这里是1个结果,因为只有一个检索请求
        # 这里的res[0]返回得到的是一个HybridHits对象，HybridHits对象仍然是一个列表，这个列表中是一个个的字典
        # 字典的个数由hybrid_search的limit参数决定,limit默认是10,这里返回了10个字典

        chunks = [
            {
                **item.get("entity"),
                "score": item.get("distance"),
                "source": "local"
            }
            for item in res[0] # res[0]仍然是一个列表，遍历res[0]取得一个个返回的chunk字典，然后对检索到的chunk字典做内容修改
        ]

        # print(chunks)

        return {
            "embedding_chunks":chunks
        }
        # chunks 是一个列表,列表里面是一个个字典,每个字典是一个经过检索得到的chunks


if __name__ == "__main__":
    init_state = {
        "rewritten_query": "关于BrotherHAK180烫金机如何使用",
        "item_names": ["BrotherHAK180烫金机"]  # 一定要和你自己的milvus存储的名字一致
    }
    node_search_embedding = NodeSearchEmbedding()
    result = node_search_embedding(init_state)
    logger.info(json_format(result))