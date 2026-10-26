# atguigu/query_process/nodes/node_answer_output.py
import re

from atguigu.import_process.config.prompt import ANSWER_PROMPT
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.get_llm_model import get_item_llm_model
from atguigu.tool.logger import logger
from atguigu.tool.mongo_tool import save_chat_messages
from atguigu.tool.task_utils import put_data


class NodeAnswerOutput(NodeBase):
    """
    节点功能: 答案生成
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_answer_output"

    def process(self, state: QueryGraphState):
        """
        节点逻辑
        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """
        answer = state.get("answer")
        task_id = state.get("task_id")
        chunks = state.get("reranked_docs")
        history = state.get("history")
        item_names = state.get("item_names")
        rewritten_query = state.get("rewritten_query")

        if answer:
            # 意图识别的时候没有确定名字，那么就有答案要推给用户
            put_data(task_id,event="final",data={"answer":answer})
        else:
            # 拿到重排序断崖后得到的chunks交给大模型总结答案
            # 1.根据chunks整理context
            context = ""
            for idx,chunk in enumerate(chunks,start=1):
                title = chunk.get("title")
                content = chunk.get("content")
                url = chunk.get("url")
                source = chunk.get("source")
                chunk_str = f"[切片:{idx}]\n[标题:{title}]\n[内容:{content}]\n[链接:{url}]\n[来源:{source}]"
                context += chunk_str

            # 2.整理历史记录
            history_str = '\n'.join([f"{h.get('role')}:{h.get('text')}" for h in history])
            # 3.整理识别出来的item_names列表
            item_names_str = ",".join(item_names)
            # 4.整理用户问题
            question = rewritten_query

            answer_prompt = ANSWER_PROMPT.format(context=context,question=question,history=history_str,item_names=item_names_str)
            if len(answer_prompt) > 10000:
                answer_prompt = answer_prompt[:10000]
            # chunks的长度是最容易超过的

            llm = get_item_llm_model()

            messages = [
                {"role":"user","content":answer_prompt}
            ]

            res = llm.stream(input=messages) # 流式输出返回的是生成器
            for chunk in res:
                print(chunk.content)
                put_data(task_id,event="delta",data={"delta":chunk.content})
                answer += chunk.content # 后期历史记录需要保存


            # 推送完答案，我们手动拿图片作为最后的推送 1、防止大模型没有把图片解析显示 2、作为这次推送的结束标志
            seen = set()  # 用于去重，避免同一张图片重复出现
            md_img_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
            for i, doc in enumerate(chunks):
                # 检查 text 字段中的 Markdown 图片 (主要针对 Local Chunk)
                text = doc.get("content")
                matches = md_img_pattern.findall(text)
                for img_url in matches:
                    img_url = img_url.strip()
                    seen.add(img_url)
            images = list(seen)

            put_data(task_id,event="final",data={"image_urls":images})

            if answer:
                # 创建当前答案的历史记录并保存
                message_id = save_chat_messages(
                    session_id=state.get("session_id"),
                    role="assistant",
                    text=answer,
                    rewritten_query=question,item_names=item_names
                )

        return {
            "answer":answer,
            "message_id":message_id
        }




        return state