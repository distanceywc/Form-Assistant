from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from typing import Literal

from langchain_core.tools import tool

def get_react_agent( tools: list, prompt: str | None = None):
    model = ChatOpenAI(
            temperature=0,
            model='deepseek-chat',
            openai_api_key='xxx',
            openai_api_base='https://api.deepseek.com',
            streaming=False
            )
    if prompt:
        graph = create_react_agent(model, tools=tools, state_modifier=prompt)
    else:
        graph = create_react_agent(model, tools=tools)
    return graph