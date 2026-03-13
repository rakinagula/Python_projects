"""
Utility functions and validators for Informatica Framework
Purpose: Helper functions for configuration validation and file handling
"""

import json
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path


logger = logging.getLogger(__name__)


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_mapping_data(mapping_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate mapping data structure
    
    Args:
        mapping_data: Dictionary containing mapping data
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    required_fields = ['mapping_name', 'source_table', 'target_table', 'columns']
    for field in required_fields:
        if field not in mapping_data or not mapping_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate columns
    if 'columns' in mapping_data:
        if not isinstance(mapping_data['columns'], list):
            errors.append("Columns must be a list")
        elif len(mapping_data['columns']) == 0:
            errors.append("At least one column must be defined")
        else:
            for idx, col in enumerate(mapping_data['columns']):
                col_errors = validate_column(col, idx)
                errors.extend(col_errors)
    
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_column(column: Dict[str, Any], index: int) -> List[str]:
    """
    Validate column definition
    
    Args:
        column: Column dictionary
        index: Column index for error reporting
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if 'column_name' not in column or not column['column_name']:
        errors.append(f"Column {index}: Missing column_name")
    
    if 'data_type' not in column or not column['data_type']:
        errors.append(f"Column {index}: Missing data_type")
    else:
        valid_types = [
            'INT', 'INTEGER', 'BIGINT', 'DECIMAL', 'FLOAT', 'DOUBLE',
            'VARCHAR', 'CHAR', 'TEXT', 'DATE', 'DATETIME', 'TIMESTAMP',
            'BOOLEAN', 'BIT'
        ]
        if column['data_type'].upper() not in valid_types:
            errors.append(f"Column {index}: Invalid data_type '{column['data_type']}'")
    
    return errors


def validate_configuration(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate generated configuration structure
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check main sections
    required_sections = ['metadata', 'mapping', 'syntheticDataGeneration']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")
    
    # Validate metadata
    if 'metadata' in config:
        metadata = config['metadata']
        if 'generatedDate' not in metadata:
            errors.append("Metadata: Missing generatedDate")
    
    # Validate mapping
    if 'mapping' in config:
        mapping = config['mapping']
        required_mapping_fields = ['name', 'source', 'target']
        for field in required_mapping_fields:
            if field not in mapping:
                errors.append(f"Mapping: Missing {field}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


# ============================================================================
# FILE HANDLING FUNCTIONS
# ============================================================================

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary containing JSON data
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded JSON from: {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {str(e)}")
        raise


def save_json_file(data: Dict[str, Any], file_path: str, pretty: bool = True) -> bool:
    """
    Save data to JSON file
    
    Args:
        data: Dictionary to save
        file_path: Path to save file
        pretty: Whether to pretty-print JSON
        
    Returns:
        Boolean indicating success
    """
    try:
        file_obj = Path(file_path)
        file_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
        
        logger.info(f"Successfully saved JSON to: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file: {str(e)}")
        return False


# ============================================================================
# STRING AND FORMAT FUNCTIONS
# ============================================================================

def camel_case_to_snake_case(name: str) -> str:
    """Convert camelCase to snake_case"""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('_')
            result.append(char.lower())
        else:
            result.append(char)
    return ''.join(result)


def snake_case_to_camel_case(name: str) -> str:
    """Convert snake_case to camelCase"""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def sanitize_table_name(table_name: str) -> str:
    """Sanitize table name for safe usage"""
    return table_name.strip().upper().replace(' ', '_')


def sanitize_column_name(column_name: str) -> str:
    """Sanitize column name for safe usage"""
    return column_name.strip().upper().replace(' ', '_')


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

def log_validation_errors(errors: List[str], context: str = "") -> None:
    """Log validation errors"""
    if errors:
        logger.warning(f"Validation errors {context}:")
        for error in errors:
            logger.warning(f"  - {error}")


def log_processing_summary(total: int, successful: int, failed: int) -> None:
    """Log processing summary"""
    logger.info("=" * 60)
    logger.info(f"Processing Summary:")
    logger.info(f"  Total Items: {total}")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Success Rate: {(successful/total*100 if total > 0 else 0):.1f}%")
    logger.info("=" * 60)


# ============================================================================
# DATA TRANSFORMATION FUNCTIONS
# ============================================================================

def get_data_type_category(data_type: str) -> str:
    """
    Categorize data type
    
    Args:
        data_type: Data type string
        
    Returns:
        Category name
    """
    data_type_upper = data_type.upper()
    
    if any(x in data_type_upper for x in ['INT', 'DECIMAL', 'FLOAT', 'DOUBLE', 'NUMERIC']):
        return 'NUMERIC'
    elif any(x in data_type_upper for x in ['VARCHAR', 'CHAR', 'TEXT', 'STRING']):
        return 'STRING'
    elif any(x in data_type_upper for x in ['DATE', 'DATETIME', 'TIMESTAMP', 'TIME']):
        return 'TEMPORAL'
    elif any(x in data_type_upper for x in ['BOOLEAN', 'BIT', 'INT']):
        return 'BOOLEAN'
    else:
        return 'OTHER'


def get_default_length_for_type(data_type: str) -> int:
    """Get default length for data type"""
    data_type_upper = data_type.upper()
    
    defaults = {
        'VARCHAR': 255,
        'CHAR': 50,
        'TEXT': 1000,
        'BIGINT': 20,
        'INT': 11,
        'DECIMAL': 18
    }
    
    for key, value in defaults.items():
        if key in data_type_upper:
            return value
    
    return 50  # Default fallback
