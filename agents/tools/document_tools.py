"""
Tools for processing document files (e.g., Word, PDF) and extracting data for the database.
"""
import os
import docx
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.db_manager import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager()


class ReadDocumentInput(BaseModel):
    file_path: str = Field(..., description="Path to the document file")


class ReadDocumentTool(BaseTool):
    name = "read_document"
    description = "Extract text from a document file (Word only for now)"
    args_schema = ReadDocumentInput

    def _run(self, file_path: str) -> Dict:
        """Extract text from a document file."""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.docx':
            try:
                doc = docx.Document(file_path)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                
                # Extract tables if any
                tables = []
                for table in doc.tables:
                    table_data = []
                    for row in table.rows:
                        row_data = [cell.text for cell in row.cells]
                        table_data.append(row_data)
                    tables.append(table_data)
                
                return {
                    "success": True,
                    "paragraphs": paragraphs,
                    "paragraph_count": len(paragraphs),
                    "tables": tables,
                    "table_count": len(tables)
                }
            except Exception as e:
                return {"error": f"Error reading Word document: {str(e)}"}
        else:
            return {"error": f"Unsupported file format: {file_ext}. Currently only .docx is supported."}


class ExtractUsersFromDocumentInput(BaseModel):
    file_path: str = Field(..., description="Path to the document file")
    extract_method: str = Field("structured", description="Extraction method: 'structured' or 'nlp'")


class ExtractUsersFromDocumentTool(BaseTool):
    name = "extract_users_from_document"
    description = "Extract user information from a document file"
    args_schema = ExtractUsersFromDocumentInput

    def _run(self, file_path: str, extract_method: str = "structured") -> Dict:
        """Extract user information from a document file."""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext != '.docx':
            return {"error": f"Unsupported file format: {file_ext}. Currently only .docx is supported."}
        
        try:
            doc = docx.Document(file_path)
            
            # Simple structured extraction (looks for tables with user data)
            if extract_method == "structured":
                extracted_users = []
                
                for table in doc.tables:
                    # Check if this table has user data by looking at headers
                    header_row = [cell.text.strip().lower() for cell in table.rows[0].cells] if table.rows else []
                    
                    # Check if the table has username or name columns
                    if any(header in header_row for header in ['username', 'user', 'name']):
                        username_idx = next((i for i, h in enumerate(header_row) if h in ['username', 'user']), None)
                        name_idx = next((i for i, h in enumerate(header_row) if h == 'name'), None)
                        email_idx = next((i for i, h in enumerate(header_row) if h == 'email'), None)
                        
                        # Process data rows
                        for row_idx in range(1, len(table.rows)):
                            row = table.rows[row_idx]
                            cells = [cell.text.strip() for cell in row.cells]
                            
                            # Skip empty rows
                            if not any(cells):
                                continue
                            
                            user_data = {}
                            
                            # Extract data based on identified columns
                            if username_idx is not None and username_idx < len(cells) and cells[username_idx]:
                                user_data['username'] = cells[username_idx]
                            elif name_idx is not None and name_idx < len(cells) and cells[name_idx]:
                                # Use name as username if no username column
                                user_data['username'] = cells[name_idx].replace(" ", "_").lower()
                                user_data['full_name'] = cells[name_idx]
                            else:
                                # Skip rows without username
                                continue
                            
                            if email_idx is not None and email_idx < len(cells) and cells[email_idx]:
                                user_data['email'] = cells[email_idx]
                            
                            # Add any other metadata
                            profile_data = {}
                            for i, header in enumerate(header_row):
                                if i not in [username_idx, name_idx, email_idx] and i < len(cells) and cells[i]:
                                    profile_data[header] = cells[i]
                            
                            if profile_data:
                                user_data['profile_data'] = profile_data
                            
                            extracted_users.append(user_data)
                
                return {
                    "success": True,
                    "users": extracted_users,
                    "count": len(extracted_users)
                }
            else:
                # For "nlp" method, we would use an LLM or NLP techniques
                # This is a simplistic approach that looks for certain patterns
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                
                # This is a placeholder - in a real implementation, 
                # you would use more sophisticated NLP techniques or an LLM
                return {
                    "success": False,
                    "error": "NLP extraction method not fully implemented.",
                    "paragraphs": paragraphs
                }
                
        except Exception as e:
            return {"error": f"Error extracting users from document: {str(e)}"}


class ExtractGroupsFromDocumentInput(BaseModel):
    file_path: str = Field(..., description="Path to the document file")
    extract_method: str = Field("structured", description="Extraction method: 'structured' or 'nlp'")


