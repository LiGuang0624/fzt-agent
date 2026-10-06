# 法智通 · 法律咨询助手

基于 **ReAct Agent + RAG（检索增强生成）** 架构的法律领域智能助手，面向常见法律问题提供知识问答、赔偿金估算与个性化「案件行动建议报告」生成能力。

> 本项目为学习 / 演示性质，回答与报告均由大模型结合演示知识库自动生成，**不构成正式法律意见**，涉及重大权益请咨询执业律师。

## 项目简介

「法智通」构建了一个具备自主推理与工具调用能力的 AI Agent，能够：

- **法律问答**：围绕劳动争议、交通事故、婚姻家庭、房屋租赁、合同纠纷、民间借贷等常见领域，结合知识库给出有法律依据的解答
- **赔偿估算**：根据案件类型与计算基数，调用赔偿金计算器给出演示性估算（含免责说明）
- **报告生成**：读取客户历史案件记录，自动生成结构化的《案件行动建议报告》，含争议焦点、法律依据、分步行动建议、风险提示与证据清单

## 核心特性

- **ReAct 推理循环**：Agent 遵循「思考 → 行动 → 观察 → 再思考」流程，自主判断是否调用工具、调用哪个工具，最多支持 5 次工具调用迭代
- **动态提示词切换**：通过 LangGraph 中间件的 `@dynamic_prompt` 机制，在识别到报告生成场景时，自动从「法律咨询」角色切换为「法律文书撰写」角色
- **RAG 检索增强**：法律知识库经 ChromaDB 向量检索（Top-3）后交由大模型总结，确保回答有据可依
- **MD5 去重**：知识库文件通过 MD5 哈希去重，重复运行不会重复写入向量库
- **全链路可观测**：工具调用与模型调用均通过中间件写入日志，便于调试与追踪

## 技术架构

```
用户输入 (Streamlit UI)
    │
    ▼
ReactAgent (LangChain create_agent)
    │
    ├── 系统提示词 (动态切换)
    │   ├── main_prompt.txt    ← 法律咨询模式
    │   └── report_prompt.txt  ← 报告生成模式
    │
    ├── 中间件 middleware
    │   ├── monitor_tool          → 工具调用监控 + 上下文注入
    │   ├── log_before_model      → 模型调用日志
    │   └── report_prompt_switch  → 动态提示词切换
    │
    └── 工具集 tools
        ├── legal_article_search     → RAG 知识库检索
        ├── compensation_calculator  → 赔偿金估算（演示）
        ├── get_client_id            → 获取当前客户 ID
        ├── fetch_case_history       → 检索客户历史案件
        └── fill_context_for_report  → 触发报告生成上下文
```

### 工具与中间件说明

| 名称 | 类型 | 作用 |
|------|------|------|
| `legal_article_search` | 工具 | 从法律知识库检索法条、司法解释、常见问答与办事流程 |
| `compensation_calculator` | 工具 | 按案件类型与基数估算赔偿金额（演示性规则） |
| `get_client_id` | 工具 | 获取当前客户唯一标识 |
| `fetch_case_history` | 工具 | 根据客户 ID 检索全部历史案件记录 |
| `fill_context_for_report` | 工具 | 触发中间件注入报告上下文（报告生成前置步骤） |
| `monitor_tool` | 中间件 | 记录工具调用入参/结果，并在报告工具调用后置位上下文标记 |
| `log_before_model` | 中间件 | 每次模型调用前记录消息数量与内容 |
| `report_prompt_switch` | 中间件 | 依据上下文标记动态切换系统提示词 |

## 技术栈

| 组件 | 技术选型 |
|------|----------|
| **大语言模型** | DeepSeek-V4.1-Flash（火山方舟 OpenAI 兼容接口） |
| **嵌入模型** | doubao-embedding-vision（火山方舟） |
| **Agent 框架** | LangChain + LangGraph（`create_agent` + middleware） |
| **向量数据库** | ChromaDB |
| **前端界面** | Streamlit |
| **文本分割** | RecursiveCharacterTextSplitter |
| **配置管理** | PyYAML |

## 项目结构

