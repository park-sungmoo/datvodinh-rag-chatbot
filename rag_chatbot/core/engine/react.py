from llama_index.core.agent import ReActAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import RetrieverTool, ToolMetadata
from ..prompt import get_system_prompt
from .retriever import LocalRetriever
from llama_index.core.llms.llm import LLM
from llama_index.core.schema import BaseNode
from typing import List
from ...setting import RAGSettings


class ReActRAGAgent:
    def __init__(
        self,
        setting: RAGSettings | None = None,
        host: str = "host.docker.internal"
    ):
        self._setting = setting or RAGSettings()
        self._retriever = LocalRetriever(self._setting)
        self._host = host

    def set_engine(
        self,
        llm: LLM,
        nodes: List[BaseNode],
        language: str = "eng",
    ):
        # Chat engine with documents
        retriever = self._retriever.get_retrievers(
            llm=llm,
            language=language,
            nodes=nodes
        )

        retriever_tool = RetrieverTool(
            retriever=retriever,
            metadata=ToolMetadata(
                description=(
                    "Use this tool for question related to university (such as HUST)"
                    "or about IT major such as Computer Science."
                    "Only use when user mention about HUST or IT major at HUST "
                    "(not IT related field such as Machine Learning or Software Engineer, only IT major at HUST)."
                    "Do NOT use this tool for other questions that are NOT related to HUST and IT major at HUST, "
                    "even if the question is about IT field (but not related to HUST)."
                ),
                name="retriever",
            ),
        )

        agent = ReActAgent.from_tools(
            tools=[retriever_tool],
            llm=llm,
            verbose=True,
            memory=ChatMemoryBuffer(
                token_limit=self._setting.ollama.chat_token_limit
            ),
            context=get_system_prompt(language, is_rag_prompt=False)
        )
        return agent
