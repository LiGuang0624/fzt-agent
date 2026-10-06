import os
from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from utils.config_handler import rag_conf

# 火山方舟 Agent Plan 专属 OpenAI 兼容接口
# 请勿使用 https://ark.cn-beijing.volces.com/api/v3，会产生额外费用
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/plan/v3")


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatOpenAI(
            model=rag_conf["chat_model_name"],
            api_key=os.environ["ARK_API_KEY"],
            base_url=ARK_BASE_URL,
            temperature=0,
        )


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return OpenAIEmbeddings(
            model=rag_conf["embedding_model_name"],
            api_key=os.environ["ARK_API_KEY"],
            base_url=ARK_BASE_URL,
            check_embedding_ctx_length=False,
            chunk_size=10,
        )


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
