"""
File Utilities for SoPDF

This module contains utility functions for PDF file operations and common file tasks.
"""

import os
from pathlib import Path


def get_asset_path(asset_name):
    """
    Get the full path to an asset file.
    
    Args:
        asset_name (str): Name of the asset file
        
    Returns:
        str: Full path to the asset file
    """
    # Get the project root directory (two levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    asset_path = project_root / "assets" / asset_name
    return str(asset_path)


def get_docs_path(doc_name):
    """
    Get the full path to a documentation file.
    
    Args:
        doc_name (str): Name of the documentation file
        
    Returns:
        str: Full path to the documentation file
    """
    # Get the project root directory (two levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    docs_path = project_root / "docs" / doc_name
    return str(docs_path)


def ensure_file_extension(filename, extension):
    """
    Ensure a filename has the correct extension.
    
    Args:
        filename (str): The filename to check
        extension (str): The required extension (with or without dot)
        
    Returns:
        str: Filename with correct extension
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    
    if not filename.lower().endswith(extension.lower()):
        filename += extension
    
    return filename


def get_safe_filename(filename):
    """
    Create a safe filename by removing/replacing invalid characters.
    
    Args:
        filename (str): The original filename
        
    Returns:
        str: Safe filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure it's not empty
    if not filename:
        filename = "untitled"
    
    return filename


def format_file_size(size_bytes):
    """
    Format file size in bytes to human readable format.
    
    Args:
        size_bytes (int): File size in bytes
        
    Returns:
        str: Formatted file size (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_pdf_file(file_path):
    """
    Validate if a file is a valid PDF file.
    
    Args:
        file_path (str): Path to the file to validate
        
    Returns:
        bool: True if file is a valid PDF, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    if not file_path.lower().endswith('.pdf'):
        return False
    
    try:
        # Check if file has PDF header
        with open(file_path, 'rb') as f:
            header = f.read(5)
            return header == b'%PDF-'
    except Exception:
        return False 