"""
Database schema definitions for the dashboard application.
"""

CREATE_GROUPS_TABLE = """
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_score INTEGER DEFAULT 0,
    members_count INTEGER DEFAULT 0
);
"""

CREATE_USER_GROUP_TABLE = """
CREATE TABLE IF NOT EXISTS user_group (
    user_id INTEGER,
    group_id INTEGER,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role TEXT DEFAULT 'member',
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_data TEXT,
    score INTEGER DEFAULT 0,
    activities TEXT,
    last_active TIMESTAMP
);
"""

CREATE_ACTIVITIES_TABLE = """
CREATE TABLE IF NOT EXISTS activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    group_id INTEGER,
    activity_type TEXT NOT NULL,
    description TEXT,
    points INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);
"""

# List of all tables creation statements
ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_GROUPS_TABLE,
    CREATE_USER_GROUP_TABLE,
    CREATE_ACTIVITIES_TABLE
]

# Sample queries for dashboard components
GET_TOP_USERS = """
SELECT username, score FROM users 
ORDER BY score DESC LIMIT ?
"""

GET_TOP_GROUPS = """
SELECT name, total_score FROM groups 
ORDER BY total_score DESC LIMIT ?
"""

GET_USER_ACTIVITIES = """
SELECT activity_type, description, points, timestamp 
FROM activities 
WHERE user_id = ? 
ORDER BY timestamp DESC LIMIT ?
"""

GET_GROUP_ACTIVITIES = """
SELECT a.activity_type, a.description, a.points, a.timestamp, u.username
FROM activities a
JOIN users u ON a.user_id = u.id
WHERE a.group_id = ? 
ORDER BY a.timestamp DESC LIMIT ?
"""

GET_USER_PROFILE = """
SELECT username, email, full_name, created_at, profile_data, score, last_active
FROM users
WHERE id = ?
"""

GET_GROUP_DETAILS = """
SELECT g.name, g.description, g.created_at, g.total_score, g.members_count,
       COUNT(a.id) as activity_count
FROM groups g
LEFT JOIN activities a ON g.id = a.group_id
WHERE g.id = ?
GROUP BY g.id
"""

# Get user timeline data
GET_USER_TIMELINE = """
SELECT timestamp, activity_type, points, description
FROM activities
WHERE user_id = ?
ORDER BY timestamp ASC
"""

# Get group timeline data
GET_GROUP_TIMELINE = """
SELECT a.timestamp, a.activity_type, a.points, a.description, u.username
FROM activities a
JOIN users u ON a.user_id = u.id
WHERE a.group_id = ?
ORDER BY a.timestamp ASC
"""
