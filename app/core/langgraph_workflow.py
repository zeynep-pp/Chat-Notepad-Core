from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from ..agents.text_editor_agent import TextEditorAgent
from ..agents.summarizer_agent import SummarizerAgent
import logging

logger = logging.getLogger(__name__)

class WorkflowState(TypedDict):
    text: str
    command: str
    result: str
    agent_used: str
    agent_info: Dict[str, Any]
    success: bool
    error: Optional[str]

class LangGraphWorkflow:
    def __init__(self):
        self.text_editor = TextEditorAgent("editor")
        self.summarizer = SummarizerAgent("summarizer")
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("router", self._route_request)
        workflow.add_node("text_editor", self._process_text_editor)
        workflow.add_node("summarizer", self._process_summarizer)
        workflow.add_node("error_handler", self._handle_error)
        
        # Add edges
        workflow.add_edge(START, "router")
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "editor": "text_editor",
                "summarizer": "summarizer",
                "error": "error_handler"
            }
        )
        workflow.add_edge("text_editor", END)
        workflow.add_edge("summarizer", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    async def _route_request(self, state: WorkflowState) -> WorkflowState:
        """Route request to appropriate agent based on command"""
        logger.info(f"Routing request: {state['command']}")
        return state
    
    def _route_decision(self, state: WorkflowState) -> str:
        """Decide which agent to use based on command"""
        command_lower = state["command"].lower()
        
        if any(keyword in command_lower for keyword in ["summarize", "summary", "brief"]):
            return "summarizer"
        elif any(keyword in command_lower for keyword in ["edit", "replace", "remove", "uppercase", "lowercase", "capitalize"]):
            return "editor"
        else:
            # Default to editor for general text processing
            return "editor"
    
    async def _process_text_editor(self, state: WorkflowState) -> WorkflowState:
        """Process text using text editor agent"""
        try:
            if not await self.text_editor.validate_input(state["text"], state["command"]):
                raise ValueError("Invalid input for text editor")
            
            result = await self.text_editor.process(state["text"], state["command"])
            
            return {
                **state,
                "result": result["result"],
                "agent_used": self.text_editor.name,
                "agent_info": result["agent_info"],
                "success": True,
                "error": None
            }
        except Exception as e:
            logger.error(f"Text editor processing failed: {e}")
            return {
                **state,
                "result": f"Error: {str(e)}",
                "agent_used": self.text_editor.name,
                "success": False,
                "error": str(e)
            }
    
    async def _process_summarizer(self, state: WorkflowState) -> WorkflowState:
        """Process text using summarizer agent"""
        try:
            if not await self.summarizer.validate_input(state["text"], state["command"]):
                raise ValueError("Invalid input for summarizer")
            
            result = await self.summarizer.process(state["text"], state["command"])
            
            return {
                **state,
                "result": result["result"],
                "agent_used": self.summarizer.name,
                "agent_info": result["agent_info"],
                "success": True,
                "error": None
            }
        except Exception as e:
            logger.error(f"Summarizer processing failed: {e}")
            return {
                **state,
                "result": f"Error: {str(e)}",
                "agent_used": self.summarizer.name,
                "success": False,
                "error": str(e)
            }
    
    async def _handle_error(self, state: WorkflowState) -> WorkflowState:
        """Handle errors in workflow"""
        logger.error(f"Workflow error: {state.get('error', 'Unknown error')}")
        return {
            **state,
            "result": "Error: Unable to process request",
            "agent_used": "error_handler",
            "success": False
        }
    
    async def execute(self, text: str, command: str) -> Dict[str, Any]:
        """Execute the workflow with given text and command"""
        initial_state = WorkflowState(
            text=text,
            command=command,
            result="",
            agent_used="",
            agent_info={},
            success=False,
            error=None
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            return {
                "result": final_state["result"],
                "success": final_state["success"],
                "agent_used": final_state["agent_used"],
                "agent_info": final_state.get("agent_info", {})
            }
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "result": f"Workflow error: {str(e)}",
                "success": False,
                "agent_used": "workflow_error",
                "agent_info": {}
            }