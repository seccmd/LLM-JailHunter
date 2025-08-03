# llm_client.py
from langchain_openai import ChatOpenAI


async def query_target_llm(prompt: str, config: dict) -> str:
    """向目标 LLM 发起查询"""
    llm = ChatOpenAI(
        model=config["model"],
        base_url=config["base_url"],
        api_key=config["api_key"],
        temperature=0.7,
        max_retries=2
    )
    try:
        message = [{"role": "user", "content": prompt}]
        ai_msg = await llm.ainvoke(message)
        return ai_msg.content
    except Exception as e:
        return f"[ERROR] {str(e)}"