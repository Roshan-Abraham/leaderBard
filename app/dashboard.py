"""
Main Streamlit dashboard application.
"""
import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import components
from components.leaderboard import render_combined_leaderboard
from components.graphs import (render_user_score_chart, render_group_score_chart,
                               render_activity_type_pie_chart, render_points_over_time_chart,
                               render_user_comparison_radar_chart, render_group_comparison_radar_chart)
from components.timeline import (render_user_timeline, render_group_timeline, 
                                render_activity_calendar)
from components.detail_cards import (render_user_card, render_group_card,
                                    render_user_selection_card, render_group_selection_card)

# Import database manager
from database.db_manager import DatabaseManager

# Import agent manager
from agents.agent_manager import create_agent_manager, AgentManager


# Set page configuration
st.set_page_config(
    page_title="Dashboard with Agent Integration",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'agent_manager' not in st.session_state:
    st.session_state.agent_manager = create_agent_manager()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


# Helper function for the agent chat interface
def process_agent_message(message):
    """Process a message with the agent and update chat history."""
    if not message.strip():
        return
    
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": message})
    
    # Process with agent
    try:
        agent_manager = st.session_state.agent_manager
        response = agent_manager.run_agent(message)
        agent_response = response["output"]
        
        # Add agent response to history
        st.session_state.chat_history.append({"role": "assistant", "content": agent_response})
    except Exception as e:
        error_msg = f"Error processing your request: {str(e)}"
        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})


# Main dashboard layout
def main():
    """Main dashboard application."""
    
    # Sidebar for navigation
    st.sidebar.title("Dashboard Navigation")
    
    # Main sections
    pages = [
        "Overview",
        "User Details",
        "Group Details",
        "Comparison Analytics",
        "Activity Timeline",
        "Agent Interface"
    ]
    
    selected_page = st.sidebar.radio("Go to", pages)
    
    # Initialize the database manager
    db_manager = st.session_state.db_manager
    
    # Page title
    st.title("Dashboard with Agent Integration")
    st.write("An interactive dashboard for tracking user and group performance")
    
    # Render the selected page
    if selected_page == "Overview":
        render_overview_page(db_manager)
    elif selected_page == "User Details":
        render_user_details_page(db_manager)
    elif selected_page == "Group Details":
        render_group_details_page(db_manager)
    elif selected_page == "Comparison Analytics":
        render_comparison_page(db_manager)
    elif selected_page == "Activity Timeline":
        render_timeline_page(db_manager)
    elif selected_page == "Agent Interface":
        render_agent_interface_page(db_manager)


