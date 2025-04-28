"""
Database tools for agents to interact with the SQLite database.
"""
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager()


# User Management Tools
class AddUserInput(BaseModel):
    username: str = Field(..., description="Unique username for the user")
    email: Optional[str] = Field(None, description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    profile_data: Optional[Dict[str, Any]] = Field(None, description="Additional profile information")


class AddUserTool(BaseTool):
    name = "add_user"
    description = "Add a new user to the database"
    args_schema = AddUserInput

    def _run(self, username: str, email: Optional[str] = None, 
             full_name: Optional[str] = None, profile_data: Optional[Dict[str, Any]] = None) -> int:
        """Add a new user to the database."""
        return db_manager.add_user(username, email, full_name, profile_data)


class UpdateUserScoreInput(BaseModel):
    user_id: int = Field(..., description="User ID")
    points: int = Field(..., description="Points to add to user's score")


class UpdateUserScoreTool(BaseTool):
    name = "update_user_score"
    description = "Update a user's score by adding points"
    args_schema = UpdateUserScoreInput

    def _run(self, user_id: int, points: int) -> None:
        """Update a user's score."""
        db_manager.update_user_score(user_id, points)
        return f"Updated score for user {user_id} by adding {points} points"


class GetUserInput(BaseModel):
    user_id: int = Field(..., description="User ID")


class GetUserTool(BaseTool):
    name = "get_user"
    description = "Get user details by ID"
    args_schema = GetUserInput

    def _run(self, user_id: int) -> Dict:
        """Get user details."""
        user = db_manager.get_user(user_id)
        if not user:
            return {"error": f"User with ID {user_id} not found"}
        return user


class SearchUsersInput(BaseModel):
    query: str = Field(..., description="Search query for username, email, or full name")
    limit: int = Field(10, description="Maximum number of results to return")


class SearchUsersTool(BaseTool):
    name = "search_users"
    description = "Search for users by username, email, or full name"
    args_schema = SearchUsersInput

    def _run(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for users."""
        return db_manager.search_users(query, limit)


# Group Management Tools
class AddGroupInput(BaseModel):
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")


class AddGroupTool(BaseTool):
    name = "add_group"
    description = "Add a new group to the database"
    args_schema = AddGroupInput

    def _run(self, name: str, description: Optional[str] = None) -> int:
        """Add a new group to the database."""
        return db_manager.add_group(name, description)


class AddUserToGroupInput(BaseModel):
    user_id: int = Field(..., description="User ID")
    group_id: int = Field(..., description="Group ID")
    role: str = Field("member", description="User's role in the group")


class AddUserToGroupTool(BaseTool):
    name = "add_user_to_group"
    description = "Add a user to a group"
    args_schema = AddUserToGroupInput

    def _run(self, user_id: int, group_id: int, role: str = "member") -> None:
        """Add a user to a group."""
        db_manager.add_user_to_group(user_id, group_id, role)
        return f"Added user {user_id} to group {group_id} with role '{role}'"


class GetGroupInput(BaseModel):
    group_id: int = Field(..., description="Group ID")


class GetGroupTool(BaseTool):
    name = "get_group"
    description = "Get group details by ID"
    args_schema = GetGroupInput

    def _run(self, group_id: int) -> Dict:
        """Get group details."""
        group = db_manager.get_group(group_id)
        if not group:
            return {"error": f"Group with ID {group_id} not found"}
        return group


class SearchGroupsInput(BaseModel):
    query: str = Field(..., description="Search query for group name or description")
    limit: int = Field(10, description="Maximum number of results to return")


class SearchGroupsTool(BaseTool):
    name = "search_groups"
    description = "Search for groups by name or description"
    args_schema = SearchGroupsInput

    def _run(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for groups."""
        return db_manager.search_groups(query, limit)


# Activity Management Tools
class AddActivityInput(BaseModel):
    user_id: int = Field(..., description="User ID")
    activity_type: str = Field(..., description="Type of activity")
    description: str = Field(..., description="Description of the activity")
    points: int = Field(0, description="Points earned from the activity")
    group_id: Optional[int] = Field(None, description="Group ID if the activity is associated with a group")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AddActivityTool(BaseTool):
    name = "add_activity"
    description = "Add a new activity for a user and optionally a group"
    args_schema = AddActivityInput

    def _run(self, user_id: int, activity_type: str, description: str,
             points: int = 0, group_id: Optional[int] = None,
             metadata: Optional[Dict[str, Any]] = None) -> int:
        """Add a new activity."""
        return db_manager.add_activity(user_id, activity_type, description, points, group_id, metadata)


# Dashboard Query Tools
class GetLeaderboardUsersInput(BaseModel):
    limit: int = Field(10, description="Number of users to return")


class GetLeaderboardUsersTool(BaseTool):
    name = "get_leaderboard_users"
    description = "Get top users for leaderboard"
    args_schema = GetLeaderboardUsersInput

    def _run(self, limit: int = 10) -> List[Dict]:
        """Get top users for leaderboard."""
        return db_manager.get_leaderboard_users(limit)


class GetLeaderboardGroupsInput(BaseModel):
    limit: int = Field(10, description="Number of groups to return")


class GetLeaderboardGroupsTool(BaseTool):
    name = "get_leaderboard_groups"
    description = "Get top groups for leaderboard"
    args_schema = GetLeaderboardGroupsInput

    def _run(self, limit: int = 10) -> List[Dict]:
        """Get top groups for leaderboard."""
        return db_manager.get_leaderboard_groups(limit)


class GetUserActivitiesInput(BaseModel):
    user_id: int = Field(..., description="User ID")
    limit: int = Field(10, description="Number of activities to return")


class GetUserActivitiesTool(BaseTool):
    name = "get_user_activities"
    description = "Get recent activities for a user"
    args_schema = GetUserActivitiesInput

    def _run(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent user activities."""
        return db_manager.get_recent_user_activities(user_id, limit)


class GetGroupActivitiesInput(BaseModel):
    group_id: int = Field(..., description="Group ID")
    limit: int = Field(10, description="Number of activities to return")


class GetGroupActivitiesTool(BaseTool):
    name = "get_group_activities"
    description = "Get recent activities for a group"
    args_schema = GetGroupActivitiesInput

    def _run(self, group_id: int, limit: int = 10) -> List[Dict]:
        """Get recent group activities."""
        return db_manager.get_recent_group_activities(group_id, limit)


class GetUserTimelineInput(BaseModel):
    user_id: int = Field(..., description="User ID")


class GetUserTimelineTool(BaseTool):
    name = "get_user_timeline"
    description = "Get activity timeline for a user"
    args_schema = GetUserTimelineInput

    def _run(self, user_id: int) -> List[Dict]:
        """Get user activities timeline."""
        return db_manager.get_user_activities_timeline(user_id)


class GetGroupTimelineInput(BaseModel):
    group_id: int = Field(..., description="Group ID")


class GetGroupTimelineTool(BaseTool):
    name = "get_group_timeline"
    description = "Get activity timeline for a group"
    args_schema = GetGroupTimelineInput

    def _run(self, group_id: int) -> List[Dict]:
        """Get group activities timeline."""
        return db_manager.get_group_activities_timeline(group_id)


# List of all database tools
DB_TOOLS = [
    AddUserTool(),
    UpdateUserScoreTool(),
    GetUserTool(),
    SearchUsersTool(),
    AddGroupTool(),
    AddUserToGroupTool(),
    GetGroupTool(),
    SearchGroupsTool(),
    AddActivityTool(),
    GetLeaderboardUsersTool(),
    GetLeaderboardGroupsTool(),
    GetUserActivitiesTool(),
    GetGroupActivitiesTool(),
    GetUserTimelineTool(),
    GetGroupTimelineTool()
]
