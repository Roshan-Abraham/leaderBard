"""
Database manager for handling all database operations.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
from .schema import ALL_TABLES, GET_TOP_USERS, GET_TOP_GROUPS, GET_USER_ACTIVITIES, GET_GROUP_ACTIVITIES
from .schema import GET_USER_PROFILE, GET_GROUP_DETAILS, GET_USER_TIMELINE, GET_GROUP_TIMELINE
from .db_adapter import DatabaseAdapter


class DatabaseManager:
    """Database manager for handling all database operations."""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses DB_PATH environment variable or defaults to 'dashboard.db'
        """
        self.db_path = db_path or os.environ.get('DB_PATH', 'dashboard.db')
        self.db_adapter = DatabaseAdapter()
        self.initialize_db()
    
    def get_connection(self):
        """Get database connection."""
        return self.db_adapter.get_connection()
    
    def initialize_db(self) -> None:
        """Create database tables if they don't exist."""
        for table_query in ALL_TABLES:
            self.db_adapter.execute_query(table_query, fetch_type='none')
    
    # User operations
    def add_user(self, username: str, email: str = None, full_name: str = None, 
                 profile_data: Dict = None) -> int:
        """Add a new user to the database.
        
        Args:
            username: Unique username
            email: User email
            full_name: User's full name
            profile_data: Additional profile information as dictionary
            
        Returns:
            User ID
        """
        profile_json = json.dumps(profile_data) if profile_data else None
        now = datetime.now().isoformat()
        
        query = """
            INSERT INTO users (username, email, full_name, profile_data, last_active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """
        
        if self.db_adapter.db_type != 'postgres':
            query = query.replace('%s', '?')
            self.db_adapter.execute_query(query, (username, email, full_name, profile_json, now), fetch_type='none')
            return self.db_adapter.get_last_insert_id()
        else:
            result = self.db_adapter.execute_query(query, (username, email, full_name, profile_json, now), fetch_type='one')
            return result['id'] if result else None
    
    def update_user_score(self, user_id: int, points: int) -> None:
        """Update a user's score.
        
        Args:
            user_id: User ID
            points: Points to add to user's score
        """
        now = datetime.now().isoformat()
        
        query = """
            UPDATE users 
            SET score = score + %s, last_active = %s
            WHERE id = %s
            """
        
        if self.db_adapter.db_type != 'postgres':
            query = query.replace('%s', '?')
        
        self.db_adapter.execute_query(query, (points, now, user_id), fetch_type='none')
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user details.
        
        Args:
            user_id: User ID
            
        Returns:
            User details dictionary or None if not found
        """
        query = GET_USER_PROFILE
        if self.db_adapter.db_type == 'postgres':
            query = query.replace('?', '%s')
            
        result = self.db_adapter.execute_query(query, (user_id,), fetch_type='one')
        
        if result:
            if result.get('profile_data'):
                result['profile_data'] = json.loads(result['profile_data'])
            return result
        return None
    
    # Group operations
    def add_group(self, name: str, description: str = None) -> int:
        """Add a new group to the database.
        
        Args:
            name: Group name
            description: Group description
            
        Returns:
            Group ID
        """
        query = """
            INSERT INTO groups (name, description)
            VALUES (%s, %s)
            RETURNING id
            """
        
        if self.db_adapter.db_type != 'postgres':
            query = query.replace('%s', '?')
            self.db_adapter.execute_query(query, (name, description), fetch_type='none')
            return self.db_adapter.get_last_insert_id('groups' if self.db_adapter.db_type == 'postgres' else None)
        else:
            result = self.db_adapter.execute_query(query, (name, description), fetch_type='one')
            return result['id'] if result else None
    
    def add_user_to_group(self, user_id: int, group_id: int, role: str = 'member') -> None:
        """Add a user to a group.
        
        Args:
            user_id: User ID
            group_id: Group ID
            role: User role in the group
        """
        # Add user to group
        insert_query = """
            INSERT INTO user_group (user_id, group_id, role)
            VALUES (%s, %s, %s)
            """
        
        # Update group member count
        update_query = """
            UPDATE groups
            SET members_count = members_count + 1
            WHERE id = %s
            """
        
        if self.db_adapter.db_type != 'postgres':
            insert_query = insert_query.replace('%s', '?')
            update_query = update_query.replace('%s', '?')
        
        # Execute queries
        self.db_adapter.execute_query(insert_query, (user_id, group_id, role), fetch_type='none')
        self.db_adapter.execute_query(update_query, (group_id,), fetch_type='none')
    
    def update_group_score(self, group_id: int, points: int) -> None:
        """Update a group's total score.
        
        Args:
            group_id: Group ID
            points: Points to add to group's score
        """
        query = """
            UPDATE groups 
            SET total_score = total_score + %s
            WHERE id = %s
            """
        
        if self.db_adapter.db_type != 'postgres':
            query = query.replace('%s', '?')
        
        self.db_adapter.execute_query(query, (points, group_id), fetch_type='none')
    
    def get_group(self, group_id: int) -> Optional[Dict]:
        """Get group details.
        
        Args:
            group_id: Group ID
            
        Returns:
            Group details dictionary or None if not found
        """
        query = GET_GROUP_DETAILS
        if self.db_adapter.db_type == 'postgres':
            query = query.replace('?', '%s')
        
        result = self.db_adapter.execute_query(query, (group_id,), fetch_type='one')
        
        return result
    
    # Activity operations
    def add_activity(self, user_id: int, activity_type: str, description: str,
                     points: int = 0, group_id: Optional[int] = None,
                     metadata: Dict = None) -> int:
        """Add a new activity.
        
        Args:
            user_id: User ID
            activity_type: Type of activity
            description: Description of the activity
            points: Points earned from the activity
            group_id: Group ID if the activity is associated with a group
            metadata: Additional metadata as dictionary
            
        Returns:
            Activity ID
        """
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Insert activity
        insert_query = """
            INSERT INTO activities (user_id, group_id, activity_type, description, points, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """
        
        # Update user score query
        update_user_query = """
            UPDATE users 
            SET score = score + %s, last_active = CURRENT_TIMESTAMP
            WHERE id = %s
            """
        
        # Update group score query
        update_group_query = """
            UPDATE groups 
            SET total_score = total_score + %s
            WHERE id = %s
            """
        
        # Replace %s with ? for SQLite
        if self.db_adapter.db_type != 'postgres':
            insert_query = insert_query.replace('%s', '?')
            update_user_query = update_user_query.replace('%s', '?')
            update_group_query = update_group_query.replace('%s', '?')
        
        # Execute insert query
        if self.db_adapter.db_type == 'postgres':
            result = self.db_adapter.execute_query(
                insert_query, 
                (user_id, group_id, activity_type, description, points, metadata_json),
                fetch_type='one'
            )
            activity_id = result['id'] if result else None
        else:
            self.db_adapter.execute_query(
                insert_query,
                (user_id, group_id, activity_type, description, points, metadata_json),
                fetch_type='none'
            )
            activity_id = self.db_adapter.get_last_insert_id('activities' if self.db_adapter.db_type == 'postgres' else None)
        
        # Update user and group scores
        if points != 0:
            self.db_adapter.execute_query(update_user_query, (points, user_id), fetch_type='none')
            
            if group_id:
                self.db_adapter.execute_query(update_group_query, (points, group_id), fetch_type='none')
        
        return activity_id
    
    # Dashboard queries
    def get_leaderboard_users(self, limit: int = 10) -> List[Dict]:
        """Get top users for leaderboard.
        
        Args:
            limit: Number of users to return
            
        Returns:
            List of top users with scores
        """
        query = GET_TOP_USERS
        if self.db_adapter.db_type == 'postgres':
            query = query.replace('?', '%s')
        
        return self.db_adapter.execute_query(query, (limit,), fetch_type='all')
    
    def get_leaderboard_groups(self, limit: int = 10) -> List[Dict]:
        """Get top groups for leaderboard.
        
        Args:
            limit: Number of groups to return
            
        Returns:
            List of top groups with scores
        """
        query = GET_TOP_GROUPS
        if self.db_adapter.db_type == 'postgres':
            query = query.replace('?', '%s')
        
        return self.db_adapter.execute_query(query, (limit,), fetch_type='all')
    
    def get_user_activities_timeline(self, user_id: int) -> List[Dict]:
        """Get user activities for timeline.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user activities with timestamps
        """
        query = GET_USER_TIMELINE
        if self.db_adapter.db_type == 'postgres':
            query = query.replace('?', '%s')
        
        return self.db_adapter.execute_query(query, (user_id,), fetch_type='all')
    
    def get_group_activities_timeline(self, group_id: int) -> List[Dict]:
        """Get group activities for timeline.
        
        Args:
            group_id: Group ID
            
        Returns:
            List of group activities with timestamps and usernames
        """
        query = GET_GROUP_TIMELINE
        if self.db_adapter.db_type == 'postgres':
            query = query.replace('?', '%s')
        
        return self.db_adapter.execute_query(query, (group_id,), fetch_type='all')
    
    def get_recent_user_activities(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent user activities.
        
        Args:
            user_id: User ID
            limit: Number of activities to return
            
        Returns:
            List of recent user activities
        """
        query = GET_USER_ACTIVITIES
        if self.db_adapter.db_type == 'postgres':
            query = query.replace('?', '%s')
        
        return self.db_adapter.execute_query(query, (user_id, limit), fetch_type='all')
    
    def get_recent_group_activities(self, group_id: int, limit: int = 10) -> List[Dict]:
        """Get recent group activities.
        
        Args:
            group_id: Group ID
            limit: Number of activities to return
            
        Returns:
            List of recent group activities
        """
        query = GET_GROUP_ACTIVITIES
        if self.db_adapter.db_type == 'postgres':
            query = query.replace('?', '%s')
        
        return self.db_adapter.execute_query(query, (group_id, limit), fetch_type='all')
    
    def search_users(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for users.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching users
        """
        # Search by username, email, or full name
        sql_query = """
            SELECT id, username, email, full_name, score 
            FROM users 
            WHERE username LIKE %s OR email LIKE %s OR full_name LIKE %s 
            ORDER BY score DESC 
            LIMIT %s
            """
            
        if self.db_adapter.db_type != 'postgres':
            sql_query = sql_query.replace('%s', '?')
        
        pattern = f"%{query}%"
        return self.db_adapter.execute_query(
            sql_query, 
            (pattern, pattern, pattern, limit),
            fetch_type='all'
        )
    
    def search_groups(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for groups.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching groups
        """
        # Search by name or description
        sql_query = """
            SELECT id, name, description, total_score, members_count 
            FROM groups 
            WHERE name LIKE %s OR description LIKE %s 
            ORDER BY total_score DESC 
            LIMIT %s
            """
            
        if self.db_adapter.db_type != 'postgres':
            sql_query = sql_query.replace('%s', '?')
        
        pattern = f"%{query}%"
        return self.db_adapter.execute_query(
            sql_query, 
            (pattern, pattern, limit),
            fetch_type='all'
        )