def render_overview_page(db_manager):
    """Render the overview dashboard page."""
    st.header("Dashboard Overview")
    
    # Top leaderboards
    render_combined_leaderboard(db_manager, limit=5)
    
    # Activity metrics
    st.subheader("Activity Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_activity_type_pie_chart(db_manager)
    
    with col2:
        render_points_over_time_chart(db_manager, days=30)
    
    # Top performers charts
    st.subheader("Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_user_score_chart(db_manager, limit=5)
    
    with col2:
        render_group_score_chart(db_manager, limit=5)
    
    # Activity calendar
    st.subheader("Activity Calendar")
    render_activity_calendar(db_manager)


def render_user_details_page(db_manager):
    """Render the user details page."""
    st.header("User Details")
    
    # User selection
    selected_user_id = render_user_selection_card(db_manager)
    
    if selected_user_id:
        # Display user card
        render_user_card(db_manager, selected_user_id)
        
        # Display user timeline
        render_user_timeline(db_manager, selected_user_id)
        
        # Display user analytics
        st.header("User Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            render_activity_type_pie_chart(db_manager, user_id=selected_user_id)
        
        with col2:
            render_points_over_time_chart(db_manager, user_id=selected_user_id)


def render_group_details_page(db_manager):
    """Render the group details page."""
    st.header("Group Details")
    
    # Group selection
    selected_group_id = render_group_selection_card(db_manager)
    
    if selected_group_id:
        # Display group card
        render_group_card(db_manager, selected_group_id)
        
        # Display group timeline
        render_group_timeline(db_manager, selected_group_id)
        
        # Display group analytics
        st.header("Group Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            render_activity_type_pie_chart(db_manager, group_id=selected_group_id)
        
        with col2:
            render_points_over_time_chart(db_manager, group_id=selected_group_id)


def render_comparison_page(db_manager):
    """Render the comparison analytics page."""
    st.header("Comparison Analytics")
    
    # Selection tabs
    tab1, tab2 = st.tabs(["Compare Users", "Compare Groups"])
    
    with tab1:
        st.subheader("Compare Users")
        
        # Get all users for selection
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, score FROM users ORDER BY username")
        all_users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not all_users:
            st.info("No users available for comparison.")
        else:
            # Create options for multiselect
            user_options = {f"{user['username']} ({user['score']} pts)": user['id'] for user in all_users}
            
            selected_users = st.multiselect(
                "Select users to compare",
                options=list(user_options.keys()),
                key="user_compare"
            )
            
            if selected_users:
                # Get IDs of selected users
                selected_user_ids = [user_options[user] for user in selected_users]
                
                # Render comparison chart
                render_user_comparison_radar_chart(db_manager, selected_user_ids)
                
                # Render score chart for selected users
                col1, col2 = st.columns(2)
                
                with col1:
                    for user_id in selected_user_ids:
                        user = db_manager.get_user(user_id)
                        if user:
                            st.write(f"**{user['username']}:** {user['score']} points")
    
    with tab2:
        st.subheader("Compare Groups")
        
        # Get all groups for selection
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, total_score FROM groups ORDER BY name")
        all_groups = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not all_groups:
            st.info("No groups available for comparison.")
        else:
            # Create options for multiselect
            group_options = {f"{group['name']} ({group['total_score']} pts)": group['id'] for group in all_groups}
            
            selected_groups = st.multiselect(
                "Select groups to compare",
                options=list(group_options.keys()),
                key="group_compare"
            )
            
            if selected_groups:
                # Get IDs of selected groups
                selected_group_ids = [group_options[group] for group in selected_groups]
                
                # Render comparison chart
                render_group_comparison_radar_chart(db_manager, selected_group_ids)
                
                # Render score chart for selected groups
                col1, col2 = st.columns(2)
                
                with col1:
                    for group_id in selected_group_ids:
                        group = db_manager.get_group(group_id)
                        if group:
                            st.write(f"**{group['name']}:** {group['total_score']} points")


def render_timeline_page(db_manager):
    """Render the activity timeline page."""
    st.header("Activity Timeline")
    
    # Selection options
    timeline_type = st.selectbox(
        "Select timeline type",
        options=["Overall Activity", "User Activity", "Group Activity"],
        key="timeline_type"
    )
    
    if timeline_type == "Overall Activity":
        # Year selection for calendar
        current_year = datetime.now().year
        year_options = list(range(current_year - 5, current_year + 1))
        selected_year = st.selectbox(
            "Select year",
            options=year_options,
            index=len(year_options) - 1,
            key="overall_year"
        )
        
        # Render calendar
        render_activity_calendar(db_manager, year=selected_year)
        
    elif timeline_type == "User Activity":
        # User selection
        selected_user_id = render_user_selection_card(db_manager)
        
        if selected_user_id:
            # Year selection for calendar
            current_year = datetime.now().year
            year_options = list(range(current_year - 5, current_year + 1))
            selected_year = st.selectbox(
                "Select year",
                options=year_options,
                index=len(year_options) - 1,
                key="user_year"
            )
            
            # Render user timeline
            render_user_timeline(db_manager, selected_user_id)
            
            # Render user calendar
            render_activity_calendar(db_manager, user_id=selected_user_id, year=selected_year)
    
    elif timeline_type == "Group Activity":
        # Group selection
        selected_group_id = render_group_selection_card(db_manager)
        
        if selected_group_id:
            # Year selection for calendar
            current_year = datetime.now().year
            year_options = list(range(current_year - 5, current_year + 1))
            selected_year = st.selectbox(
                "Select year",
                options=year_options,
                index=len(year_options) - 1,
                key="group_year"
            )
            
            # Render group timeline
            render_group_timeline(db_manager, selected_group_id)
            
            # Render group calendar
            render_activity_calendar(db_manager, group_id=selected_group_id, year=selected_year)


def render_agent_interface_page(db_manager):
    """Render the agent interface page."""
    st.header("Agent Interface")
    
    st.write("""
    Use this interface to interact with the dashboard agent. You can:
    - Ask questions about the dashboard data
    - Upload Excel files for processing
    - Upload Word documents for processing
    - Request to add or update information
    """)
    
    # File upload section
    st.subheader("Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_excel = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
        
        if uploaded_excel:
            # Save the uploaded file
            excel_path = os.path.join("uploads", uploaded_excel.name)
            os.makedirs("uploads", exist_ok=True)
            
            with open(excel_path, "wb") as f:
                f.write(uploaded_excel.getbuffer())
            
            st.success(f"Excel file saved: {excel_path}")
            
            # Add a message to the chat about the uploaded file
            process_agent_message(f"I've uploaded an Excel file called {uploaded_excel.name}. Please process it. The file is saved at {excel_path}")
    
    with col2:
        uploaded_doc = st.file_uploader("Upload Word Document", type=["docx"])
        
        if uploaded_doc:
            # Save the uploaded file
            doc_path = os.path.join("uploads", uploaded_doc.name)
            os.makedirs("uploads", exist_ok=True)
            
            with open(doc_path, "wb") as f:
                f.write(uploaded_doc.getbuffer())
            
            st.success(f"Document file saved: {doc_path}")
            
            # Add a message to the chat about the uploaded file
            process_agent_message(f"I've uploaded a document file called {uploaded_doc.name}. Please process it. The file is saved at {doc_path}")
    
    # Chat interface
    st.subheader("Chat with Agent")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Agent:** {message['content']}")
    
    # Input for new message
    user_message = st.text_area("Type your message", key="agent_input")
    
    if st.button("Send", key="send_button"):
        process_agent_message(user_message)
        st.experimental_rerun()


# Run the app
if __name__ == "__main__":
    main()
