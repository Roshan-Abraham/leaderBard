-- Database initialization script for the Windsurf dashboard application
-- This script creates all necessary tables and populates them with sample data

-- Create tables
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

CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_score INTEGER DEFAULT 0,
    members_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_group (
    user_id INTEGER,
    group_id INTEGER,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role TEXT DEFAULT 'member',
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);

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

-- Insert sample users
INSERT INTO users (username, email, full_name, profile_data, score, last_active)
VALUES 
    ('john_doe', 'john.doe@example.com', 'John Doe', '{"department": "Engineering", "role": "Developer", "location": "New York"}', 1250, CURRENT_TIMESTAMP),
    ('jane_smith', 'jane.smith@example.com', 'Jane Smith', '{"department": "Marketing", "role": "Manager", "location": "San Francisco"}', 980, CURRENT_TIMESTAMP),
    ('alex_wong', 'alex.wong@example.com', 'Alex Wong', '{"department": "Design", "role": "UI/UX Designer", "location": "Chicago"}', 1430, CURRENT_TIMESTAMP),
    ('sarah_johnson', 'sarah.johnson@example.com', 'Sarah Johnson', '{"department": "Sales", "role": "Account Executive", "location": "Boston"}', 750, CURRENT_TIMESTAMP),
    ('mike_brown', 'mike.brown@example.com', 'Mike Brown', '{"department": "Engineering", "role": "QA Engineer", "location": "Seattle"}', 890, CURRENT_TIMESTAMP),
    ('lisa_taylor', 'lisa.taylor@example.com', 'Lisa Taylor', '{"department": "Product", "role": "Product Manager", "location": "Austin"}', 1120, CURRENT_TIMESTAMP),
    ('david_miller', 'david.miller@example.com', 'David Miller', '{"department": "Engineering", "role": "DevOps Engineer", "location": "Denver"}', 1360, CURRENT_TIMESTAMP),
    ('emily_wilson', 'emily.wilson@example.com', 'Emily Wilson', '{"department": "Marketing", "role": "Content Specialist", "location": "Portland"}', 870, CURRENT_TIMESTAMP),
    ('kevin_chen', 'kevin.chen@example.com', 'Kevin Chen', '{"department": "Finance", "role": "Financial Analyst", "location": "Los Angeles"}', 930, CURRENT_TIMESTAMP),
    ('olivia_garcia', 'olivia.garcia@example.com', 'Olivia Garcia', '{"department": "Customer Support", "role": "Support Manager", "location": "Miami"}', 1050, CURRENT_TIMESTAMP);

-- Insert sample groups
INSERT INTO groups (name, description, total_score, members_count)
VALUES
    ('Engineering Team', 'Software developers and engineers', 3500, 3),
    ('Marketing Team', 'Marketing and content specialists', 1850, 2),
    ('Product Team', 'Product managers and designers', 2550, 2),
    ('Sales Team', 'Sales representatives and account executives', 750, 1),
    ('Support Team', 'Customer support and success', 1050, 1);

-- Link users to groups
-- First get the user and group IDs
INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'member'
FROM users u, groups g
WHERE u.username = 'john_doe' AND g.name = 'Engineering Team';

INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'member'
FROM users u, groups g
WHERE u.username = 'mike_brown' AND g.name = 'Engineering Team';

INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'admin'
FROM users u, groups g
WHERE u.username = 'david_miller' AND g.name = 'Engineering Team';

INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'admin'
FROM users u, groups g
WHERE u.username = 'jane_smith' AND g.name = 'Marketing Team';

INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'member'
FROM users u, groups g
WHERE u.username = 'emily_wilson' AND g.name = 'Marketing Team';

INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'member'
FROM users u, groups g
WHERE u.username = 'alex_wong' AND g.name = 'Product Team';

INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'admin'
FROM users u, groups g
WHERE u.username = 'lisa_taylor' AND g.name = 'Product Team';

INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'admin'
FROM users u, groups g
WHERE u.username = 'sarah_johnson' AND g.name = 'Sales Team';

INSERT INTO user_group (user_id, group_id, role)
SELECT u.id, g.id, 'admin'
FROM users u, groups g
WHERE u.username = 'olivia_garcia' AND g.name = 'Support Team';

-- Generate sample activities for each user
-- This is a procedure that would generate 10-20 activities per user
-- with appropriate activity types, descriptions, points, and timestamps
-- For simplicity, we'll insert a few example activities for each user

-- Insert sample activities for John Doe (Engineering)
INSERT INTO activities (user_id, group_id, activity_type, description, points, timestamp, metadata)
SELECT u.id, g.id, 'Code Commit', 'Committed 25 changes to backend module', 120, 
       CURRENT_TIMESTAMP - (INTERVAL '1 day' * (floor(random() * 90)::int)) - (INTERVAL '1 hour' * (floor(random() * 24)::int)), 
       '{"complexity": "medium", "effort": "significant", "impact": "large"}'