```
agent----main/
├── README.md
└── FZT-Agent/                       # 项目主目录
    ├── app.py                       # Streamlit 应用入口
    ├── requirements.txt             # 依赖清单
    ├── md5.text                     # 知识库文件 MD5 去重记录
    │
    ├── agent/                       # Agent 核心
    │   ├── react_agent.py           # ReAct Agent 定义与流式执行
    │   └── tools/
    │       ├── agent_tools.py       # 5 个工具函数
    │       └── middleware.py        # 3 个中间件
    │
    ├── rag/                         # RAG 检索增强生成
    │   ├── rag_service.py           # 检索 + 大模型总结服务
    │   └── vector_store.py          # ChromaDB 向量存储与文档加载
    │
    ├── model/
    │   └── factory.py               # 模型工厂（对话模型 + 嵌入模型）
    │
    ├── config/                      # 配置文件
    │   ├── agent.yml                # 外部数据路径
    │   ├── chroma.yml               # ChromaDB 参数
    │   ├── rag.yml                  # 模型名称
    │   └── prompts.yml              # 提示词文件路径
    │
    ├── prompts/                     # 提示词模板
    │   ├── main_prompt.txt          # 法律咨询模式提示词
    │   ├── report_prompt.txt        # 报告生成模式提示词
    │   └── rag_summarize.txt        # RAG 总结提示词
    │
    ├── data/                        # 知识库与数据
    │   ├── 交通事故赔偿_要点.txt
    │   ├── 劳动法_常见问题.txt
    │   ├── 婚姻家庭_法律问答.txt
    │   ├── 房屋租赁_纠纷处理.txt
    │   ├── 民法典_合同编_要点.txt
    │   ├── 民间借贷_法律要点.txt
    │   └── external/
    │       └── cases.csv            # 模拟客户案件记录（10 位客户）
    │
    ├── utils/                       # 工具模块
    │   ├── config_handler.py        # YAML 配置加载
    │   ├── file_handler.py          # 文件处理（MD5、PDF/TXT 加载）
    │   ├── logger_handler.py        # 日志系统
    │   ├── path_tool.py             # 绝对路径解析
    │   └── prompt_loader.py         # 提示词文件加载
    │
    ├── chroma_db/                   # 向量库持久化目录（运行后生成）
    └── logs/                        # 运行日志（运行后生成）
```

## 快速开始

### 环境要求

- Python 3.10+
- 火山方舟（Volcengine Ark）API Key

### 安装步骤

1. **克隆项目**

```bash
git clone <your-repo-url>
cd agent----main/FZT-Agent
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置 API Key**

项目通过 `ARK_API_KEY` 环境变量读取密钥：

```bash
# Linux / macOS
export ARK_API_KEY="your-api-key"

# Windows (CMD)
set ARK_API_KEY=your-api-key

# Windows (PowerShell)
$env:ARK_API_KEY="your-api-key"
```

4. **加载知识库**（首次运行，将 `data/` 下的法律文本写入向量库）

```bash
python -m rag.vector_store
```

5. **启动应用**

```bash
streamlit run app.py
```

启动后在浏览器访问 `http://localhost:8501` 即可使用。

## 使用示例

### 法律问答

```
用户：公司违法解除劳动合同应该怎么赔偿？
法智通：[调用 legal_article_search 检索劳动法资料]
        根据劳动法相关规定，用人单位违法解除劳动合同的，劳动者可以要求
        继续履行合同，或要求支付赔偿金。经济补偿按工作年限每满一年支付
        一个月工资，违法解除的赔偿金为经济补偿标准的两倍（即 2N）……
```

### 赔偿估算

```
用户：交通事故对方全责，医疗费花了 5 万，大概能赔多少？
法智通：[调用 compensation_calculator(case_type="交通事故", amount=50000)]
        估算赔偿金额：75000.00 元（演示性估算，实际金额须以法律规定与证据为准）
```

### 报告生成

```
用户：帮我生成我的案件行动建议报告
法智通：[固定工具链：get_client_id → fill_context_for_report → fetch_case_history]
        # 法智通案件行动建议报告
        ## 一、案件基本情况
        ## 二、争议焦点与法律依据
        ## 三、行动建议（分步骤、可操作）
        ## 四、风险提示与证据清单
        ## 五、免责声明
```

## 配置说明

所有配置位于 `FZT-Agent/config/` 目录，均为 YAML 格式：

- **rag.yml**：对话模型名称（默认 `DeepSeek-V4.1-Flash`）与嵌入模型名称（默认 `doubao-embedding-vision`）
- **chroma.yml**：向量库集合名、持久化目录、检索数量 `k`、分块大小/重叠、分隔符、允许的知识库文件类型
- **agent.yml**：外部案件数据文件路径
- **prompts.yml**：各提示词文件路径映射

## 免责声明

- 本项目知识库内容为**演示用法律常识整理**，赔偿金计算器使用**演示性估算规则**，均不代表真实法律标准
- 所有回答与报告由大模型自动生成，仅供参考，**不构成正式法律意见**
- 涉及重大权益时，请务必咨询执业律师

## License

本项目仅供学习与研究使用。
