"""
Excel tools for agents using Google ADK framework.
"""
from typing import List, Dict, Any, Optional
import os
import sys
import pandas as pd
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import DatabaseManager
from .util import load_instruction_from_file

# Initialize database manager
db_manager = DatabaseManager()

def read_excel(file_path: str, sheet_name: str = "Sheet1") -> Dict:
    """Read data from an Excel file.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to read
        
    Returns:
        Dictionary with Excel data and metadata
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return {
            "columns": df.columns.tolist(),
            "rows_count": len(df),
            "sample_data": df.head(5).to_dict(orient="records"),
            "complete_data": df.to_dict(orient="records")
        }
    except Exception as e:
        return {"error": f"Error reading Excel file: {str(e)}"}

def import_users_from_excel(file_path: str, sheet_name: str = "Sheet1", username_col: str = None,
                           email_col: Optional[str] = None, full_name_col: Optional[str] = None,
                           profile_data_cols: Optional[List[str]] = None) -> Dict:
    """Import users from an Excel file into the database.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to read
        username_col: Column name for username
        email_col: Column name for email
        full_name_col: Column name for full name
        profile_data_cols: Columns to include in profile data
        
    Returns:
        Import results summary
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Validate required columns
        if username_col not in df.columns:
            return {"error": f"Username column '{username_col}' not found in Excel file"}
        
        # Validate optional columns
        if email_col and email_col not in df.columns:
            return {"error": f"Email column '{email_col}' not found in Excel file"}
        if full_name_col and full_name_col not in df.columns:
            return {"error": f"Full name column '{full_name_col}' not found in Excel file"}
        
        # Validate profile data columns
        if profile_data_cols:
            missing_cols = [col for col in profile_data_cols if col not in df.columns]
            if missing_cols:
                return {"error": f"Profile data columns {missing_cols} not found in Excel file"}
        
        # Process each row
        user_ids = []
        for _, row in df.iterrows():
            # Skip rows with missing usernames
            if pd.isna(row[username_col]):
                continue
            
            username = str(row[username_col])
            email = str(row[email_col]) if email_col and not pd.isna(row[email_col]) else None
            full_name = str(row[full_name_col]) if full_name_col and not pd.isna(row[full_name_col]) else None
            
            # Build profile data dictionary
            profile_data = {}
            if profile_data_cols:
                for col in profile_data_cols:
                    if col in df.columns and not pd.isna(row[col]):
                        profile_data[col] = row[col]
            
            try:
                user_id = db_manager.add_user(username, email, full_name, profile_data)
                user_ids.append(user_id)
            except Exception as e:
                # Skip duplicate users or other errors
                continue
        
        return {
            "success": True,
            "imported_users_count": len(user_ids),
            "user_ids": user_ids
        }
        
    except Exception as e:
        return {"error": f"Error importing users from Excel file: {str(e)}"}

def import_groups_from_excel(file_path: str, sheet_name: str = "Sheet1", name_col: str = None,
                            description_col: Optional[str] = None) -> Dict:
    """Import groups from an Excel file into the database.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to read
        name_col: Column name for group name
        description_col: Column name for group description
        
    Returns:
        Import results summary
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Validate required columns
        if name_col not in df.columns:
            return {"error": f"Group name column '{name_col}' not found in Excel file"}
        
        # Validate optional columns
        if description_col and description_col not in df.columns:
            return {"error": f"Description column '{description_col}' not found in Excel file"}
        
        # Process each row
        group_ids = []
        for _, row in df.iterrows():
            # Skip rows with missing group names
            if pd.isna(row[name_col]):
                continue
            
            name = str(row[name_col])
            description = str(row[description_col]) if description_col and not pd.isna(row[description_col]) else None
            
            try:
                group_id = db_manager.add_group(name, description)
                group_ids.append(group_id)
            except Exception as e:
                # Skip duplicate groups or other errors
                continue
        
        return {
            "success": True,
            "imported_groups_count": len(group_ids),
            "group_ids": group_ids
        }
        
    except Exception as e:
        return {"error": f"Error importing groups from Excel file: {str(e)}"}

def import_user_group_mappings_from_excel(file_path: str, sheet_name: str = "Sheet1", username_col: str = None,
                                         group_name_col: str = None, role_col: Optional[str] = None) -> Dict:
    """Import user-group mappings from an Excel file into the database.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to read
        username_col: Column name for username
        group_name_col: Column name for group name
        role_col: Column name for role
        
    Returns:
        Import results summary
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Validate required columns
        if username_col not in df.columns:
            return {"error": f"Username column '{username_col}' not found in Excel file"}
        if group_name_col not in df.columns:
            return {"error": f"Group name column '{group_name_col}' not found in Excel file"}
        
        # Validate optional columns
        if role_col and role_col not in df.columns:
            return {"error": f"Role column '{role_col}' not found in Excel file"}
        
        # Process each row
        mappings_added = 0
        errors = []
        
        for _, row in df.iterrows():
            # Skip rows with missing usernames or group names
            if pd.isna(row[username_col]) or pd.isna(row[group_name_col]):
                continue
            
            username = str(row[username_col])
            group_name = str(row[group_name_col])
            role = str(row[role_col]) if role_col and not pd.isna(row[role_col]) else "member"
            
            # Find user ID by username
            user_results = db_manager.search_users(username, limit=1)
            if not user_results:
                errors.append(f"User '{username}' not found")
                continue
            user_id = user_results[0]["id"]
            
            # Find group ID by name
            group_results = db_manager.search_groups(group_name, limit=1)
            if not group_results:
                errors.append(f"Group '{group_name}' not found")
                continue
            group_id = group_results[0]["id"]
            
            try:
                db_manager.add_user_to_group(user_id, group_id, role)
                mappings_added += 1
            except Exception as e:
                errors.append(f"Error adding {username} to {group_name}: {str(e)}")
                continue
        
        return {
            "success": True,
            "mappings_added": mappings_added,
            "errors": errors
        }
        
    except Exception as e:
        return {"error": f"Error importing user-group mappings from Excel file: {str(e)}"}

