"""
Graphs and visualization components for the Streamlit dashboard.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import DatabaseManager


def render_user_score_chart(db_manager: DatabaseManager, limit: int = 10):
    """Render horizontal bar chart of top user scores.
    
    Args:
        db_manager: Database manager instance
        limit: Number of top users to display
    """
    # Get top users from database
    top_users = db_manager.get_leaderboard_users(limit)
    
    if not top_users:
        st.info("No user data available for chart.")
        return
    
    # Create dataframe for display
    df = pd.DataFrame(top_users)
    
    # Sort by score descending
    df = df.sort_values('score', ascending=True)
    
    # Create horizontal bar chart
    fig = px.bar(
        df,
        y='username',
        x='score',
        orientation='h',
        title=f'Top {len(df)} Users by Score',
        labels={'username': 'User', 'score': 'Score'},
        color='score',
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title="Score",
        yaxis_title="",
        coloraxis_showscale=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_group_score_chart(db_manager: DatabaseManager, limit: int = 10):
    """Render horizontal bar chart of top group scores.
    
    Args:
        db_manager: Database manager instance
        limit: Number of top groups to display
    """
    # Get top groups from database
    top_groups = db_manager.get_leaderboard_groups(limit)
    
    if not top_groups:
        st.info("No group data available for chart.")
        return
    
    # Create dataframe for display
    df = pd.DataFrame(top_groups)
    
    # Sort by score descending
    df = df.sort_values('total_score', ascending=True)
    
    # Create horizontal bar chart
    fig = px.bar(
        df,
        y='name',
        x='total_score',
        orientation='h',
        title=f'Top {len(df)} Groups by Score',
        labels={'name': 'Group', 'total_score': 'Score'},
        color='total_score',
        color_continuous_scale='Teal'
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title="Score",
        yaxis_title="",
        coloraxis_showscale=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_activity_type_pie_chart(db_manager: DatabaseManager, user_id: Optional[int] = None, 
                                 group_id: Optional[int] = None):
    """Render pie chart of activity types.
    
    Args:
        db_manager: Database manager instance
        user_id: Optional user ID to filter activities
        group_id: Optional group ID to filter activities
    """
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute(
            """
            SELECT activity_type, COUNT(*) as count
            FROM activities
            WHERE user_id = ?
            GROUP BY activity_type
            ORDER BY count DESC
            """,
            (user_id,)
        )
        title = "Activity Types Distribution for User"
    elif group_id:
        cursor.execute(
            """
            SELECT activity_type, COUNT(*) as count
            FROM activities
            WHERE group_id = ?
            GROUP BY activity_type
            ORDER BY count DESC
            """,
            (group_id,)
        )
        title = "Activity Types Distribution for Group"
    else:
        cursor.execute(
            """
            SELECT activity_type, COUNT(*) as count
            FROM activities
            GROUP BY activity_type
            ORDER BY count DESC
            """
        )
        title = "Overall Activity Types Distribution"
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        st.info("No activity data available for pie chart.")
        return
    
    # Create dataframe for display
    df = pd.DataFrame([dict(row) for row in results])
    
    # Create pie chart
    fig = px.pie(
        df,
        values='count',
        names='activity_type',
        title=title,
        hole=0.4
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_points_over_time_chart(db_manager: DatabaseManager, user_id: Optional[int] = None, 
                                 group_id: Optional[int] = None, days: int = 30):
    """Render line chart of points earned over time.
    
    Args:
        db_manager: Database manager instance
        user_id: Optional user ID to filter activities
        group_id: Optional group ID to filter activities
        days: Number of days to include in the chart
    """
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    if user_id:
        cursor.execute(
            """
            SELECT DATE(timestamp) as date, SUM(points) as total_points
            FROM activities
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
            """,
            (user_id, start_date.isoformat())
        )
        title = f"Points Earned Over Last {days} Days for User"
    elif group_id:
        cursor.execute(
            """
            SELECT DATE(timestamp) as date, SUM(points) as total_points
            FROM activities
            WHERE group_id = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
            """,
            (group_id, start_date.isoformat())
        )
        title = f"Points Earned Over Last {days} Days for Group"
    else:
        cursor.execute(
            """
            SELECT DATE(timestamp) as date, SUM(points) as total_points
            FROM activities
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
            """,
            (start_date.isoformat(),)
        )
        title = f"Overall Points Earned Over Last {days} Days"
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        st.info("No points data available for line chart.")
        return
    
    # Create dataframe for display
    df = pd.DataFrame([dict(row) for row in results])
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Create line chart
    fig = px.line(
        df,
        x='date',
        y='total_points',
        title=title,
        labels={'date': 'Date', 'total_points': 'Points'},
        markers=True
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Points Earned"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_user_comparison_radar_chart(db_manager: DatabaseManager, user_ids: List[int]):
    """Render radar chart comparing multiple users.
    
    Args:
        db_manager: Database manager instance
        user_ids: List of user IDs to compare
    """
    if not user_ids:
        st.info("Please select users to compare.")
        return
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Get metrics for each user
    metrics = [
        "COUNT(*) as activity_count",
        "SUM(points) as total_points",
        "COUNT(DISTINCT DATE(timestamp)) as active_days",
        "COUNT(DISTINCT activity_type) as activity_types",
        "MAX(points) as max_points"
    ]
    
    user_data = []
    user_names = []
    
    for user_id in user_ids:
        # Get user info
        user = db_manager.get_user(user_id)
        if not user:
            continue
        
        user_names.append(user["username"])
        
        # Get metrics
        cursor.execute(
            f"""
            SELECT {', '.join(metrics)}
            FROM activities
            WHERE user_id = ?
            """,
            (user_id,)
        )
        
        result = cursor.fetchone()
        if result:
            user_data.append(dict(result))
    
    conn.close()
    
    if not user_data:
        st.info("No data available for selected users.")
        return
    
    # Create radar chart
    categories = ['Activity Count', 'Total Points', 'Active Days', 'Activity Types', 'Max Points']
    
    fig = go.Figure()
    
    for i, data in enumerate(user_data):
        values = [
            data['activity_count'],
            data['total_points'],
            data['active_days'],
            data['activity_types'],
            data['max_points']
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=user_names[i]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max([max([d[key] for d in user_data]) for key in user_data[0].keys()])]
            )
        ),
        showlegend=True,
        title="User Comparison"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_group_comparison_radar_chart(db_manager: DatabaseManager, group_ids: List[int]):
    """Render radar chart comparing multiple groups.
    
    Args:
        db_manager: Database manager instance
        group_ids: List of group IDs to compare
    """
    if not group_ids:
        st.info("Please select groups to compare.")
        return
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Get metrics for each group
    metrics = [
        "COUNT(*) as activity_count",
        "SUM(points) as total_points",
        "COUNT(DISTINCT DATE(timestamp)) as active_days",
        "COUNT(DISTINCT activity_type) as activity_types",
        "COUNT(DISTINCT user_id) as active_users"
    ]
    
    group_data = []
    group_names = []
    
    for group_id in group_ids:
        # Get group info
        group = db_manager.get_group(group_id)
        if not group:
            continue
        
        group_names.append(group["name"])
        
        # Get metrics
        cursor.execute(
            f"""
            SELECT {', '.join(metrics)}
            FROM activities
            WHERE group_id = ?
            """,
            (group_id,)
        )
        
        result = cursor.fetchone()
        if result:
            group_data.append(dict(result))
    
    conn.close()
    
    if not group_data:
        st.info("No data available for selected groups.")
        return
    
    # Create radar chart
    categories = ['Activity Count', 'Total Points', 'Active Days', 'Activity Types', 'Active Users']
    
    fig = go.Figure()
    
    for i, data in enumerate(group_data):
        values = [
            data['activity_count'],
            data['total_points'],
            data['active_days'],
            data['activity_types'],
            data['active_users']
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=group_names[i]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max([max([d[key] for d in group_data]) for key in group_data[0].keys()])]
            )
        ),
        showlegend=True,
        title="Group Comparison"
    )
    
    st.plotly_chart(fig, use_container_width=True)
