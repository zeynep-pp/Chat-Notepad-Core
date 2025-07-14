from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import time
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    async def process(self, text: str, command: str) -> Dict[str, Any]:
        """Process input and return result with agent_info"""
        pass

    async def validate_input(self, text: str, command: str) -> bool:
        """Validate input data"""
        return bool(text and text.strip() and command and command.strip())