"""
Initialize database with sample data for testing.
"""
import sqlite3
import json
import random
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.schema import (CREATE_USERS_TABLE, CREATE_GROUPS_TABLE,
                          CREATE_USER_GROUP_TABLE, CREATE_ACTIVITIES_TABLE)


def init_database(db_path):
    """Initialize database with tables and sample data.
    
    Args:
        db_path: Path to the SQLite database
    """
    # Create directory for database if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute(CREATE_USERS_TABLE)
    cursor.execute(CREATE_GROUPS_TABLE)
    cursor.execute(CREATE_USER_GROUP_TABLE)
    cursor.execute(CREATE_ACTIVITIES_TABLE)
    
    # Insert sample users
    sample_users = [
        {
            'username': 'john_doe',
            'email': 'john.doe@example.com',
            'full_name': 'John Doe',
            'profile_data': json.dumps({'department': 'Engineering', 'role': 'Developer', 'location': 'New York'}),
            'score': 1250
        },
        {
            'username': 'jane_smith',
            'email': 'jane.smith@example.com',
            'full_name': 'Jane Smith',
            'profile_data': json.dumps({'department': 'Marketing', 'role': 'Manager', 'location': 'San Francisco'}),
            'score': 980
        },
        {
            'username': 'alex_wong',
            'email': 'alex.wong@example.com',
            'full_name': 'Alex Wong',
            'profile_data': json.dumps({'department': 'Design', 'role': 'UI/UX Designer', 'location': 'Chicago'}),
            'score': 1430
        },
        {
            'username': 'sarah_johnson',
            'email': 'sarah.johnson@example.com',
            'full_name': 'Sarah Johnson',
            'profile_data': json.dumps({'department': 'Sales', 'role': 'Account Executive', 'location': 'Boston'}),
            'score': 750
        },
        {
            'username': 'mike_brown',
            'email': 'mike.brown@example.com',
            'full_name': 'Mike Brown',
            'profile_data': json.dumps({'department': 'Engineering', 'role': 'QA Engineer', 'location': 'Seattle'}),
            'score': 890
        },
        {
            'username': 'lisa_taylor',
            'email': 'lisa.taylor@example.com',
            'full_name': 'Lisa Taylor',
            'profile_data': json.dumps({'department': 'Product', 'role': 'Product Manager', 'location': 'Austin'}),
            'score': 1120
        },
        {
            'username': 'david_miller',
            'email': 'david.miller@example.com',
            'full_name': 'David Miller',
            'profile_data': json.dumps({'department': 'Engineering', 'role': 'DevOps Engineer', 'location': 'Denver'}),
            'score': 1360
        },
        {
            'username': 'emily_wilson',
            'email': 'emily.wilson@example.com',
            'full_name': 'Emily Wilson',
            'profile_data': json.dumps({'department': 'Marketing', 'role': 'Content Specialist', 'location': 'Portland'}),
            'score': 870
        },
        {
            'username': 'kevin_chen',
            'email': 'kevin.chen@example.com',
            'full_name': 'Kevin Chen',
            'profile_data': json.dumps({'department': 'Finance', 'role': 'Financial Analyst', 'location': 'Los Angeles'}),
            'score': 930
        },
        {
            'username': 'olivia_garcia',
            'email': 'olivia.garcia@example.com',
            'full_name': 'Olivia Garcia',
            'profile_data': json.dumps({'department': 'Customer Support', 'role': 'Support Manager', 'location': 'Miami'}),
            'score': 1050
        }
    ]
    
    now = datetime.now().isoformat()
    
    for user in sample_users:
        cursor.execute(
            """
            INSERT INTO users (username, email, full_name, profile_data, score, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user['username'], user['email'], user['full_name'], user['profile_data'], user['score'], now)
        )
    
    # Insert sample groups
    sample_groups = [
        {
            'name': 'Engineering Team',
            'description': 'Software developers and engineers',
            'total_score': 3500,
            'members_count': 3
        },
        {
            'name': 'Marketing Team',
            'description': 'Marketing and content specialists',
            'total_score': 1850,
            'members_count': 2
        },
        {
            'name': 'Product Team',
            'description': 'Product managers and designers',
            'total_score': 2550,
            'members_count': 2
        },
        {
            'name': 'Sales Team',
            'description': 'Sales representatives and account executives',
            'total_score': 750,
            'members_count': 1
        },
        {
            'name': 'Support Team',
            'description': 'Customer support and success',
            'total_score': 1050,
            'members_count': 1
        }
    ]
    
    for group in sample_groups:
        cursor.execute(
            """
            INSERT INTO groups (name, description, total_score, members_count)
            VALUES (?, ?, ?, ?)
            """,
            (group['name'], group['description'], group['total_score'], group['members_count'])
        )
    
    # Link users to groups
    user_group_mappings = [
        {'username': 'john_doe', 'group_name': 'Engineering Team', 'role': 'member'},
        {'username': 'mike_brown', 'group_name': 'Engineering Team', 'role': 'member'},
        {'username': 'david_miller', 'group_name': 'Engineering Team', 'role': 'admin'},
        {'username': 'jane_smith', 'group_name': 'Marketing Team', 'role': 'admin'},
        {'username': 'emily_wilson', 'group_name': 'Marketing Team', 'role': 'member'},
        {'username': 'alex_wong', 'group_name': 'Product Team', 'role': 'member'},
        {'username': 'lisa_taylor', 'group_name': 'Product Team', 'role': 'admin'},
        {'username': 'sarah_johnson', 'group_name': 'Sales Team', 'role': 'admin'},
        {'username': 'olivia_garcia', 'group_name': 'Support Team', 'role': 'admin'}
    ]
    
    for mapping in user_group_mappings:
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (mapping['username'],))
        user_id = cursor.fetchone()[0]
        
        # Get group ID
        cursor.execute("SELECT id FROM groups WHERE name = ?", (mapping['group_name'],))
        group_id = cursor.fetchone()[0]
        
        cursor.execute(
            """
            INSERT INTO user_group (user_id, group_id, role)
            VALUES (?, ?, ?)
            """,
            (user_id, group_id, mapping['role'])
        )
    
    # Generate sample activities
    activity_types = [
        'Code Commit', 'Pull Request', 'Code Review', 'Bug Fix',
        'Feature Implementation', 'Documentation', 'Meeting Attendance',
        'Knowledge Sharing', 'Client Presentation', 'Training Completion',
        'Blog Post', 'Social Media Post', 'Lead Generation', 'Customer Onboarding',
        'Support Ticket Resolution'
    ]
    
    # Map activity types to specific users based on their department
    activity_type_by_department = {
        'Engineering': ['Code Commit', 'Pull Request', 'Code Review', 'Bug Fix', 'Feature Implementation', 'Documentation'],
        'Marketing': ['Social Media Post', 'Blog Post', 'Client Presentation', 'Lead Generation'],
        'Design': ['Documentation', 'Client Presentation', 'Feature Implementation'],
        'Sales': ['Client Presentation', 'Lead Generation', 'Customer Onboarding'],
        'Product': ['Feature Implementation', 'Documentation', 'Meeting Attendance', 'Client Presentation'],
        'Customer Support': ['Support Ticket Resolution', 'Customer Onboarding', 'Documentation'],
        'Finance': ['Documentation', 'Meeting Attendance', 'Knowledge Sharing']
    }
    
    # Generate activities for each user
    for user in sample_users:
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
        user_id = cursor.fetchone()[0]
        
        # Get group ID if the user is in a group
        cursor.execute(
            """
            SELECT g.id, g.name 
            FROM groups g
            JOIN user_group ug ON g.id = ug.group_id
            WHERE ug.user_id = ?
            """,
            (user_id,)
        )
        group_result = cursor.fetchone()
        group_id = group_result[0] if group_result else None
        group_name = group_result[1] if group_result else None
        
        # Get department for the user
        department = json.loads(user['profile_data'])['department']
        
        # Get activity types for this user's department
        user_activity_types = activity_type_by_department.get(department, activity_types)
        
        # Generate 10-20 activities per user
        num_activities = random.randint(10, 20)
        
        for _ in range(num_activities):
            activity_type = random.choice(user_activity_types)
            
            # Generate descriptions based on activity type
            if activity_type == 'Code Commit':
                description = f"Committed {random.randint(5, 50)} changes to {random.choice(['frontend', 'backend', 'database', 'API', 'documentation'])} module"
            elif activity_type == 'Pull Request':
                description = f"Opened pull request for {random.choice(['feature implementation', 'bug fix', 'code refactoring', 'performance optimization'])}"
            elif activity_type == 'Code Review':
                description = f"Reviewed pull request by {random.choice([u['username'] for u in sample_users if u['username'] != user['username']])}"
            elif activity_type == 'Bug Fix':
                description = f"Fixed {random.choice(['critical', 'major', 'minor'])} bug in {random.choice(['frontend', 'backend', 'database', 'API'])}"
            elif activity_type == 'Feature Implementation':
                description = f"Implemented {random.choice(['authentication', 'notification', 'reporting', 'dashboard', 'integration'])} feature"
            elif activity_type == 'Documentation':
                description = f"Updated documentation for {random.choice(['API', 'user guide', 'developer guide', 'installation', 'configuration'])}"
            elif activity_type == 'Meeting Attendance':
                description = f"Attended {random.choice(['team', 'project', 'planning', 'retrospective', 'daily standup'])} meeting"
            elif activity_type == 'Knowledge Sharing':
                description = f"Shared knowledge about {random.choice(['new technology', 'best practices', 'industry trends', 'case study'])}"
            elif activity_type == 'Client Presentation':
                description = f"Presented to client {random.choice(['ABC Corp', 'XYZ Inc', '123 Industries', 'Tech Solutions', 'Global Services'])}"
            elif activity_type == 'Training Completion':
                description = f"Completed training on {random.choice(['new technology', 'leadership', 'communication', 'project management'])}"
            elif activity_type == 'Blog Post':
                description = f"Published blog post about {random.choice(['industry trends', 'case study', 'technology review', 'company culture'])}"
            elif activity_type == 'Social Media Post':
                description = f"Created social media content for {random.choice(['Facebook', 'Twitter', 'LinkedIn', 'Instagram'])}"
            elif activity_type == 'Lead Generation':
                description = f"Generated {random.randint(1, 10)} new leads for {random.choice(['product A', 'product B', 'service X', 'service Y'])}"
            elif activity_type == 'Customer Onboarding':
                description = f"Onboarded customer {random.choice(['ABC Corp', 'XYZ Inc', '123 Industries', 'Tech Solutions', 'Global Services'])}"
            elif activity_type == 'Support Ticket Resolution':
                description = f"Resolved {random.choice(['critical', 'high', 'medium', 'low'])} priority support ticket"
            else:
                description = f"Completed {activity_type} activity"
            
            # Generate random points (more for complex activities)
            if activity_type in ['Feature Implementation', 'Bug Fix', 'Code Commit', 'Pull Request']:
                points = random.randint(50, 150)
            elif activity_type in ['Client Presentation', 'Blog Post', 'Customer Onboarding']:
                points = random.randint(30, 100)
            else:
                points = random.randint(10, 50)
            
            # Generate random timestamp within the last 90 days
            timestamp = (datetime.now() - timedelta(days=random.randint(0, 90), 
                                                  hours=random.randint(0, 23), 
                                                  minutes=random.randint(0, 59))).isoformat()
            
            # Create metadata
            metadata = {
                'complexity': random.choice(['low', 'medium', 'high']),
                'effort': random.choice(['minimal', 'moderate', 'significant']),
                'impact': random.choice(['small', 'medium', 'large'])
            }
            
            metadata_json = json.dumps(metadata)
            
            cursor.execute(
                """
                INSERT INTO activities (user_id, group_id, activity_type, description, points, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, group_id, activity_type, description, points, timestamp, metadata_json)
            )
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {db_path} with sample data")


if __name__ == "__main__":
    # Get database path from environment variable or use default
    db_path = os.environ.get("DB_PATH", "data/dashboard.db")
    init_database(db_path)


