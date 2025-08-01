from typing import Dict
from ..agents.base_agent import BaseAgent
from ..agents.text_editor_agent import TextEditorAgent
from ..agents.summarizer_agent import SummarizerAgent
from ..agents.transformer_agent import TransformerAgent
from .langgraph_workflow import LangGraphWorkflow

class AgentManager:
    def __init__(self, use_langgraph: bool = True):
        self.use_langgraph = use_langgraph
        self.agents: Dict[str, BaseAgent] = {
            "editor": TextEditorAgent("editor"),
            "summarizer": SummarizerAgent("summarizer"),
            "transformer": TransformerAgent("transformer")
        }
        if use_langgraph:
            self.workflow = LangGraphWorkflow()

    async def execute(self, agent_name: str, text: str, command: str) -> Dict:
        # Use LangGraph workflow if enabled
        if self.use_langgraph:
            return await self.workflow.execute(text, command)
        
        # Fall back to legacy agent execution
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        if not await agent.validate_input(text, command):
            raise ValueError("Invalid input data")

        try:
            agent_result = await agent.process(text, command)
            return {
                "result": agent_result["result"],
                "success": True,
                "agent_used": agent.name,
                "agent_info": agent_result["agent_info"]
            }
        except Exception as e:
            agent.logger.error(f"Processing failed: {e}")
            return {
                "result": f"Error: {str(e)}",
                "success": False,
                "agent_used": agent.name,
                "agent_info": {
                    "model": "error",
                    "processing_time_ms": 0,
                    "tokens_used": None,
                    "confidence_score": 0.0,
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                }
            }

    def get_available_agents(self) -> list:
        return list(self.agents.keys())