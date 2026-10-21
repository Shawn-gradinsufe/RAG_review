# atguigu/query_process/nodes/node_search_embedding_hyde.py
from atguigu.import_process.config.config import MilvusConfig
from atguigu.import_process.config.prompt import HYDE_PROMPT
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.get_bge_embeddings import get_bge_embedding
from atguigu.tool.get_llm_model import get_item_llm_model
from atguigu.tool.json_format import json_format
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import get_search_reqs, hybrid_search


class NodeSearchEmbeddingHyde(NodeBase):
    """
    节点功能：HyDE (Hypothetical Document Embedding)
    先让 LLM 生成假设性答案，再对答案进行向量检索，提高召回率。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_search_embedding_hyde"

    def process(self, state: QueryGraphState):
        """
        节点逻辑
        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """

        rewritten_query = state.get("rewritten_query")
        item_names = state.get("item_names")  # 是一个字典,里面是前一步意图识别节点大模型识别出的用户问题中关联的商品名称
        if not rewritten_query:
            logger.error("改写后的用户问题不能为空")
            raise ValueError("改写后的用户问题不能为空")

        if not item_names:  # 这里是否还需要进行防御性判断？item_names为空,应该已经在前一个节点被拦截了
            logger.error("模型未能识别您的问题")
            raise ValueError("模型未能识别您的问题")


        # 先把重写的问题传给大模型,让大模型生成假设性答案
        llm = get_item_llm_model()
        messages = [
            {"role":"user","content": HYDE_PROMPT.format(rewritten_query=rewritten_query)}
        ]

        res = llm.invoke(input=messages)
        # print(res,type(res))
        # 注意:大模型调用返回的是一个AIMessage对象,需要调用content属性获取文本内容,而content属性取出来的内容是一个json串
        hyde_answer = res.content # 是一个字符串
        # print(hyde_answer, type(hyde_answer))


        # 把生成的假设性答案进行向量化
        embeddings = get_bge_embedding([rewritten_query, hyde_answer])
        dense_data = embeddings.get("dense")[0]
        sparse_data = embeddings.get("sparse")[0]

        # 混合检索
        # 为了防止milvus解析时,发生错误
        item_names = [
            item_name.replace("\\", "\\\\").replace("\'", "\\'").replace('\"', '\\"')
            for item_name in item_names
        ]
        #
        expr = f"item_name in {json_format(item_names)}"
        # 告诉milvus检索时应该过滤哪些数据的查询表达式，代表一个标量过滤条件，类似Mysql的where

        reqs = get_search_reqs(
            dense_data=[dense_data],
            dense_anns_field="dense_vector",
            sparse_data=[sparse_data],
            sparse_anns_field="sparse_vector",
            expr=expr,
        )  # 返回两个检索请求的实例组成的列表，是混合检索的参数

        # 混合检索
        res = hybrid_search(
            collection_name=MilvusConfig.chunks_collection,  # 检索的是商品名称的集合，标量判断过滤商品名
            reqs=reqs,
            output_fields=["id", "title", "file_title", "content", "part", "item_name"],
            # 检索结果中需要返回的字段，这和之前在向量数据库中存了什么字段有关系，因为现在检索的是chunks_collection集合，所以这里要和存的时候对应
            ranker=(0.7, 0.3)
        )

        chunks = [
            {
                **item.get("entity"),
                "score": item.get("distance"),
                "source": "local"
            }
            for item in res[0]
        ]

        return {
            "hyde_embedding_chunks": chunks
        }




# atguigu/query_process/node_search_embedding_hyde.py
if __name__ == "__main__":
    init_state = {
        "rewritten_query": "关于BrotherHAK180烫金机如何使用",
        "item_names": ["BrotherHAK180烫金机"]
    }
    node_search_embedding_hyde = NodeSearchEmbeddingHyde()
    result = node_search_embedding_hyde(init_state)
    logger.info(json_format(result))