def import_activities_from_excel(file_path: str, sheet_name: str = "Sheet1", username_col: str = None,
                               activity_type_col: str = None, description_col: str = None,
                               points_col: Optional[str] = None, group_name_col: Optional[str] = None,
                               timestamp_col: Optional[str] = None, metadata_cols: Optional[List[str]] = None) -> Dict:
    """Import activities from an Excel file into the database.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to read
        username_col: Column name for username
        activity_type_col: Column name for activity type
        description_col: Column name for description
        points_col: Column name for points
        group_name_col: Column name for group name
        timestamp_col: Column name for timestamp
        metadata_cols: Columns to include in metadata
        
    Returns:
        Import results summary
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Validate required columns
        required_cols = [username_col, activity_type_col, description_col]
        missing_required = [col for col in required_cols if col not in df.columns]
        if missing_required:
            return {"error": f"Required columns {missing_required} not found in Excel file"}
        
        # Validate optional columns
        optional_cols = [col for col in [points_col, group_name_col, timestamp_col] if col]
        missing_optional = [col for col in optional_cols if col not in df.columns]
        if missing_optional:
            return {"error": f"Optional columns {missing_optional} not found in Excel file"}
        
        # Validate metadata columns
        if metadata_cols:
            missing_metadata = [col for col in metadata_cols if col not in df.columns]
            if missing_metadata:
                return {"error": f"Metadata columns {missing_metadata} not found in Excel file"}
        
        # Process each row
        activities_added = 0
        errors = []
        
        for _, row in df.iterrows():
            # Skip rows with missing required data
            if any(pd.isna(row[col]) for col in required_cols):
                continue
            
            username = str(row[username_col])
            activity_type = str(row[activity_type_col])
            description = str(row[description_col])
            points = int(row[points_col]) if points_col and not pd.isna(row[points_col]) else 0
            group_name = str(row[group_name_col]) if group_name_col and not pd.isna(row[group_name_col]) else None
            
            # Build metadata dictionary
            metadata = {}
            if metadata_cols:
                for col in metadata_cols:
                    if col in df.columns and not pd.isna(row[col]):
                        metadata[col] = row[col]
            
            if timestamp_col and not pd.isna(row[timestamp_col]):
                metadata["original_timestamp"] = str(row[timestamp_col])
            
            # Find user ID by username
            user_results = db_manager.search_users(username, limit=1)
            if not user_results:
                errors.append(f"User '{username}' not found")
                continue
            user_id = user_results[0]["id"]
            
            # Find group ID by name if group specified
            group_id = None
            if group_name:
                group_results = db_manager.search_groups(group_name, limit=1)
                if not group_results:
                    errors.append(f"Group '{group_name}' not found")
                    continue
                group_id = group_results[0]["id"]
            
            try:
                db_manager.add_activity(user_id, activity_type, description, points, group_id, metadata)
                activities_added += 1
            except Exception as e:
                errors.append(f"Error adding activity for {username}: {str(e)}")
                continue
        
        return {
            "success": True,
            "activities_added": activities_added,
            "errors": errors
        }
        
    except Exception as e:
        return {"error": f"Error importing activities from Excel file: {str(e)}"}

# Create function tools for ADK
EXCEL_TOOLS = [
    FunctionTool(read_excel, "read_excel", "Read data from an Excel file"),
    FunctionTool(import_users_from_excel, "import_users_from_excel", "Import users from an Excel file into the database"),
    FunctionTool(import_groups_from_excel, "import_groups_from_excel", "Import groups from an Excel file into the database"),
    FunctionTool(import_user_group_mappings_from_excel, "import_user_group_mappings_from_excel", "Import user-group mappings from an Excel file"),
    FunctionTool(import_activities_from_excel, "import_activities_from_excel", "Import activities from an Excel file")
]

# Create the Excel agent
excel_agent = LlmAgent(
    name="ExcelAgent",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("excel_agent_instruction.txt"),
    description="Specialized agent for processing Excel files for the dashboard system",
    tools=EXCEL_TOOLS,
    output_key="excel_result"
)