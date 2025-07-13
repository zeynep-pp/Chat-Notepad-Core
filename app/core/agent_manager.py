from typing import Dict
from ..agents.base_agent import BaseAgent
from ..agents.text_editor_agent import TextEditorAgent
from ..agents.summarizer_agent import SummarizerAgent

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {
            "editor": TextEditorAgent("editor"),
            "summarizer": SummarizerAgent("summarizer")
        }

    async def execute(self, agent_name: str, text: str, command: str) -> Dict:
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        if not await agent.validate_input(text, command):
            raise ValueError("Invalid input data")

        try:
            result = await agent.process(text, command)
            return {
                "result": result,
                "success": True,
                "agent_used": agent.name
            }
        except Exception as e:
            agent.logger.error(f"Processing failed: {e}")
            return {
                "result": f"Error: {str(e)}",
                "success": False,
                "agent_used": agent.name
            }

    def get_available_agents(self) -> list:
        return list(self.agents.keys())