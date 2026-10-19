from pathlib import Path

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger


class NodeEntry(NodeBase):
    """
    入口节点：任务分发
    """

    name = "node_entry"

    def process(self, state: ImportGraphState):
        local_file_path = state.get("local_file_path")
        if not local_file_path:
            logger.error("文件路径未指定")
            raise Exception("文件路径未指定")

        # 文件路径指定了,判断是否读取到文件
        local_file_path_obj = Path(local_file_path)
        # Path对象包裹路径,内部会规范化解析路径
        # print(local_file_path_obj.exists()) 结果是一个bool值
        # 包装成了Path对象,但不会立刻去磁盘读取文件
        if not local_file_path_obj.exists():# Path对象调用exists()方法才真正访问磁盘,判断是否存在
            logger.error("文件不存在")
            raise Exception("文件不存在")

        # 文件读到了,判断是否是支持解析的文件格式
        suffix = local_file_path_obj.suffix
        file_title = local_file_path_obj.stem # stem是不包含后缀名的文件名;name是包含后缀名的文件名,
                                              # Path继承了PurePath类对象的这两个属性
        # print(file_title)
        if suffix == ".pdf":
            return {
                "pdf_path":str(local_file_path_obj),
                # 这里为什么用str(local_file_path_obj)而不使用原始路径local_file_path？
                # 图任务流中,state 在多个节点之间流转，后面还有其他节点（pdf 解析节点、md 解析节点）读取 `pdf_path`
                # 不是技术上必须这么写，是工程设计上的选择：保证传递出去的路径，永远是经过 Path 标准化清洗后的路径，
                # 而不是原始输入的裸字符串 `local_file_path`
                # str(local_file_path_obj)保证
                "file_title":file_title,
                "is_pdf_read_enabled":True
            }
        elif suffix == ".md":
            return {
                "md_path": str(local_file_path_obj),
                "file_title":file_title,
                "is_md_read_enabled":True
            }
        else:
            logger.error("不支持的文件类型")
            raise Exception(f"不支持的文件类型,只支持PDF和MD文件")



if __name__ == '__main__':
    node = NodeEntry()
    init_state = {
        "local_file_path":r"E:\Python_projects\output\hak180产品安全手册.pdf"
    }
    result = node(init_state)
    logger.info(result)