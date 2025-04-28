"""
Runner for the dashboard agent.
"""
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from typing import Dict, Any, List, Optional

from .dashboard_agent import root_agent

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Constants
APP_NAME = "dashboard_manager"
USER_ID = "user123"
SESSION_ID = "session456"


class AgentManager:
    """Manages interactions with the dashboard agent."""
    
    def __init__(self, app_name: str = APP_NAME, user_id: str = USER_ID, session_id: str = SESSION_ID):
        """
        Initialize the agent manager.
        
        Args:
            app_name: The name of the application
            user_id: The user ID
            session_id: The session ID
        """
        self.app_name = app_name
        self.user_id = user_id
        self.session_id = session_id
        
        # Initialize session service and runner
        self.session_service = InMemorySessionService()
        self.session = self.session_service.create_session(
            app_name=self.app_name, 
            user_id=self.user_id, 
            session_id=self.session_id
        )
        self.runner = Runner(
            agent=root_agent, 
            app_name=self.app_name, 
            session_service=self.session_service
        )
    
    def run_agent(self, query: str) -> Dict[str, Any]:
        """
        Send a query to the dashboard agent and get a response.
        
        Args:
            query: The user's query
            
        Returns:
            Dictionary containing the agent's response and any additional metadata
        """
        try:
            content = types.Content(role="user", parts=[types.Part(text=query)])
            events = self.runner.run(
                user_id=self.user_id, 
                session_id=self.session_id, 
                new_message=content
            )

            response_text = ""
            for event in events:
                if event.is_final_response():
                    response_text = event.content.parts[0].text
                    break
            
            return {
                "status": "success",
                "output": response_text,
                "metadata": {
                    "timestamp": None,  # Could add timestamp if needed
                    "query_type": self._detect_query_type(query)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "output": f"Error processing request: {str(e)}",
                "metadata": {
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            }
    
    def _detect_query_type(self, query: str) -> str:
        """
        Detect the type of query being made.
        
        Args:
            query: The user's query
            
        Returns:
            The detected query type
        """
        query = query.lower()
        
        if any(word in query for word in ["excel", "xlsx", "spreadsheet"]):
            return "excel_processing"
        elif any(word in query for word in ["doc", "word", "document", "docx"]):
            return "document_processing"
        elif any(word in query for word in ["show", "display", "get", "leaderboard", "rank"]):
            return "data_retrieval"
        elif any(word in query for word in ["add", "update", "insert", "create", "modify"]):
            return "data_modification"
        else:
            return "general_query"


def create_agent_manager(app_name: str = APP_NAME, 
                         user_id: str = USER_ID, 
                         session_id: str = SESSION_ID) -> AgentManager:
    """
    Create and return an instance of the AgentManager.
    
    Args:
        app_name: The name of the application
        user_id: The user ID
        session_id: The session ID
        
    Returns:
        An initialized AgentManager
    """
    return AgentManager(app_name, user_id, session_id)


if __name__ == "__main__":
    # Example usage
    agent_manager = create_agent_manager()
    response = agent_manager.run_agent("Show me the top 5 users on the leaderboard")
    print(response["output"])
    
    # Example with Excel file
    # response = agent_manager.run_agent("Import users from users.xlsx with username column 'username', email column 'email', and full name column 'name'")
    # print(response["output"])
    
    # Example with document file
    # response = agent_manager.run_agent("Extract user information from team_report.docx")
    # print(response["output"])