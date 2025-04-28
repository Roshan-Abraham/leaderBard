"""
Timeline component for the Streamlit dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import DatabaseManager


def render_user_timeline(db_manager: DatabaseManager, user_id: int):
    """Render timeline for a specific user.
    
    Args:
        db_manager: Database manager instance
        user_id: User ID
    """
    # Get user information
    user = db_manager.get_user(user_id)
    if not user:
        st.error(f"User with ID {user_id} not found.")
        return
    
    st.subheader(f"Timeline for {user['username']}")
    
    # Get timeline data
    timeline_data = db_manager.get_user_activities_timeline(user_id)
    
    if not timeline_data:
        st.info(f"No activity data available for {user['username']}.")
        return
    
    # Create dataframe
    df = pd.DataFrame(timeline_data)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Cumulative sum of points
    df['cumulative_points'] = df['points'].cumsum()
    
    # Create two visualizations
    
    # 1. Gantt chart for activities
    create_activity_gantt(df, f"Activity Timeline for {user['username']}")
    
    # 2. Line chart for cumulative points
    create_cumulative_points_chart(df, f"Points Progression for {user['username']}")
    
    # 3. Activity list
    create_activity_list(df)


def render_group_timeline(db_manager: DatabaseManager, group_id: int):
    """Render timeline for a specific group.
    
    Args:
        db_manager: Database manager instance
        group_id: Group ID
    """
    # Get group information
    group = db_manager.get_group(group_id)
    if not group:
        st.error(f"Group with ID {group_id} not found.")
        return
    
    st.subheader(f"Timeline for {group['name']}")
    
    # Get timeline data
    timeline_data = db_manager.get_group_activities_timeline(group_id)
    
    if not timeline_data:
        st.info(f"No activity data available for {group['name']}.")
        return
    
    # Create dataframe
    df = pd.DataFrame(timeline_data)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Cumulative sum of points
    df['cumulative_points'] = df['points'].cumsum()
    
    # Create visualizations
    
    # 1. Gantt chart for activities by user
    create_activity_gantt(df, f"Activity Timeline for {group['name']}", user_col='username')
    
    # 2. Line chart for cumulative points
    create_cumulative_points_chart(df, f"Points Progression for {group['name']}")
    
    # 3. Activity list with usernames
    create_activity_list(df, include_username=True)


def create_activity_gantt(df: pd.DataFrame, title: str, user_col: Optional[str] = None):
    """Create a Gantt chart for activities.
    
    Args:
        df: DataFrame with activity data
        title: Chart title
        user_col: Column name for user if included
    """
    # Create a copy to avoid modifying the original
    plot_df = df.copy()
    
    # Add duration (assume each activity takes 1 hour by default)
    plot_df['end_time'] = plot_df['timestamp'] + pd.Timedelta(hours=1)
    
    # Prepare data for Gantt chart
    if user_col and user_col in plot_df.columns:
        # If user column is provided, use it for grouping
        fig = px.timeline(
            plot_df,
            x_start='timestamp',
            x_end='end_time',
            y=user_col,
            color='activity_type',
            hover_data=['description', 'points'],
            title=title
        )
    else:
        # Use activity type for grouping
        fig = px.timeline(
            plot_df,
            x_start='timestamp',
            x_end='end_time',
            y='activity_type',
            color='activity_type',
            hover_data=['description', 'points'],
            title=title
        )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date & Time",
        yaxis_title="",
        height=400
    )
    
    # Update yaxis to be in reverse order (latest at the top)
    fig.update_yaxes(autorange="reversed")
    
    st.plotly_chart(fig, use_container_width=True)


def create_cumulative_points_chart(df: pd.DataFrame, title: str):
    """Create a line chart for cumulative points over time.
    
    Args:
        df: DataFrame with activity data including cumulative_points
        title: Chart title
    """
    fig = px.line(
        df,
        x='timestamp',
        y='cumulative_points',
        title=title,
        labels={'timestamp': 'Date & Time', 'cumulative_points': 'Cumulative Points'},
        markers=True
    )
    
    # Add points as scatter plot
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['points'],
            mode='markers',
            name='Points per Activity',
            marker=dict(
                size=10,
                color=df['points'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Points")
            ),
            hovertemplate='%{x}<br>Points: %{y}<br><extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date & Time",
        yaxis_title="Points",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_activity_list(df: pd.DataFrame, include_username: bool = False):
    """Create an expandable list of activities.
    
    Args:
        df: DataFrame with activity data
        include_username: Whether to include username column
    """
    st.subheader("Activity Details")
    
    # Format DataFrame for display
    display_df = df.copy()
    
    # Format timestamp
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Select columns to display
    if include_username and 'username' in display_df.columns:
        columns = ['timestamp', 'username', 'activity_type', 'description', 'points']
    else:
        columns = ['timestamp', 'activity_type', 'description', 'points']
    
    display_df = display_df[columns]
    
    # Rename columns for better display
    column_names = {
        'timestamp': 'Date & Time',
        'username': 'User',
        'activity_type': 'Activity Type',
        'description': 'Description',
        'points': 'Points'
    }
    display_df = display_df.rename(columns=column_names)
    
    # Sort by timestamp (newest first)
    display_df = display_df.sort_values(by='Date & Time', ascending=False)
    
    # Display as table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def render_activity_calendar(db_manager: DatabaseManager, user_id: Optional[int] = None, 
                          group_id: Optional[int] = None, year: Optional[int] = None):
    """Render calendar heatmap of activities.
    
    Args:
        db_manager: Database manager instance
        user_id: Optional user ID to filter activities
        group_id: Optional group ID to filter activities
        year: Year to display, defaults to current year
    """
    # Determine year
    if year is None:
        year = datetime.now().year
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Build query based on filters
    query = """
        SELECT DATE(timestamp) as date, COUNT(*) as activity_count, SUM(points) as points_sum
        FROM activities
        WHERE strftime('%Y', timestamp) = ?
    """
    
    params = [str(year)]
    
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
        
        # Get user info
        user = db_manager.get_user(user_id)
        entity_name = user['username'] if user else f"User {user_id}"
    elif group_id:
        query += " AND group_id = ?"
        params.append(group_id)
        
        # Get group info
        group = db_manager.get_group(group_id)
        entity_name = group['name'] if group else f"Group {group_id}"
    else:
        entity_name = "All Users & Groups"
    
    query += " GROUP BY DATE(timestamp) ORDER BY date"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        st.info(f"No activity data available for {entity_name} in {year}.")
        return
    
    # Create dataframe
    df = pd.DataFrame([dict(row) for row in results])
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Create calendar heatmap
    title = f"Activity Calendar for {entity_name} ({year})"
    
    # Create a date range for the full year
    start_date = pd.Timestamp(year=year, month=1, day=1)
    end_date = pd.Timestamp(year=year, month=12, day=31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create a DataFrame with all dates in the year
    full_df = pd.DataFrame({'date': date_range})
    
    # Merge with activity data
    full_df = pd.merge(full_df, df, on='date', how='left')
    
    # Fill NaN values with 0
    full_df = full_df.fillna(0)
    
    # Extract components for calendar display
    full_df['month'] = full_df['date'].dt.month_name()
    full_df['day'] = full_df['date'].dt.day
    full_df['weekday'] = full_df['date'].dt.day_name()
    
    # Create heatmap
    fig = px.density_heatmap(
        full_df,
        x='day',
        y='month',
        z='points_sum',
        title=title,
        labels={'day': 'Day of Month', 'month': 'Month', 'points_sum': 'Points'},
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        height=500,
        xaxis_title="Day of Month",
        yaxis_title="Month",
        coloraxis_colorbar=dict(title="Points")
    )
    
    # Order y-axis (months) correctly
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    fig.update_layout(yaxis={'categoryarray': month_order[::-1]})
    
    st.plotly_chart(fig, use_container_width=True)