class ExtractGroupsFromDocumentTool(BaseTool):
    name = "extract_groups_from_document"
    description = "Extract group information from a document file"
    args_schema = ExtractGroupsFromDocumentInput

    def _run(self, file_path: str, extract_method: str = "structured") -> Dict:
        """Extract group information from a document file."""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext != '.docx':
            return {"error": f"Unsupported file format: {file_ext}. Currently only .docx is supported."}
        
        try:
            doc = docx.Document(file_path)
            
            # Simple structured extraction (looks for tables with group data)
            if extract_method == "structured":
                extracted_groups = []
                
                for table in doc.tables:
                    # Check if this table has group data by looking at headers
                    header_row = [cell.text.strip().lower() for cell in table.rows[0].cells] if table.rows else []
                    
                    # Check if the table has group name or related columns
                    if any(header in header_row for header in ['group', 'team', 'department']):
                        name_idx = next((i for i, h in enumerate(header_row) 
                                        if h in ['group', 'group name', 'team', 'department']), None)
                        desc_idx = next((i for i, h in enumerate(header_row) 
                                        if h in ['description', 'desc', 'details', 'info']), None)
                        
                        # Process data rows
                        for row_idx in range(1, len(table.rows)):
                            row = table.rows[row_idx]
                            cells = [cell.text.strip() for cell in row.cells]
                            
                            # Skip empty rows
                            if not any(cells):
                                continue
                            
                            group_data = {}
                            
                            # Extract data based on identified columns
                            if name_idx is not None and name_idx < len(cells) and cells[name_idx]:
                                group_data['name'] = cells[name_idx]
                            else:
                                # Skip rows without group name
                                continue
                            
                            if desc_idx is not None and desc_idx < len(cells) and cells[desc_idx]:
                                group_data['description'] = cells[desc_idx]
                            
                            extracted_groups.append(group_data)
                
                return {
                    "success": True,
                    "groups": extracted_groups,
                    "count": len(extracted_groups)
                }
            else:
                # For "nlp" method
                return {
                    "success": False,
                    "error": "NLP extraction method not fully implemented."
                }
                
        except Exception as e:
            return {"error": f"Error extracting groups from document: {str(e)}"}


class SaveUsersFromDocumentInput(BaseModel):
    file_path: str = Field(..., description="Path to the document file")


class SaveUsersFromDocumentTool(BaseTool):
    name = "save_users_from_document"
    description = "Extract users from document and save to the database"
    args_schema = SaveUsersFromDocumentInput

    def _run(self, file_path: str) -> Dict:
        """Extract users from document and save to the database."""
        # First extract users from the document
        extractor = ExtractUsersFromDocumentTool()
        extraction_result = extractor._run(file_path)
        
        if "error" in extraction_result:
            return extraction_result
        
        if not extraction_result.get("users", []):
            return {"success": False, "message": "No users found in the document"}
        
        # Save extracted users to the database
        users_added = 0
        user_ids = []
        errors = []
        
        for user_data in extraction_result["users"]:
            try:
                username = user_data.get("username")
                email = user_data.get("email")
                full_name = user_data.get("full_name")
                profile_data = user_data.get("profile_data", {})
                
                if not username:
                    errors.append("Skipped user with no username")
                    continue
                
                user_id = db_manager.add_user(username, email, full_name, profile_data)
                user_ids.append(user_id)
                users_added += 1
                
            except Exception as e:
                # Skip duplicate users or other errors
                errors.append(f"Error adding user {user_data.get('username')}: {str(e)}")
                continue
        
        return {
            "success": True,
            "users_added": users_added,
            "user_ids": user_ids,
            "errors": errors
        }


class SaveGroupsFromDocumentInput(BaseModel):
    file_path: str = Field(..., description="Path to the document file")


class SaveGroupsFromDocumentTool(BaseTool):
    name = "save_groups_from_document"
    description = "Extract groups from document and save to the database"
    args_schema = SaveGroupsFromDocumentInput

    def _run(self, file_path: str) -> Dict:
        """Extract groups from document and save to the database."""
        # First extract groups from the document
        extractor = ExtractGroupsFromDocumentTool()
        extraction_result = extractor._run(file_path)
        
        if "error" in extraction_result:
            return extraction_result
        
        if not extraction_result.get("groups", []):
            return {"success": False, "message": "No groups found in the document"}
        
        # Save extracted groups to the database
        groups_added = 0
        group_ids = []
        errors = []
        
        for group_data in extraction_result["groups"]:
            try:
                name = group_data.get("name")
                description = group_data.get("description")
                
                if not name:
                    errors.append("Skipped group with no name")
                    continue
                
                group_id = db_manager.add_group(name, description)
                group_ids.append(group_id)
                groups_added += 1
                
            except Exception as e:
                # Skip duplicate groups or other errors
                errors.append(f"Error adding group {group_data.get('name')}: {str(e)}")
                continue
        
        return {
            "success": True,
            "groups_added": groups_added,
            "group_ids": group_ids,
            "errors": errors
        }


# List of all document tools
DOCUMENT_TOOLS = [
    ReadDocumentTool(),
    ExtractUsersFromDocumentTool(),
    ExtractGroupsFromDocumentTool(),
    SaveUsersFromDocumentTool(),
    SaveGroupsFromDocumentTool()
]
