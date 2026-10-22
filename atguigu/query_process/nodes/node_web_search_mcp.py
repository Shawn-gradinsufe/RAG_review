# atguigu/query_process/nodes/node_web_search_mcp.py
import asyncio
import json
import os


from agents.mcp import MCPServerStreamableHttp
from atguigu.import_process.config.config import McpConfig
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.json_format import json_format
from atguigu.tool.logger import logger

class NodeWebSearchMcp(NodeBase):
    """
    节点功能，调用外部搜索引擎补充信息
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_web_search_mcp"

    def process(self, state: QueryGraphState):
        """
        节点逻辑
        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """

        rewritten_query = state.get("rewritten_query")
        if not rewritten_query:
            logger.error("改写后的用户问题不能为空")
            raise ValueError("改写后的用户问题不能为空")

        result = asyncio.run(self.mcp_run(rewritten_query)) # run是事件循环开始的标志

        # print(result,type(result))
        # # 调用协程函数,传入协程对象,
        # # .run()方法创建事件循环,运行事件循环,把协程对象加入事件循环
        # # 返回得到的result，是一个CallToolResult对象
        # print(result.content,type(result.content))
        # # 取出result.content里面的内容,是一个列表
        # print(result.content[0],type(result.content[0]))
        # # 取出列表里面的第一个元素,是一个TextContent对象
        # print(result.content[0].text,type(result.content[0].text))
        # # 取出TextContent对象里面的文本内容，是一个json串({}形式，但class却是str，说明是json串)
        data = json.loads(result.content[0].text).get("pages")
        # print(json_format(data))
        # 反序列化后得到字典,.get方法取出键为"pages"的值,是一个列表,列表里面是一个个的字典,
        # 字典中有"snippet",对应mcp检索到的摘要;"hostname"对应检索内容的站点主体域名,title是HTML中的<title>,url是完整网页链接
        
        chunks = [
            {
                "title": item.get('title'),
                "content": item.get('snippet'),
                "url": item.get('url'),
                "source": "web"
            }
            for item in data
        ]
        return {
            "web_search_docs":chunks
        }


    async def mcp_run(self,query,limit=10) -> None:
        token = McpConfig.mcp_api_key
        async with MCPServerStreamableHttp(
                name="网络搜索mcp工具",
                params={
                    "url": McpConfig.mcp_base_url,
                    "headers": {"Authorization": f"Bearer {token}"},
                    "timeout": 10,
                },
                cache_tools_list=True,
                max_retry_attempts=3,
        ) as server:
            # 原本使用的是智能体的方式,现在没办法使用,只能调用服务器工具的方法传递工具名的方式去使用,异步操作
            result = await server.call_tool(
                tool_name="bailian_web_search", # 阿里云百炼联网搜索功能MCP工具的工具名称
                arguments={
                    "query": query,
                    "count": limit
                }
            )
            return result

if __name__ == "__main__":

    init_state = {
        "rewritten_query": "关于BrotherHAK180烫金机如何使用"
    }

    # 执行节点的业务调用
    node_web_search_mcp = NodeWebSearchMcp()
    result = node_web_search_mcp(init_state)
    logger.info(json_format(result))