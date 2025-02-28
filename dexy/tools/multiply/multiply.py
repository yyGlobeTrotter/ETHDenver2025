from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class MultiplyInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


class MultiplyTool(BaseTool):
    name: str = "Multiply"
    description: str = "A tool that multiplies two integers a and b."
    args_schema: Type[BaseModel] = MultiplyInput

    def _run(self, a: int, b: int) -> str:
        """
        Multiply two integers provided in tool_input.
        """
        return str(a * b)
