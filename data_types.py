"""
Data types module - Defines data type mappings and configurations for synthetic data generation
"""

# Informatica to Python data type mapping
INFORMATICA_TO_PYTHON = {
    'string': 'str',
    'decimal': 'float',
    'integer': 'int',
    'biginteger': 'int',
    'double': 'float',
    'date': 'date',
    'timestamp': 'datetime',
    'boolean': 'bool',
    'blob': 'str'  # represented as string
}

# Default lengths for string types
DEFAULT_STRING_LENGTH = 50
DEFAULT_DECIMAL_PRECISION = 10
DEFAULT_DECIMAL_SCALE = 2

# Data type categories
NUMERIC_TYPES = ['integer', 'biginteger', 'decimal', 'double']
STRING_TYPES = ['string', 'varchar', 'char']
DATE_TYPES = ['date', 'timestamp', 'datetime']
BOOLEAN_TYPES = ['boolean']
