"""
Leaderboard component for the Streamlit dashboard.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import DatabaseManager


def render_user_leaderboard(db_manager: DatabaseManager, limit: int = 10):
    """Render the user leaderboard component.
    
    Args:
        db_manager: Database manager instance
        limit: Number of top users to display
    """
    st.subheader("Top Users")
    
    # Get top users from database
    top_users = db_manager.get_leaderboard_users(limit)
    
    if not top_users:
        st.info("No user data available yet.")
        return
    
    # Create dataframe for display
    df = pd.DataFrame(top_users)
    
    # Add rank column
    df['rank'] = range(1, len(df) + 1)
    
    # Reorder columns
    df = df[['rank', 'username', 'score']]
    
    # Display as table with formatting
    st.dataframe(
        df,
        column_config={
            "rank": st.column_config.TextColumn("Rank", help="Position on the leaderboard"),
            "username": st.column_config.TextColumn("User", help="Username"),
            "score": st.column_config.NumberColumn("Score", help="Total points earned", format="%d pts")
        },
        hide_index=True,
        use_container_width=True
    )


def render_group_leaderboard(db_manager: DatabaseManager, limit: int = 10):
    """Render the group leaderboard component.
    
    Args:
        db_manager: Database manager instance
        limit: Number of top groups to display
    """
    st.subheader("Top Groups")
    
    # Get top groups from database
    top_groups = db_manager.get_leaderboard_groups(limit)
    
    if not top_groups:
        st.info("No group data available yet.")
        return
    
    # Create dataframe for display
    df = pd.DataFrame(top_groups)
    
    # Add rank column
    df['rank'] = range(1, len(df) + 1)
    
    # Reorder columns
    df = df[['rank', 'name', 'total_score']]
    
    # Rename column for display
    df = df.rename(columns={'total_score': 'score'})
    
    # Display as table with formatting
    st.dataframe(
        df,
        column_config={
            "rank": st.column_config.TextColumn("Rank", help="Position on the leaderboard"),
            "name": st.column_config.TextColumn("Group", help="Group name"),
            "score": st.column_config.NumberColumn("Score", help="Total points earned", format="%d pts")
        },
        hide_index=True,
        use_container_width=True
    )


def render_combined_leaderboard(db_manager: DatabaseManager, limit: int = 10):
    """Render both user and group leaderboards side by side.
    
    Args:
        db_manager: Database manager instance
        limit: Number of top entries to display
    """
    col1, col2 = st.columns(2)
    
    with col1:
        render_user_leaderboard(db_manager, limit)
    
    with col2:
        render_group_leaderboard(db_manager, limit)
