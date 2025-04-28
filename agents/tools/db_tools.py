"""
Database tools for agents using Google ADK framework.
"""
from typing import List, Dict, Any, Optional
import sys
import os
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import DatabaseManager
from .utils import load_instruction_from_file

# Initialize database manager
db_manager = DatabaseManager()

# User Management Tools
def add_user(username: str, email: Optional[str] = None, 
             full_name: Optional[str] = None, profile_data: Optional[Dict[str, Any]] = None) -> int:
    """Add a new user to the database.
    
    Args:
        username: Unique username for the user
        email: User's email address
        full_name: User's full name
        profile_data: Additional profile information
        
    Returns:
        User ID
    """
    return db_manager.add_user(username, email, full_name, profile_data)

def update_user_score(user_id: int, points: int) -> str:
    """Update a user's score by adding points.
    
    Args:
        user_id: User ID
        points: Points to add to user's score
        
    Returns:
        Confirmation message
    """
    db_manager.update_user_score(user_id, points)
    return f"Updated score for user {user_id} by adding {points} points"

def get_user(user_id: int) -> Dict:
    """Get user details by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User details
    """
    user = db_manager.get_user(user_id)
    if not user:
        return {"error": f"User with ID {user_id} not found"}
    return user

def search_users(query: str, limit: int = 10) -> List[Dict]:
    """Search for users by username, email, or full name.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        List of matching users
    """
    return db_manager.search_users(query, limit)

# Group Management Tools
def add_group(name: str, description: Optional[str] = None) -> int:
    """Add a new group to the database.
    
    Args:
        name: Group name
        description: Group description
        
    Returns:
        Group ID
    """
    return db_manager.add_group(name, description)

def add_user_to_group(user_id: int, group_id: int, role: str = "member") -> str:
    """Add a user to a group.
    
    Args:
        user_id: User ID
        group_id: Group ID
        role: User's role in the group
        
    Returns:
        Confirmation message
    """
    db_manager.add_user_to_group(user_id, group_id, role)
    return f"Added user {user_id} to group {group_id} with role '{role}'"

def get_group(group_id: int) -> Dict:
    """Get group details by ID.
    
    Args:
        group_id: Group ID
        
    Returns:
        Group details
    """
    group = db_manager.get_group(group_id)
    if not group:
        return {"error": f"Group with ID {group_id} not found"}
    return group

def search_groups(query: str, limit: int = 10) -> List[Dict]:
    """Search for groups by name or description.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        List of matching groups
    """
    return db_manager.search_groups(query, limit)

# Activity Management Tools
def add_activity(user_id: int, activity_type: str, description: str,
                 points: int = 0, group_id: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> int:
    """Add a new activity for a user and optionally a group.
    
    Args:
        user_id: User ID
        activity_type: Type of activity
        description: Description of the activity
        points: Points earned from the activity
        group_id: Group ID if the activity is associated with a group
        metadata: Additional metadata
        
    Returns:
        Activity ID
    """
    return db_manager.add_activity(user_id, activity_type, description, points, group_id, metadata)

# Dashboard Query Tools
def get_leaderboard_users(limit: int = 10) -> List[Dict]:
    """Get top users for leaderboard.
    
    Args:
        limit: Number of users to return
        
    Returns:
        List of top users
    """
    return db_manager.get_leaderboard_users(limit)

def get_leaderboard_groups(limit: int = 10) -> List[Dict]:
    """Get top groups for leaderboard.
    
    Args:
        limit: Number of groups to return
        
    Returns:
        List of top groups
    """
    return db_manager.get_leaderboard_groups(limit)

def get_user_activities(user_id: int, limit: int = 10) -> List[Dict]:
    """Get recent activities for a user.
    
    Args:
        user_id: User ID
        limit: Number of activities to return
        
    Returns:
        List of recent user activities
    """
    return db_manager.get_recent_user_activities(user_id, limit)

def get_group_activities(group_id: int, limit: int = 10) -> List[Dict]:
    """Get recent activities for a group.
    
    Args:
        group_id: Group ID
        limit: Number of activities to return
        
    Returns:
        List of recent group activities
    """
    return db_manager.get_recent_group_activities(group_id, limit)

def get_user_timeline(user_id: int) -> List[Dict]:
    """Get activity timeline for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        User activities timeline
    """
    return db_manager.get_user_activities_timeline(user_id)

def get_group_timeline(group_id: int) -> List[Dict]:
    """Get activity timeline for a group.
    
    Args:
        group_id: Group ID
        
    Returns:
        Group activities timeline
    """
    return db_manager.get_group_activities_timeline(group_id)

# Create function tools for ADK
DB_TOOLS = [
    FunctionTool(add_user, "add_user", "Add a new user to the database"),
    FunctionTool(update_user_score, "update_user_score", "Update a user's score by adding points"),
    FunctionTool(get_user, "get_user", "Get user details by ID"),
    FunctionTool(search_users, "search_users", "Search for users by username, email, or full name"),
    FunctionTool(add_group, "add_group", "Add a new group to the database"),
    FunctionTool(add_user_to_group, "add_user_to_group", "Add a user to a group"),
    FunctionTool(get_group, "get_group", "Get group details by ID"),
    FunctionTool(search_groups, "search_groups", "Search for groups by name or description"),
    FunctionTool(add_activity, "add_activity", "Add a new activity for a user and optionally a group"),
    FunctionTool(get_leaderboard_users, "get_leaderboard_users", "Get top users for leaderboard"),
    FunctionTool(get_leaderboard_groups, "get_leaderboard_groups", "Get top groups for leaderboard"),
    FunctionTool(get_user_activities, "get_user_activities", "Get recent activities for a user"),
    FunctionTool(get_group_activities, "get_group_activities", "Get recent activities for a group"),
    FunctionTool(get_user_timeline, "get_user_timeline", "Get activity timeline for a user"),
    FunctionTool(get_group_timeline, "get_group_timeline", "Get activity timeline for a group")
]

# Create the database agent
db_agent = LlmAgent(
    name="DatabaseAgent",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("db_agent_instruction.txt"),
    description="Specialized agent for database operations on the dashboard system",
    tools=DB_TOOLS,
    output_key="db_result"
)