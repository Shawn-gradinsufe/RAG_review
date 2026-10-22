# atguigu/query_process/nodes/node_rrf.py

from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.json_format import json_format
from atguigu.tool.logger import logger

class NodeRrf(NodeBase):
    """
    节点功能：Reciprocal Rank Fusion
    将多路召回的结果（向量、HyDE、Web）进行加权融合排序。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_rrf"

    def process(self, state: QueryGraphState):
        """
        节点逻辑
        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """
        embedding_chunks = state.get("embedding_chunks")
        # 是个列表
        hyde_embedding_chunks = state.get("hyde_embedding_chunks")

        # 设定权重值 分子自行设定
        weighted_embedding_chunks = [
            (embedding_chunks, 1),
            (hyde_embedding_chunks, 1),
        ]


        rrf_dict = {}

        for chunks,weight in weighted_embedding_chunks:
            # 遍历每个回路检索到的chunks,计算RRF_Score,每个回路有自己的权重
            for idx,chunk in enumerate(chunks): # 取出了embedding_chunks的索引和值(字典),索引就是该chunk(字典)对应的排名
                score = weight / (60 + idx)
                # 分回路计算每个chunk的RRF_Score,先按照chunk算,再按回路算
                # 用id作为键,区分chunk
                id = chunk.get("id")

                if id in rrf_dict:
                    # 如果id已经存在,说明该id对应的chunk已经存在,已经在其他路检索到过,则累加该id对应的score
                    rrf_dict[id]["score"] += score
                else:
                    # 如果id不存在,说明该id对应的chunk是第一次检索到,则初始化该id的score
                    # 原本chunk的字典的score只是该路的相似度分数
                    chunk["score"] = score
                    rrf_dict[id] = chunk

        # 最终得到的rrf_dict是一个字典,键是chunk的id,值是该chunk,相较于此节点处理前,chunk字典中的score变成了RRF_Score,

        rrf_chunks = sorted(rrf_dict.values(), key=lambda x: x["score"], reverse=True)[:10]

        return {
            "rrf_chunks":rrf_chunks
        }

if __name__ == '__main__':

    node = NodeRrf()
    # 模拟两路检索结果
    init_state =  {
    "embedding_chunks": [
        {
            "content": "## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。",
            "part": 0,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748361,
            "title": "## HAK 180 烫金机",
            "file_title": "hak180产品安全手册",
            "score": 0.7724524736404419,
            "source": "local"
        },
        {
            "content": "## HAK 180 烫金机\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。",
            "part": 1,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748362,
            "title": "## HAK 180 烫金机",
            "file_title": "hak180产品安全手册",
            "score": 0.7701514959335327,
            "source": "local"
        },
        {
            "content": "## 设备\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/ 或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。",
            "part": 1,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748366,
            "title": "## 设备",
            "file_title": "hak180产品安全手册",
            "score": 0.761479914188385,
            "source": "local"
        },
        {
            "content": "## 设备\n\n•\t请先阅读这本手册，再尝试操作本设备或尝试进行任何维护。不按照这些说明操作可能会提高发生人员受伤或财产损坏（包括火灾、触电、烧伤或窒息所致）的风险。对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t请勿在未去除所有包装材料的情况下使用本设备，包括本设备内部的任何附加的包装材料。否则可能会产生火灾的风险。\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。",
            "part": 0,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748365,
            "title": "## 设备",
            "file_title": "hak180产品安全手册",
            "score": 0.7578579783439636,
            "source": "local"
        },
        {
            "content": "![](images/f93ddcd837fa399f0c165da43b0badb013c2961acc828a095c6d98f0a660dbca.jpg)  \nD01WD7001-00\n\nSCHN",
            "part": 0,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748360,
            "title": "无标题",
            "file_title": "hak180产品安全手册",
            "score": 0.7532786726951599,
            "source": "local"
        },
        {
            "content": "## 设备\n\n![](images/71f9e17a760882436455f7ddc3a5fd358ce821ceb6e598b76d013d93dc26c943.jpg)",
            "part": 6,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748371,
            "title": "## 设备",
            "file_title": "hak180产品安全手册",
            "score": 0.7532770037651062,
            "source": "local"
        },
        {
            "content": "## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通常需要合格技术进行全面工作以将本设备恢复到正常操作。Brother不建议使用 Brother 正品烫金膜盒以外的其他品牌烫金膜盒。如果使用与本设备不兼容的耗材导致损坏本设备的任何零件，由此导致的任何维修可能不在保修范围内。",
            "part": 0,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748379,
            "title": "## 设备",
            "file_title": "hak180产品安全手册",
            "score": 0.7525407671928406,
            "source": "local"
        },
        {
            "content": "## HAK 180 烫金机\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。\n\n•\t请注意，对于使用通过本设备制作的产品造成的任何损坏或利润损失，或者故障、维修导致的数据消失或更改，或者第三方提出的任何索赔，我们不承担任何责任。",
            "part": 2,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748363,
            "title": "## HAK 180 烫金机",
            "file_title": "hak180产品安全手册",
            "score": 0.7518904209136963,
            "source": "local"
        },
        {
            "content": "## 设备\n\n•\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![](images/944ad0b1ae642d4a65bc1b40c979beeb12bc30e6a409b9d9666ee013ff48cc60.jpg)\n\n![](images/3bf3b3639360a2c43c223a6ee46c44b27d54f4a79506a17a8b99e6ba4703df40.jpg)",
            "part": 0,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748375,
            "title": "## 设备",
            "file_title": "hak180产品安全手册",
            "score": 0.5346356630325317,
            "source": "local"
        },
        {
            "content": "## 设备\n\n•\t如果水、其他液体或金属物体进入设备内部，请立即从电源插座中拔掉设备的插头，然后联系 Brother 呼叫中心或您当地的 Brother经销商。\n\n•\t请勿在卡纸或有纸张散落在设备内部的情况下尝试使用本设备。纸张与定影单元长时间接触可能导致火灾。\n\n•\t请勿使用任何易燃物品、任何类型的喷雾剂包含酒精或氨水的有机溶剂/液体来清洁本设备的内部或外部。否则可能导致火灾。请改用无绒干抹布。有关如何清洁本设备的说明，请参阅使用说明书。",
            "part": 3,
            "item_name": "BrotherHAK180烫金机",
            "id": 469867433341748368,
            "title": "## 设备",
            "file_title": "hak180产品安全手册",
            "score": 0.516148030757904,
            "source": "local"
        }
    ],
        "hyde_embedding_chunks": [
            {
                "id": 469867433341748361,
                "title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。",
                "part": 0,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.8025564551353455,
                "source": "local"
            },
            {
                "id": 469867433341748362,
                "title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。",
                "part": 1,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.7997452020645142,
                "source": "local"
            },
            {
                "id": 469867433341748366,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/ 或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。",
                "part": 1,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.7913774251937866,
                "source": "local"
            },
            {
                "id": 469867433341748365,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t请先阅读这本手册，再尝试操作本设备或尝试进行任何维护。不按照这些说明操作可能会提高发生人员受伤或财产损坏（包括火灾、触电、烧伤或窒息所致）的风险。对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t请勿在未去除所有包装材料的情况下使用本设备，包括本设备内部的任何附加的包装材料。否则可能会产生火灾的风险。\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。",
                "part": 0,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.7864068746566772,
                "source": "local"
            },
            {
                "id": 469867433341748371,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n![](images/71f9e17a760882436455f7ddc3a5fd358ce821ceb6e598b76d013d93dc26c943.jpg)",
                "part": 6,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.781753420829773,
                "source": "local"
            },
            {
                "id": 469867433341748360,
                "title": "无标题",
                "file_title": "hak180产品安全手册",
                "content": "![](images/f93ddcd837fa399f0c165da43b0badb013c2961acc828a095c6d98f0a660dbca.jpg)  \nD01WD7001-00\n\nSCHN",
                "part": 0,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.7812181711196899,
                "source": "local"
            },
            {
                "id": 469867433341748379,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通常需要合格技术进行全面工作以将本设备恢复到正常操作。Brother不建议使用 Brother 正品烫金膜盒以外的其他品牌烫金膜盒。如果使用与本设备不兼容的耗材导致损坏本设备的任何零件，由此导致的任何维修可能不在保修范围内。",
                "part": 0,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.7809694409370422,
                "source": "local"
            },
            {
                "id": 469867433341748363,
                "title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。\n\n•\t请注意，对于使用通过本设备制作的产品造成的任何损坏或利润损失，或者故障、维修导致的数据消失或更改，或者第三方提出的任何索赔，我们不承担任何责任。",
                "part": 2,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.7801679372787476,
                "source": "local"
            },
            {
                "id": 469867433341748375,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![](images/944ad0b1ae642d4a65bc1b40c979beeb12bc30e6a409b9d9666ee013ff48cc60.jpg)\n\n![](images/3bf3b3639360a2c43c223a6ee46c44b27d54f4a79506a17a8b99e6ba4703df40.jpg)",
                "part": 0,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.6237751245498657,
                "source": "local"
            },
            {
                "id": 469867433341748368,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t如果水、其他液体或金属物体进入设备内部，请立即从电源插座中拔掉设备的插头，然后联系 Brother 呼叫中心或您当地的 Brother经销商。\n\n•\t请勿在卡纸或有纸张散落在设备内部的情况下尝试使用本设备。纸张与定影单元长时间接触可能导致火灾。\n\n•\t请勿使用任何易燃物品、任何类型的喷雾剂包含酒精或氨水的有机溶剂/液体来清洁本设备的内部或外部。否则可能导致火灾。请改用无绒干抹布。有关如何清洁本设备的说明，请参阅使用说明书。",
                "part": 3,
                "item_name": "BrotherHAK180烫金机",
                "score": 0.6022157073020935,
                "source": "local"
            }
        ]
    }

    result = node(init_state)
    logger.info(json_format(result))
