'''第三步开始到最后所有'''
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from atguigu.import_process.nodes.node_bge_embedding import NodeBGEEmbedding
from atguigu.import_process.nodes.node_document_spilt import NodeDocumentSplit
from atguigu.import_process.nodes.node_entry import NodeEntry
from atguigu.import_process.nodes.node_import_milvus import NodeImportMilvus
from atguigu.import_process.nodes.node_item_name_recognition import NodeItemNameRecognition
from atguigu.import_process.nodes.node_md_img import NodeMDImg
from atguigu.import_process.nodes.node_pdf_to_md import NodePDFToMD
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger

# 创建builder
# builder = StateGraph(state_schema=ImportGraphState)
#
# # 注册节点
# builder.add_node(NodeEntry.name,NodeEntry())
# builder.add_node(NodePDFToMD.name,NodePDFToMD())
# builder.add_node(NodeMDImg.name,NodeMDImg())
# builder.add_node(NodeDocumentSplit.name,NodeDocumentSplit())
# builder.add_node(NodeItemNameRecognition.name,NodeItemNameRecognition())
# builder.add_node(NodeBGEEmbedding.name,NodeBGEEmbedding())
# builder.add_node(NodeImportMilvus.name,NodeImportMilvus())
#
# # 定义条件边的路由函数
# def after_entry_router(state: ImportGraphState):
#     is_pdf_read_enabled = state.get("is_pdf_read_enabled")
#     is_md_read_enabled = state.get("is_md_read_enabled")
#
#     if is_pdf_read_enabled:
#         return NodePDFToMD.name
#     elif is_md_read_enabled:
#         return NodeMDImg.name
#     else:
#         return END
#
# # 添加边
# builder.add_edge(START,NodeEntry.name)
# builder.add_contional_edges(NodeEntry.name,after_entry_router)
# builder.add_edge(NodePDFToMD.name,NodeMDImg.name)
# builder.add_edge(NodeMDImg.name,NodeDocumentSplit.name)
# builder.add_edge(NodeDocumentSplit.name,NodeItemNameRecognition.name)
# builder.add_edge(NodeItemNameRecognition.name,NodeBGEEmbedding.name)
# builder.add_edge(NodeBGEEmbedding.name,NodeImportMilvus.name)
# builder.add_edge(NodeImportMilvus.name,END)
#
# # 编译builder
# graph = builder.compile()
# print(graph)
#
# # 传入初始状态
#
#
# init_state = {
#     "local_file_path":r"E:\Python_projects\output\hak180产品安全手册.pdf"
# }
# result = graph.invoke(init_state)
# logger.info(result)

class MainGraphRunner:
    def __init__(self):
        self.builder = StateGraph(state_schema=ImportGraphState)
        self.add_nodes()
        self.add_edges()
        self.graph = None

    def add_nodes(self):
        self.builder.add_node(NodeEntry.name, NodeEntry())
        self.builder.add_node(NodePDFToMD.name, NodePDFToMD())
        self.builder.add_node(NodeMDImg.name, NodeMDImg())
        self.builder.add_node(NodeDocumentSplit.name, NodeDocumentSplit())
        self.builder.add_node(NodeItemNameRecognition.name, NodeItemNameRecognition())
        self.builder.add_node(NodeBGEEmbedding.name, NodeBGEEmbedding())
        self.builder.add_node(NodeImportMilvus.name, NodeImportMilvus())

    def add_edges(self):
        self.builder.add_edge(START, NodeEntry.name)
        self.builder.add_conditional_edges(NodeEntry.name, self.after_entry_router)
        self.builder.add_edge(NodePDFToMD.name, NodeMDImg.name)
        self.builder.add_edge(NodeMDImg.name, NodeDocumentSplit.name)
        self.builder.add_edge(NodeDocumentSplit.name, NodeItemNameRecognition.name)
        self.builder.add_edge(NodeItemNameRecognition.name, NodeBGEEmbedding.name)
        self.builder.add_edge(NodeBGEEmbedding.name, NodeImportMilvus.name)
        self.builder.add_edge(NodeImportMilvus.name, END)

    def after_entry_router(self,state: ImportGraphState):
        is_pdf_read_enabled = state.get("is_pdf_read_enabled")
        is_md_read_enabled = state.get("is_md_read_enabled")

        if is_pdf_read_enabled:
            return NodePDFToMD.name
        elif is_md_read_enabled:
            return NodeMDImg.name
        else:
            return END

    def run(self,state):
        # 两个作用：1、懒加载 2、如果一个人实例化了一个对象，然后通过这个对象同时执行graph多次不能重复编译（单例）
        if self.graph is None:
            self.graph = self.builder.compile()
        result = self.graph.invoke(state)
        return result

    @classmethod
    def create_and_run(cls,state):
        return cls().run(state)

if __name__ == '__main__':
    init_state = {
        "local_file_path": r"E:\Python_projects\output\hak180产品安全手册.pdf",
        "local_dir": r"E:\Python_projects\output",
    }
    result = MainGraphRunner.create_and_run(init_state)
    logger.info(result)