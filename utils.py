"""
Utility functions - Helper functions for the framework
"""

import json
import os
from typing import Any, Dict, List
from datetime import datetime


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save dictionary to JSON file with pretty formatting.
    
    Args:
        data: Dictionary to save
        filepath: Path where to save the JSON file
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON configuration saved to: {filepath}")
    except Exception as e:
        print(f"✗ Error saving JSON: {str(e)}")
        raise


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON file and return as dictionary.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Dictionary loaded from JSON
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON format: {str(e)}")
        raise


def validate_xml_file(filepath: str) -> bool:
    """
    Check if file exists and has .xml extension.
    
    Args:
        filepath: Path to check
        
    Returns:
        True if valid XML file, False otherwise
    """
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return False
    
    if not filepath.lower().endswith('.xml'):
        print(f"✗ File is not an XML file: {filepath}")
        return False
    
    return True


def get_output_filename(input_file: str, output_type: str) -> str:
    """
    Generate output filename based on input file and output type.
    
    Args:
        input_file: Input XML file path
        output_type: Type of output ('config' or 'data')
        
    Returns:
        Generated filename
    """
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    if output_type == 'config':
        return f"{base_name}_config.json"
    elif output_type == 'data':
        return f"{base_name}_synthetic_data.json"
    else:
        return f"{base_name}_output.json"


def print_summary(title: str, details: Dict[str, Any]) -> None:
    """
    Print formatted summary information.
    
    Args:
        title: Summary title
        details: Dictionary of details to print
    """
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    for key, value in details.items():
        print(f"{key}: {value}")
    print(f"{'='*60}\n")
