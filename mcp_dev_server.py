
"""
MCP Server with Developer Tools using FastMCP
Provides common developer tools like file operations, directory listing, etc.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import aiofiles
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Developer Tools Server 🛠️")

# File Operations Tools

@mcp.tool()
async def read_file(path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        path: Path to the file to read
        
    Returns:
        Contents of the file as a string
    """
    try:
        async with aiofiles.open(path, 'r') as f:
            content = await f.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
async def write_file(path: str, content: str) -> str:
    """
    Write content to a file. Creates the file if it doesn't exist.
    
    Args:
        path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success message or error
    """
    try:
        # Create parent directories if they don't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(path, 'w') as f:
            await f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool()
async def append_file(path: str, content: str) -> str:
    """
    Append content to an existing file.
    
    Args:
        path: Path to the file to append to
        content: Content to append to the file
        
    Returns:
        Success message or error
    """
    try:
        async with aiofiles.open(path, 'a') as f:
            await f.write(content)
        return f"Successfully appended to {path}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error appending to file: {str(e)}"


@mcp.tool()
def delete_file(path: str) -> str:
    """
    Delete a file.
    
    Args:
        path: Path to the file to delete
        
    Returns:
        Success message or error
    """
    try:
        os.remove(path)
        return f"Successfully deleted {path}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"


# Directory Operations Tools

@mcp.tool()
def list_directory(path: str = ".", recursive: bool = False) -> Dict[str, Any]:
    """
    List contents of a directory.
    
    Args:
        path: Path to the directory to list (default: current directory)
        recursive: Whether to list recursively
        
    Returns:
        Dictionary containing files and directories
    """
    try:
        result = {"path": path, "files": [], "directories": []}
        
        if recursive:
            for root, dirs, files in os.walk(path):
                rel_root = os.path.relpath(root, path)
                if rel_root == ".":
                    rel_root = ""
                    
                for d in dirs:
                    dir_path = os.path.join(rel_root, d) if rel_root else d
                    result["directories"].append(dir_path)
                    
                for f in files:
                    file_path = os.path.join(rel_root, f) if rel_root else f
                    result["files"].append(file_path)
        else:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    result["directories"].append(item)
                else:
                    result["files"].append(item)
                    
        return result
    except FileNotFoundError:
        return {"error": f"Directory not found: {path}"}
    except Exception as e:
        return {"error": f"Error listing directory: {str(e)}"}


@mcp.tool()
def create_directory(path: str) -> str:
    """
    Create a directory (including parent directories if needed).
    
    Args:
        path: Path to the directory to create
        
    Returns:
        Success message or error
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return f"Successfully created directory: {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


@mcp.tool()
def delete_directory(path: str, recursive: bool = False) -> str:
    """
    Delete a directory.
    
    Args:
        path: Path to the directory to delete
        recursive: Whether to delete recursively (including contents)
        
    Returns:
        Success message or error
    """
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        return f"Successfully deleted directory: {path}"
    except FileNotFoundError:
        return f"Error: Directory not found: {path}"
    except OSError as e:
        if not recursive and e.errno == 39:  # Directory not empty
            return f"Error: Directory not empty: {path}. Use recursive=True to delete non-empty directories."
        return f"Error deleting directory: {str(e)}"
    except Exception as e:
        return f"Error deleting directory: {str(e)}"


@mcp.tool()
def move_file(source: str, destination: str) -> str:
    """
    Move or rename a file or directory.
    
    Args:
        source: Source path
        destination: Destination path
        
    Returns:
        Success message or error
    """
    try:
        shutil.move(source, destination)
        return f"Successfully moved {source} to {destination}"
    except FileNotFoundError:
        return f"Error: Source not found: {source}"
    except Exception as e:
        return f"Error moving file: {str(e)}"


@mcp.tool()
def copy_file(source: str, destination: str) -> str:
    """
    Copy a file or directory.
    
    Args:
        source: Source path
        destination: Destination path
        
    Returns:
        Success message or error
    """
    try:
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        return f"Successfully copied {source} to {destination}"
    except FileNotFoundError:
        return f"Error: Source not found: {source}"
    except Exception as e:
        return f"Error copying: {str(e)}"


# Code Execution Tools

@mcp.tool()
def execute_command(command: str, working_dir: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute a shell command.
    
    Args:
        command: Command to execute
        working_dir: Working directory for the command (optional)
        timeout: Timeout in seconds (default: 30)
        
    Returns:
        Dictionary with stdout, stderr, and return code
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=timeout
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "error": f"Command timed out after {timeout} seconds",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Error executing command: {str(e)}",
            "success": False
        }


@mcp.tool()
def execute_python(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute Python code and return the result.
    
    Args:
        code: Python code to execute
        timeout: Timeout in seconds (default: 30)
        
    Returns:
        Dictionary with output and any errors
    """
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "error": f"Code execution timed out after {timeout} seconds",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Error executing Python code: {str(e)}",
            "success": False
        }


