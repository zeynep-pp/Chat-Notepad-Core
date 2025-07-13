from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    async def process(self, text: str, command: str) -> str:
        """Process input and return result"""
        pass

    async def validate_input(self, text: str, command: str) -> bool:
        """Validate input data"""
        return bool(text and text.strip() and command and command.strip())