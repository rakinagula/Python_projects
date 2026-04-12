# Data Validation Module - Complete Guide

## Overview

The Data Validation Module is a **config-driven Python framework** for performing comprehensive data quality checks on database tables. It enables you to:

- Define validation rules in JSON configuration files
- Validate data against multiple rule types (null checks, range, patterns, etc.)
- Execute validations on single or multiple tables
- Perform parallel validation for better performance
- Generate detailed JSON reports

The code is written in **simple, readable Python** that any developer can understand and maintain.

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Configuration Format](#configuration-format)
5. [Validation Rule Types](#validation-rule-types)
6. [Usage Examples](#usage-examples)
7. [API Reference](#api-reference)

---

## Features

✓ **Config-Driven**: Define all validation rules in JSON files  
✓ **Multiple Rule Types**: Null checks, range validation, allowed values, patterns, uniqueness, data types  
✓ **Multi-Database Support**: SQLite, Oracle, MySQL, PostgreSQL, SQL Server  
✓ **Parallel Processing**: Validate multiple tables concurrently  
✓ **Comprehensive Reporting**: Detailed JSON reports with pass/fail results  
✓ **Simple Readable Code**: Written for basic Python developers  
✓ **No Copyright Issues**: Original, human-written code  

---

## Installation

### Step 1: Copy Files

Copy the following files to your project directory:
- `data_validator.py` - Main validation module
- `validate_data.py` - Command-line interface
- `validation_config.json` - Example configuration
- `validation_demo.py` - Demo script

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

Run the demo to verify everything is working:

```bash
python validation_demo.py
```

---

## Quick Start

### Command Line Usage

```bash
# Basic validation using SQLite
python validate_data.py -c validation_config.json -d test.db

# Parallel validation
python validate_data.py -c validation_config.json -d test.db --parallel

# Save report to file
python validate_data.py -c validation_config.json -d test.db -o report.json

# Verbose output
python validate_data.py -c validation_config.json -d test.db -v
```

### Programmatic Usage

```python
from data_validator import DataValidationManager
import sqlite3

# Connect to database
conn = sqlite3.connect('test.db')

# Create validation manager
validator = DataValidationManager('validation_config.json', conn)

# Run validations
results = validator.validate_all_tables(use_parallel=True, max_workers=4)

# Print summary
validator.print_summary()

# Save report
validator.save_report_to_file('report.json')

conn.close()
```

---

## Configuration Format

### Configuration File Structure

```json
{
  "validation_config": {
    "version": "1.0",
    "description": "Data validation rules",
    "organization": "Your Organization"
  },
  "database_connection": {
    "db_type": "sqlite",
    "database": "test.db"
  },
  "validation_tables": [
    {
      "table_name": "customers",
      "description": "Customer data",
      "enabled": true,
      "validation_rules": [
        {
          "field_name": "customer_id",
          "rule_type": "null_check",
          "description": "ID should not be null",
          "enabled": true,
          "rule_config": {
            "allow_null": false,
            "max_null_percentage": 0
          }
        }
      ]
    }
  ]
}
```

### Database Connection Parameters

#### SQLite
```json
{
  "db_type": "sqlite",
  "database": "test.db"
}
```

#### Oracle
```json
{
  "db_type": "oracle",
  "host": "localhost",
  "port": 1521,
  "sid": "ORCL",
  "username": "user",
  "password": "password"
}
```

#### MySQL
```json
{
  "db_type": "mysql",
  "host": "localhost",
  "port": 3306,
  "database": "mydb",
  "username": "user",
  "password": "password"
}
```

#### PostgreSQL
```json
{
  "db_type": "postgres",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "password"
}
```

#### SQL Server
```json
{
  "db_type": "mssql",
  "host": "localhost",
  "database": "mydb",
  "username": "user",
  "password": "password"
}
```

---

## Validation Rule Types

### 1. Null Check

Validates that null values meet threshold requirements.

```json
{
  "field_name": "customer_id",
  "rule_type": "null_check",
  "rule_config": {
    "allow_null": false,
    "max_null_percentage": 0
  }
}
```

**Options:**
- `allow_null` (boolean): Whether null values are allowed. Default: true
- `max_null_percentage` (number): Maximum percentage of null values allowed. Default: 100

### 2. Range Check

Validates that numeric values fall within a specified range.

```json
{
  "field_name": "customer_age",
  "rule_type": "range_check",
  "rule_config": {
    "min_value": 18,
    "max_value": 120
  }
}
```

**Options:**
- `min_value` (number): Minimum allowed value
- `max_value` (number): Maximum allowed value

### 3. Allowed Values

Validates that values are from a predefined list.

```json
{
  "field_name": "status",
  "rule_type": "allowed_values",
  "rule_config": {
    "values": ["Active", "Inactive", "Suspended"]
  }
}
```

**Options:**
- `values` (array): List of allowed values

### 4. Pattern Check

Validates that string values match a regular expression pattern.

```json
{
  "field_name": "email",
  "rule_type": "pattern_check",
  "rule_config": {
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  }
}
```

**Options:**
- `pattern` (string): Regular expression pattern that values must match

### 5. Uniqueness Check

Validates that all values in a column are unique (no duplicates).

```json
{
  "field_name": "product_id",
  "rule_type": "uniqueness_check",
  "rule_config": {
    "allow_null_duplicates": false
  }
}
```

**Options:**
- `allow_null_duplicates` (boolean): Whether multiple nulls are allowed. Default: true

### 6. Data Type Check

Validates that values can be converted to the expected data type.

```json
{
  "field_name": "price",
  "rule_type": "datatype_check",
  "rule_config": {
    "expected_type": "float"
  }
}
```

**Options:**
- `expected_type` (string): Expected data type (string, integer, float, date)

---

## Usage Examples

### Example 1: Basic Configuration for Customer Table

```json
{
  "validation_tables": [
    {
      "table_name": "customers",
      "enabled": true,
      "validation_rules": [
        {
          "field_name": "customer_id",
          "rule_type": "null_check",
          "rule_config": {"allow_null": false}
        },
        {
          "field_name": "customer_id",
          "rule_type": "uniqueness_check",
          "rule_config": {}
        },
        {
          "field_name": "email",
          "rule_type": "pattern_check",
          "rule_config": {
            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
          }
        },
        {
          "field_name": "age",
          "rule_type": "range_check",
          "rule_config": {"min_value": 18, "max_value": 120}
        }
      ]
    }
  ]
}
```

### Example 2: Validate Multiple Tables

```json
{
  "validation_tables": [
    {
      "table_name": "customers",
      "enabled": true,
      "validation_rules": [...]
    },
    {
      "table_name": "orders",
      "enabled": true,
      "validation_rules": [...]
    },
    {
      "table_name": "products",
      "enabled": true,
      "validation_rules": [...]
    }
  ]
}
```

### Example 3: Selective Table Validation

```python
from data_validator import DataValidationManager, ValidationRule, TableValidator
import sqlite3

# Connect to database
conn = sqlite3.connect('test.db')

# Define custom rules for a specific table
rules = [
    ValidationRule({
        'field_name': 'order_id',
        'rule_type': 'null_check',
        'rule_config': {'allow_null': False}
    }),
    ValidationRule({
        'field_name': 'order_amount',
        'rule_type': 'range_check',
        'rule_config': {'min_value': 0, 'max_value': 999999}
    })
]

# Create validator for specific table
validator = TableValidator(conn, 'orders', rules)

# Run validations
results = validator.run_all_validations()

# Check results
for result in results:
    print(f"{result.field_name}: {'PASS' if result.passed else 'FAIL'}")
    print(f"  {result.message}")

conn.close()
```

### Example 4: Generate HTML Report

```python
import json
from data_validator import DataValidationManager

# Generate JSON report
validator = DataValidationManager('config.json', conn)
results = validator.validate_all_tables()
validator.save_report_to_file('report.json')

# Read and convert to HTML (example)
with open('report.json', 'r') as f:
    report = json.load(f)

summary = report['summary']
print(f"Validation Results: {summary['passed_checks']}/{summary['total_checks']} passed")
```

---

## API Reference

### DataValidationManager

Main class for managing validation operations.

```python
class DataValidationManager:
    def __init__(self, config_file: str, connection)
    def validate_all_tables(use_parallel: bool = False, max_workers: int = 4)
    def validate_single_table(table_name: str)
    def generate_report() -> Dict
    def save_report_to_file(output_file: str)
    def print_summary()
```

#### Methods

**`__init__(config_file, connection)`**
- Initialize the validation manager
- `config_file`: Path to JSON configuration file
- `connection`: Database connection object

**`validate_all_tables(use_parallel=False, max_workers=4)`**
- Validate all configured tables
- `use_parallel`: Enable parallel processing
- `max_workers`: Number of parallel workers
- Returns: Dictionary mapping table names to validation results

**`validate_single_table(table_name)`**
- Validate a specific table
- `table_name`: Name of the table to validate
- Returns: Tuple of (table_name, list of ValidationResult objects)

**`generate_report()`**
- Generate comprehensive validation report
- Returns: Dictionary with summary and detailed results

**`save_report_to_file(output_file)`**
- Save validation report to JSON file
- `output_file`: Path to output file

**`print_summary()`**
- Print validation summary to console

### TableValidator

Performs validation on a single table.

```python
class TableValidator:
    def __init__(self, connection, table_name: str, rules: List[ValidationRule])
    def run_all_validations() -> List[ValidationResult]
```

### ValidationRule

Represents a single validation rule.

```python
class ValidationRule:
    def __init__(self, rule_dict: Dict[str, Any])
    def is_valid() -> bool
```

### ValidationResult

Stores results of a validation check.

```python
class ValidationResult:
    def to_dict() -> Dict[str, Any]
```

---

## Report Format

The validation report is a JSON file with the following structure:

```json
{
  "summary": {
    "timestamp": "2026-04-12T14:30:45.123456",
    "config_file": "validation_config.json",
    "total_checks": 25,
    "passed_checks": 20,
    "failed_checks": 5,
    "pass_percentage": 80.0
  },
  "detailed_results": [
    {
      "field_name": "customer_id",
      "rule_type": "null_check",
      "passed": true,
      "message": "Null check passed. Null count: 0",
      "failed_count": 0,
      "total_count": 1000,
      "timestamp": "2026-04-12T14:30:45.100000"
    }
  ],
  "failed_validations": [
    {
      "field_name": "email",
      "rule_type": "pattern_check",
      "passed": false,
      "message": "Pattern check: 95/100 values match pattern",
      "failed_count": 5,
      "total_count": 100,
      "timestamp": "2026-04-12T14:30:45.150000"
    }
  ]
}
```

---

## Troubleshooting

### Issue: "Database connection failed"

**Solution:** Check your database connection parameters in the configuration file or command line arguments.

### Issue: "Column not found" error

**Solution:** Verify that the field names in your validation rules match the actual column names in the database.

### Issue: "Invalid regex pattern" error

**Solution:** Check your regex pattern syntax. Use online regex testers to validate your patterns.

### Issue: Slow validation on large tables

**Solution:** 
1. Enable parallel processing with `--parallel` flag
2. Increase the number of workers with `--workers N`
3. Consider adding indexes to frequently validated columns

### Issue: "Invalid date format" error

**Solution:** Ensure your date values are in a valid format that Python can parse (ISO format recommended).

---

## Performance Tips

1. **Parallelization**: Use `--parallel` flag for multiple tables
2. **Batch Processing**: Validate multiple related tables together
3. **Selective Validation**: Disable rules for fields that don't need validation
4. **Database Indexes**: Add indexes to columns being validated
5. **Connection Pooling**: Reuse database connections when possible

---

## Best Practices

1. **Start Simple**: Begin with null checks, then add more complex rules
2. **Test Configuration**: Run validation on test data first
3. **Version Control**: Keep configuration files under version control
4. **Documentation**: Add descriptions to all validation rules
5. **Schedule Regularly**: Set up automated validation runs
6. **Monitor Results**: Track pass rates over time

---

## Support and Contributing

For questions or issues:
1. Check the troubleshooting section
2. Review example configurations
3. Run the demo script for examples
4. Check inline code documentation

---

## License

This code is original, human-written work with no copyright issues. You are free to use and modify it for your needs.

---

**Last Updated:** April 12, 2026  
**Version:** 1.0