FROM users u
LEFT JOIN user_group ug ON u.id = ug.user_id
LEFT JOIN groups g ON ug.group_id = g.id
WHERE u.username = 'john_doe';

INSERT INTO activities (user_id, group_id, activity_type, description, points, timestamp, metadata)
SELECT u.id, g.id, 'Bug Fix', 'Fixed critical bug in API', 85, 
       CURRENT_TIMESTAMP - (INTERVAL '1 day' * (floor(random() * 90)::int)) - (INTERVAL '1 hour' * (floor(random() * 24)::int)), 
       '{"complexity": "high", "effort": "significant", "impact": "large"}'
FROM users u
LEFT JOIN user_group ug ON u.id = ug.user_id
LEFT JOIN groups g ON ug.group_id = g.id
WHERE u.username = 'john_doe';

-- Insert sample activities for Jane Smith (Marketing)
INSERT INTO activities (user_id, group_id, activity_type, description, points, timestamp, metadata)
SELECT u.id, g.id, 'Social Media Post', 'Created social media content for LinkedIn', 35, 
       CURRENT_TIMESTAMP - (INTERVAL '1 day' * (floor(random() * 90)::int)) - (INTERVAL '1 hour' * (floor(random() * 24)::int)), 
       '{"complexity": "medium", "effort": "moderate", "impact": "medium"}'
FROM users u
LEFT JOIN user_group ug ON u.id = ug.user_id
LEFT JOIN groups g ON ug.group_id = g.id
WHERE u.username = 'jane_smith';

INSERT INTO activities (user_id, group_id, activity_type, description, points, timestamp, metadata)
SELECT u.id, g.id, 'Client Presentation', 'Presented to client XYZ Inc', 75, 
       CURRENT_TIMESTAMP - (INTERVAL '1 day' * (floor(random() * 90)::int)) - (INTERVAL '1 hour' * (floor(random() * 24)::int)), 
       '{"complexity": "high", "effort": "significant", "impact": "large"}'
FROM users u
LEFT JOIN user_group ug ON u.id = ug.user_id
LEFT JOIN groups g ON ug.group_id = g.id
WHERE u.username = 'jane_smith';

-- Insert sample activities for Alex Wong (Design/Product Team)
INSERT INTO activities (user_id, group_id, activity_type, description, points, timestamp, metadata)
SELECT u.id, g.id, 'Feature Implementation', 'Implemented dashboard feature', 130, 
       CURRENT_TIMESTAMP - (INTERVAL '1 day' * (floor(random() * 90)::int)) - (INTERVAL '1 hour' * (floor(random() * 24)::int)), 
       '{"complexity": "high", "effort": "significant", "impact": "large"}'
FROM users u
LEFT JOIN user_group ug ON u.id = ug.user_id
LEFT JOIN groups g ON ug.group_id = g.id
WHERE u.username = 'alex_wong';

-- Insert sample activities for other users
-- For brevity, just a couple more examples
INSERT INTO activities (user_id, group_id, activity_type, description, points, timestamp, metadata)
SELECT u.id, g.id, 'Support Ticket Resolution', 'Resolved high priority support ticket', 45, 
       CURRENT_TIMESTAMP - (INTERVAL '1 day' * (floor(random() * 90)::int)) - (INTERVAL '1 hour' * (floor(random() * 24)::int)), 
       '{"complexity": "medium", "effort": "moderate", "impact": "medium"}'
FROM users u
LEFT JOIN user_group ug ON u.id = ug.user_id
LEFT JOIN groups g ON ug.group_id = g.id
WHERE u.username = 'olivia_garcia';

INSERT INTO activities (user_id, group_id, activity_type, description, points, timestamp, metadata)
SELECT u.id, g.id, 'Documentation', 'Updated API documentation', 30, 
       CURRENT_TIMESTAMP - (INTERVAL '1 day' * (floor(random() * 90)::int)) - (INTERVAL '1 hour' * (floor(random() * 24)::int)), 
       '{"complexity": "low", "effort": "moderate", "impact": "medium"}'
FROM users u
LEFT JOIN user_group ug ON u.id = ug.user_id
LEFT JOIN groups g ON ug.group_id = g.id
WHERE u.username = 'david_miller';

-- Postgres compatibility version
-- The following section contains PostgreSQL-specific syntax
-- It's already properly formatted for PostgreSQL since we're using SERIAL PRIMARY KEY
/*
-- For PostgreSQL: No need to alter column types as they are already set to SERIAL in the main table creation

-- No need to replace activity insert statements as they now use PostgreSQL-compatible syntax

-- And similarly for the other activity inserts
*/
