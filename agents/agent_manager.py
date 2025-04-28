"""
Agent manager class to handle agents with the Google Vertex AI SDK.
"""
import os
from typing import List, Dict, Any, Optional, Union
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableConfig
from langchain.schema import SystemMessage, HumanMessage

# Import tools
from .tools.db_tools import DB_TOOLS
from .tools.excel_tools import EXCEL_TOOLS
from .tools.document_tools import DOCUMENT_TOOLS


class AgentManager:
    """Agent manager to handle agents with the Google Vertex AI SDK."""

    def __init__(self, model_name: str = "gemini-1.0-pro"):
        """Initialize the agent manager.
        
        Args:
            model_name: The Google Vertex AI model name to use
        """
        self.model_name = model_name
        self.llm = ChatVertexAI(model_name=model_name)
        
        # Combine all tools
        self.available_tools = {
            "database": DB_TOOLS,
            "excel": EXCEL_TOOLS,
            "document": DOCUMENT_TOOLS,
            "all": DB_TOOLS + EXCEL_TOOLS + DOCUMENT_TOOLS
        }
    
    def create_agent(self, 
                     tools_type: str = "all", 
                     system_message: Optional[str] = None) -> AgentExecutor:
        """Create a new agent with specified tools.
        
        Args:
            tools_type: Type of tools to use ('database', 'excel', 'document', or 'all')
            system_message: Custom system message for the agent
            
        Returns:
            An AgentExecutor instance
        """
        tools = self.available_tools.get(tools_type, self.available_tools["all"])
        
        if system_message is None:
            system_message = self._get_default_system_message(tools_type)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}"),
        ])
        
        agent = (
            {
                "input": RunnablePassthrough()
            }
            | prompt
            | self.llm.bind_tools(tools)
        )
        
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor
    
    def _get_default_system_message(self, tools_type: str) -> str:
        """Get the default system message for the specified tools type.
        
        Args:
            tools_type: Type of tools being used
            
        Returns:
            A system message string
        """
        base_message = (
            "You are a helpful assistant tasked with managing dashboard data. "
            "Users will ask you to process and update information for a dashboard "
            "tracking users, groups, and activities. "
            "Always be polite and helpful. If you're not sure about something, "
            "ask clarifying questions."
        )
        
        tool_specific_messages = {
            "database": (
                "You specialize in interacting with the dashboard database. "
                "You can add, update, and query information about users, groups, and activities."
            ),
            "excel": (
                "You specialize in processing Excel files for the dashboard. "
                "You can extract and import data from Excel files into the dashboard database."
            ),
            "document": (
                "You specialize in processing document files for the dashboard. "
                "You can extract and import data from Word documents into the dashboard database."
            ),
            "all": (
                "You can work with the dashboard database, Excel files, and Word documents. "
                "Use the appropriate tools based on the user's request."
            )
        }
        
        return f"{base_message}\n\n{tool_specific_messages.get(tools_type, tool_specific_messages['all'])}"
    
    async def process_request(self, 
                        request: str, 
                        tools_type: str = "all", 
                        system_message: Optional[str] = None) -> str:
        """Process a user request through an agent.
        
        Args:
            request: The user's request text
            tools_type: Type of tools to use
            system_message: Custom system message for the agent
            
        Returns:
            The agent's response as a string
        """
        agent_executor = self.create_agent(tools_type, system_message)
        response = await agent_executor.ainvoke({"input": request})
        return response["output"]
    
    def run_agent(self, 
                  input_text: str, 
                  tools_type: str = "all", 
                  system_message: Optional[str] = None) -> Dict:
        """Run the agent synchronously.
        
        Args:
            input_text: The input text for the agent
            tools_type: The type of tools to use
            system_message: Custom system message
            
        Returns:
            The agent's response
        """
        agent_executor = self.create_agent(tools_type, system_message)
        response = agent_executor.invoke({"input": input_text})
        return response


# Helper class for handling chat sessions
class ChatSession:
    """Helper class for handling chat sessions with the agent."""
    
    def __init__(self, agent_manager: AgentManager, tools_type: str = "all"):
        """Initialize a chat session.
        
        Args:
            agent_manager: AgentManager instance
            tools_type: Type of tools to use
        """
        self.agent_manager = agent_manager
        self.tools_type = tools_type
        self.history = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat history.
        
        Args:
            role: Role of the message sender ('user' or 'assistant')
            content: Message content
        """
        self.history.append({"role": role, "content": content})
    
    async def send_message(self, message: str) -> str:
        """Send a message to the agent and get a response.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        self.add_message("user", message)
        
        # Create context from history
        context = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.history[-5:]  # Use last 5 messages for context
        ])
        
        # Prepare input with context
        agent_input = f"CHAT HISTORY:\n{context}\n\nUSER'S LATEST MESSAGE: {message}\n\nPlease respond to the user's latest message."
        
        response = await self.agent_manager.process_request(agent_input, self.tools_type)
        self.add_message("assistant", response)
        
        return response


# Factory function to create an agent manager
def create_agent_manager(model_name: str = "gemini-1.0-pro") -> AgentManager:
    """Create and return an agent manager instance.
    
    Args:
        model_name: Vertex AI model name
        
    Returns:
        An initialized AgentManager
    """
    return AgentManager(model_name=model_name)