# Search and Analysis Tools

@mcp.tool()
def search_files(pattern: str, path: str = ".", file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for text pattern in files.
    
    Args:
        pattern: Text pattern to search for
        path: Directory to search in (default: current directory)
        file_pattern: File pattern to match (e.g., "*.py")
        
    Returns:
        List of matches with file path and line information
    """
    import fnmatch
    
    matches = []
    
    try:
        for root, _, files in os.walk(path):
            for file in files:
                if file_pattern and not fnmatch.fnmatch(file, file_pattern):
                    continue
                    
                file_path = os.path.join(root, file)
                
                # Skip binary files
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line_num, line in enumerate(lines, 1):
                            if pattern in line:
                                matches.append({
                                    "file": file_path,
                                    "line_number": line_num,
                                    "line": line.strip(),
                                    "context": "".join(lines[max(0, line_num-2):min(len(lines), line_num+1)])
                                })
                except (UnicodeDecodeError, PermissionError):
                    # Skip files that can't be read as text
                    continue
                    
        return matches
    except Exception as e:
        return [{"error": f"Error searching files: {str(e)}"}]


@mcp.tool()
def get_file_info(path: str) -> Dict[str, Any]:
    """
    Get detailed information about a file or directory.
    
    Args:
        path: Path to the file or directory
        
    Returns:
        Dictionary with file/directory information
    """
    try:
        stat = os.stat(path)
        
        info = {
            "path": path,
            "exists": True,
            "is_file": os.path.isfile(path),
            "is_directory": os.path.isdir(path),
            "size": stat.st_size,
            "modified_time": stat.st_mtime,
            "created_time": stat.st_ctime,
            "permissions": oct(stat.st_mode)[-3:]
        }
        
        if os.path.isfile(path):
            info["extension"] = os.path.splitext(path)[1]
            
            # Try to count lines if it's a text file
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    info["line_count"] = sum(1 for _ in f)
                    info["is_text"] = True
            except (UnicodeDecodeError, PermissionError):
                info["is_text"] = False
                
        return info
    except FileNotFoundError:
        return {"path": path, "exists": False}
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}


# Git Operations Tools

@mcp.tool()
def git_status(repo_path: str = ".") -> Dict[str, Any]:
    """
    Get git repository status.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
        
    Returns:
        Dictionary with git status information
    """
    result = execute_command("git status --porcelain", working_dir=repo_path)
    
    if result.get("success"):
        lines = result["stdout"].strip().split("\n") if result["stdout"] else []
        
        status = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": [],
            "renamed": []
        }
        
        for line in lines:
            if not line:
                continue
                
            status_code = line[:2]
            file_path = line[3:]
            
            if "M" in status_code:
                status["modified"].append(file_path)
            elif "A" in status_code:
                status["added"].append(file_path)
            elif "D" in status_code:
                status["deleted"].append(file_path)
            elif "??" in status_code:
                status["untracked"].append(file_path)
            elif "R" in status_code:
                status["renamed"].append(file_path)
                
        # Get current branch
        branch_result = execute_command("git branch --show-current", working_dir=repo_path)
        status["branch"] = branch_result["stdout"].strip() if branch_result.get("success") else "unknown"
        
        return status
    else:
        return {"error": "Not a git repository or git not available"}


@mcp.tool()
def git_diff(file_path: Optional[str] = None, repo_path: str = ".") -> str:
    """
    Get git diff for a file or all changes.
    
    Args:
        file_path: Specific file to diff (optional)
        repo_path: Path to the git repository (default: current directory)
        
    Returns:
        Diff output as string
    """
    command = f"git diff {file_path}" if file_path else "git diff"
    result = execute_command(command, working_dir=repo_path)
    
    if result.get("success"):
        return result["stdout"] if result["stdout"] else "No changes"
    else:
        return f"Error: {result.get('stderr', 'Unknown error')}"


# Main entry point
if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

