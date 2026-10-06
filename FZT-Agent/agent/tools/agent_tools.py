import csv
import os
import random

from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
from utils.config_handler import agent_conf
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

rag = RagSummarizeService()

client_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]

case_data = {}

# 演示用的赔偿金估算系数，仅用于展示工具调用链路，不代表真实法律标准
COMPENSATION_RULES = {
    "劳动争议": (2.0, "违法解除劳动合同赔偿金按 2N 估算（N 为工作年限对应月数）"),
    "交通事故": (1.5, "交通事故赔偿按基数 ×1.5 估算（含医疗、误工、护理等综合项）"),
    "人身损害": (1.2, "人身损害赔偿按基数 ×1.2 估算"),
    "合同纠纷": (1.0, "合同纠纷损失按基数 ×1.0 估算"),
}


@tool(description="从法律知识库中检索法条、司法解释、常见法律问答与办事流程等参考资料")
def legal_article_search(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="赔偿金计算器：根据案件类型与计算基数金额估算赔偿金额，结果为演示性估算")
def compensation_calculator(case_type: str, amount: float) -> str:
    factor, rule = COMPENSATION_RULES.get(case_type, (1.0, "未识别案件类型，按基数 ×1.0 估算"))
    result = amount * factor
    return (
        f"案件类型：{case_type}\n"
        f"计算基数：{amount:.2f} 元\n"
        f"估算规则：{rule}\n"
        f"估算赔偿金额：{result:.2f} 元\n"
        f"说明：本结果由演示性规则生成，仅供参考，实际金额须以法律规定与证据为准。"
    )


@tool(description="获取当前客户的ID，以纯字符串形式返回")
def get_client_id() -> str:
    return random.choice(client_ids)


def generate_case_data():
    """
    {
        "client_id": [
            {"案件类型": xxx, "案情摘要": xxx, "争议焦点": xxx, "已给建议": xxx, "受理时间": xxx},
            ...
        ],
        ...
    }
    """
    if not case_data:
        case_data_path = get_abs_path(agent_conf["external_data_path"])

        if not os.path.exists(case_data_path):
            raise FileNotFoundError(f"案件数据文件{case_data_path}不存在")

        with open(case_data_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                client_id = row["客户ID"].strip()
                case_data.setdefault(client_id, []).append(
                    {
                        "案件类型": row["案件类型"].strip(),
                        "案情摘要": row["案情摘要"].strip(),
                        "争议焦点": row["争议焦点"].strip(),
                        "已给建议": row["已给建议"].strip(),
                        "受理时间": row["受理时间"].strip(),
                    }
                )


@tool(description="根据客户ID检索该客户的全部历史案件记录，以纯字符串形式返回，未检索到返回空字符串")
def fetch_case_history(client_id: str) -> str:
    generate_case_data()

    records = case_data.get(client_id)
    if not records:
        logger.warning(f"[fetch_case_history]未检索到客户：{client_id}的案件记录")
        return ""

    return "\n".join(
        f"受理时间：{r['受理时间']}；案件类型：{r['案件类型']}；案情摘要：{r['案情摘要']}；"
        f"争议焦点：{r['争议焦点']}；已给建议：{r['已给建议']}"
        for r in records
    )


@tool(description="无入参，无返回值，调用后触发中间件自动为文书生成场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"
