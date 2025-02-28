from langchain_core.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@tool
def cantar():
    """Sing a song in spanish"""
    return "Bailando bajo la luna, tus ojos brillan como el mar."
