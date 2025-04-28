"""
Main dashboard agent using Google ADK framework.
"""
from google.adk.agents import LlmAgent

from .tools.utils import load_instruction_from_file
from .tools.db_tools import db_agent
from .tools.excel_tools import excel_agent
from .tools.document_tools import document_agent

# Create the main dashboard agent that can use all specialized agents
dashboard_agent = LlmAgent(
    name="DashboardManager",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("dashboard_instructions.txt"),
    description="Main agent that manages dashboard data through database operations, Excel file processing, and document file processing.",
    sub_agents=[db_agent, excel_agent, document_agent],
)

# Root agent for the runner
root_agent = dashboard_agent