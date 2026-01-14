"""Voice AI Assistant for Employee Directory."""

import json
import logging
from livekit import rtc
from livekit.agents import Agent, function_tool, RunContext
from .employee_data import get_employee_data
from .fuzzy_search import FuzzyNameMatcher

logger = logging.getLogger("agent.assistant")


class Assistant(Agent):
    """Employee directory voice assistant with fuzzy name search."""
    
    def __init__(self, room: rtc.Room) -> None:
        self.room = room
        
        employee_data = get_employee_data()
        self._fuzzy_matcher = FuzzyNameMatcher(employee_data.employees)
        
        all_names = employee_data.get_names()
        sample_names = ", ".join(all_names[:5]) + f"... ({len(all_names)} total)"
        
        super().__init__(
            instructions=f"""You are a helpful voice AI assistant for an employee directory.
Be concise and conversational. No emojis or special formatting.

RULES:
- ALWAYS use get_employee_directory tool for employee lookups
- ONLY share: name, email, role, department
- NEVER reveal salary or confidential info
- If not found, share the suggested similar names

Directory has {len(all_names)} employees: {sample_names}""",
        )
        logger.info(f"Assistant ready with {len(all_names)} employees")

    @function_tool
    async def get_employee_directory(self, employee_name: str, context: RunContext) -> dict:
        """
        Look up employee details by name.
        
        Args:
            employee_name: Full or partial name to search
        """
        logger.info(f"Looking up: {employee_name}")
        result = self._fuzzy_matcher.search(employee_name, top_k=3)
        
        if result["found"]:
            return {
                "status": "found",
                "employee": result["employee"],
                "message": result["message"],
            }
        elif result["suggestions"]:
            return {
                "status": "not_found",
                "suggestions": [
                    {"name": s["employee"]["name"], "department": s["employee"]["department"]}
                    for s in result["suggestions"]
                ],
                "message": result["message"],
            }
        return {"status": "not_found", "suggestions": [], "message": result["message"]}

    async def send_metrics_to_frontend(self, metrics_type: str, metrics_data: dict) -> None:
        """Send metrics to frontend via data channel."""
        try:
            payload = json.dumps({
                "type": "metrics",
                "metrics_type": metrics_type,
                "data": metrics_data,
            })
            await self.room.local_participant.publish_data(payload.encode(), topic="agent_metrics")
        except Exception as e:
            logger.error(f"Error sending metrics: {e}")
