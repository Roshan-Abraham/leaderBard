"""
Detail cards component for displaying user and group profiles in the Streamlit dashboard.
"""
import streamlit as st
import pandas as pd
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import DatabaseManager


def render_user_card(db_manager: DatabaseManager, user_id: int):
    """Render a detailed profile card for a user.
    
    Args:
        db_manager: Database manager instance
        user_id: User ID
    """
    # Get user information
    user = db_manager.get_user(user_id)
    if not user:
        st.error(f"User with ID {user_id} not found.")
        return
    
    # Get recent activities
    recent_activities = db_manager.get_recent_user_activities(user_id, limit=5)
    
    # Container for card
    with st.container():
        # Header with username and score
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(user['username'])
            if user.get('full_name'):
                st.subheader(user['full_name'])
        with col2:
            st.metric(label="Score", value=user['score'])
        
        st.divider()
        
        # User details
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("User Details")
            
            details = [
                ("Email", user.get('email', 'Not specified')),
                ("Joined", format_datetime(user.get('created_at'))),
                ("Last Active", format_datetime(user.get('last_active')))
            ]
            
            for label, value in details:
                st.write(f"**{label}:** {value}")
            
            # Additional profile data
            if user.get('profile_data'):
                st.subheader("Profile Data")
                profile_data = user['profile_data']
                if isinstance(profile_data, str):
                    try:
                        profile_data = json.loads(profile_data)
                    except:
                        pass
                
                if isinstance(profile_data, dict):
                    for key, value in profile_data.items():
                        st.write(f"**{key.capitalize()}:** {value}")
        
        with col2:
            st.subheader("Recent Activities")
            
            if not recent_activities:
                st.info("No recent activities.")
            else:
                for activity in recent_activities:
                    with st.container():
                        activity_date = format_datetime(activity.get('timestamp'))
                        st.caption(f"{activity_date} | {activity['activity_type']}")
                        st.write(activity['description'])
                        if activity.get('points', 0) > 0:
                            st.write(f"**+{activity['points']} points**")
                        st.divider()


def render_group_card(db_manager: DatabaseManager, group_id: int):
    """Render a detailed profile card for a group.
    
    Args:
        db_manager: Database manager instance
        group_id: Group ID
    """
    # Get group information
    group = db_manager.get_group(group_id)
    if not group:
        st.error(f"Group with ID {group_id} not found.")
        return
    
    # Get recent activities
    recent_activities = db_manager.get_recent_group_activities(group_id, limit=5)
    
    # Get group members
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT u.id, u.username, u.score, ug.role
        FROM users u
        JOIN user_group ug ON u.id = ug.user_id
        WHERE ug.group_id = ?
        ORDER BY u.score DESC
        LIMIT 10
        """,
        (group_id,)
    )
    
    members = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Container for card
    with st.container():
        # Header with group name and score
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(group['name'])
            if group.get('description'):
                st.write(group['description'])
        with col2:
            st.metric(label="Total Score", value=group['total_score'])
        
        st.divider()
        
        # Group details and members
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Group Details")
            
            details = [
                ("Created", format_datetime(group.get('created_at'))),
                ("Members", group.get('members_count', 0)),
                ("Activities", group.get('activity_count', 0))
            ]
            
            for label, value in details:
                st.write(f"**{label}:** {value}")
            
            # Members list
            st.subheader("Top Members")
            
            if not members:
                st.info("No members in this group.")
            else:
                for i, member in enumerate(members):
                    col1a, col2a = st.columns([3, 1])
                    with col1a:
                        st.write(f"**{i+1}. {member['username']}**")
                        st.caption(f"Role: {member['role'].capitalize()}")
                    with col2a:
                        st.write(f"**{member['score']}** pts")
                    
                if len(members) >= 10:
                    st.caption("Showing top 10 members only")
        
        with col2:
            st.subheader("Recent Activities")
            
            if not recent_activities:
                st.info("No recent activities.")
            else:
                for activity in recent_activities:
                    with st.container():
                        activity_date = format_datetime(activity.get('timestamp'))
                        st.caption(f"{activity_date} | {activity['username']}")
                        st.write(f"**{activity['activity_type']}:** {activity['description']}")
                        if activity.get('points', 0) > 0:
                            st.write(f"**+{activity['points']} points**")
                        st.divider()


def render_user_selection_card(db_manager: DatabaseManager):
    """Render a card with searchable user selection.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        Selected user ID or None
    """
    st.subheader("Find User")
    
    # Search options
    search_query = st.text_input("Search by username, email or name", key="user_search")
    
    selected_user_id = None
    
    if search_query:
        # Search for users
        users = db_manager.search_users(search_query, limit=10)
        
        if not users:
            st.info(f"No users found matching '{search_query}'")
        else:
            st.success(f"Found {len(users)} users matching '{search_query}'")
            
            # Create selection options
            user_options = {f"{user['username']} ({user['score']} pts)": user['id'] for user in users}
            
            selected_user = st.selectbox(
                "Select a user",
                options=list(user_options.keys()),
                key="user_select"
            )
            
            if selected_user:
                selected_user_id = user_options[selected_user]
    
    return selected_user_id


def render_group_selection_card(db_manager: DatabaseManager):
    """Render a card with searchable group selection.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        Selected group ID or None
    """
    st.subheader("Find Group")
    
    # Search options
    search_query = st.text_input("Search by group name or description", key="group_search")
    
    selected_group_id = None
    
    if search_query:
        # Search for groups
        groups = db_manager.search_groups(search_query, limit=10)
        
        if not groups:
            st.info(f"No groups found matching '{search_query}'")
        else:
            st.success(f"Found {len(groups)} groups matching '{search_query}'")
            
            # Create selection options
            group_options = {f"{group['name']} ({group['total_score']} pts)": group['id'] for group in groups}
            
            selected_group = st.selectbox(
                "Select a group",
                options=list(group_options.keys()),
                key="group_select"
            )
            
            if selected_group:
                selected_group_id = group_options[selected_group]
    
    return selected_group_id


def format_datetime(dt_str: Optional[str]) -> str:
    """Format a datetime string for display.
    
    Args:
        dt_str: Datetime string
        
    Returns:
        Formatted datetime string
    """
    if not dt_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return dt_str
