from typing import Dict, Any

class HumanInTheLoopNode:
    """
    Interrupts the LangGraph execution flow to require human approval 
    before publishing simulated agency content.
    """
    
    @staticmethod
    def run(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pauses execution and flags the state as requiring human review.
        The FastAPI backend will expose an interactive dashboard endpoint 
        allowing the creative director to swipe left or right on this state.
        """
        print("[Human-in-the-Loop] Execution paused. Awaiting human approval.")
        
        # We mutate the state to reflect that it is pending review.
        # In a real LangGraph setup with checkpointers, this node would literally
        # interrupt the graph using `Interrupt()` or waiting for state updates.
        return {
            "status": "pending_human_review",
            "dashboard_url": f"/api/v1/dashboard/review/{state.get('campaign_id', 'unknown')}"
        }
