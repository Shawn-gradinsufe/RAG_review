from abc import ABC, abstractmethod

from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger


class NodeBase(ABC):
    name = "node_base"
    def __init__(self):
        if self.name == "node_base":
            logger.error(f"节点的{self.__class__.__name__}未配置，为节点名称")
            raise Exception(f"节点的{self.__class__.__name__}未配置，为节点名称")

    def __call__(self,state: ImportGraphState):
        try:
            logger.info(f"节点{self.name}开始执行")
            result = self.process(state)
            logger.info(f"节点{self.name}执行完毕")
            return result
        except Exception as e:
            logger.error(e)
            raise e

    @abstractmethod
    def process(self,state: ImportGraphState):
        pass