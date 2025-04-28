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
from .utils import load_instruction_from_file  # Fixed

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
    
    # Add user message to history with timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        "role": "user", 
        "content": message,
        "timestamp": timestamp,
        "status": "sent"
    })
    
    # Process with agent
    try:
        agent_manager = st.session_state.agent_manager
        response = agent_manager.run_agent(message)
        
        # Add agent response to history with status and metadata
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": response["output"],
            "timestamp": timestamp,
            "status": response["status"],
            "metadata": response.get("metadata", {})
        })
    except Exception as e:
        # Add error message to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"Error processing your request: {str(e)}",
            "timestamp": timestamp,
            "status": "error"
        })


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
    
    # Introduction and instructions
    st.write("""
    Use this interface to interact with the dashboard agent. You can:
    - Ask questions about the dashboard data
    - Upload Excel files for processing
    - Upload Word documents for processing
    - Request to add or update information
    """)
    
    # Create two columns - one for chat, one for file uploads
    chat_col, upload_col = st.columns([3, 1])
    
    with upload_col:
        st.subheader("Upload Files")
        
        # Excel file upload
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
        
        # Word document upload
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
    
    with chat_col:
        # Chat interface
        st.subheader("Chat with Dashboard Assistant")
        
        # Chat display area with custom styling
        chat_container = st.container()
        
        # Apply custom CSS for better chat bubble styling
        st.markdown("""
        <style>
        .user-bubble {
            background-color: #e6f7ff;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 5px 0;
            border-bottom-right-radius: 5px;
            max-width: 80%;
            margin-left: auto;
            margin-right: 10px;
        }
        .assistant-bubble {
            background-color: #f0f0f0;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 5px 0;
            border-bottom-left-radius: 5px;
            max-width: 80%;
            margin-right: auto;
            margin-left: 10px;
        }
        .timestamp {
            font-size: 0.7em;
            color: #888;
            text-align: right;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #eee;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display chat in a scrollable container
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="user-bubble">
                        <b>You:</b> {message['content']}
                        <div class="timestamp">{message.get('timestamp', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Determine if there was an error
                    bubble_style = "assistant-bubble"
                    if message.get("status") == "error":
                        bubble_style += " error-message"
                    
                    st.markdown(f"""
                    <div class="{bubble_style}">
                        <b>Assistant:</b> {message['content']}
                        <div class="timestamp">{message.get('timestamp', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Input for new message with better styling
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Chat input and send button side by side
        message_col, button_col = st.columns([4, 1])
        
        with message_col:
            user_message = st.text_area("Message", key="agent_input", placeholder="Type your message here...", height=80)
        
        with button_col:
            st.write("")  # Add some spacing
            st.write("")  # Add some spacing
            send_pressed = st.button("Send", key="send_button", use_container_width=True)
        
        # Handle enter key press for sending (using JavaScript)
        st.markdown("""
        <script>
        const textarea = document.querySelector('textarea[aria-label="Message"]');
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const button = document.querySelector('button:contains("Send")');
                button.click();
            }
        });
        </script>
        """, unsafe_allow_html=True)
        
        if send_pressed and user_message:
            process_agent_message(user_message)
            st.experimental_rerun()


# Run the app
if __name__ == "__main__":
    main()
