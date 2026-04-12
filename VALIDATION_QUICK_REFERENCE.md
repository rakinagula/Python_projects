# Data Validation - Quick Reference Guide

## Common Validation Rules - Copy & Paste Examples

### 1. Null Check (Disallow Nulls)

```json
{
  "field_name": "id",
  "rule_type": "null_check",
  "description": "ID cannot be null",
  "enabled": true,
  "rule_config": {
    "allow_null": false,
    "max_null_percentage": 0
  }
}
```

### 2. Null Check (Allow Nulls with Max Threshold)

```json
{
  "field_name": "optional_field",
  "rule_type": "null_check",
  "description": "Allow nulls but not more than 5%",
  "enabled": true,
  "rule_config": {
    "allow_null": true,
    "max_null_percentage": 5
  }
}
```

### 3. Number Range Validation

```json
{
  "field_name": "age",
  "rule_type": "range_check",
  "description": "Age should be 18-120",
  "enabled": true,
  "rule_config": {
    "min_value": 18,
    "max_value": 120
  }
}
```

### 4. Positive Number

```json
{
  "field_name": "amount",
  "rule_type": "range_check",
  "description": "Amount must be positive",
  "enabled": true,
  "rule_config": {
    "min_value": 0.01,
    "max_value": 999999.99
  }
}
```

### 5. Email Validation (Pattern)

```json
{
  "field_name": "email",
  "rule_type": "pattern_check",
  "description": "Valid email format",
  "enabled": true,
  "rule_config": {
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  }
}
```

### 6. Phone Number (US Format)

```json
{
  "field_name": "phone",
  "rule_type": "pattern_check",
  "description": "US phone number format",
  "enabled": true,
  "rule_config": {
    "pattern": "^\\d{3}-\\d{3}-\\d{4}$"
  }
}
```

### 7. Allowed Values (Status Field)

```json
{
  "field_name": "status",
  "rule_type": "allowed_values",
  "description": "Status must be one of predefined values",
  "enabled": true,
  "rule_config": {
    "values": ["Active", "Inactive", "Suspended", "Closed"]
  }
}
```

### 8. Unique Values (No Duplicates)

```json
{
  "field_name": "product_code",
  "rule_type": "uniqueness_check",
  "description": "Product codes must be unique",
  "enabled": true,
  "rule_config": {
    "allow_null_duplicates": false
  }
}
```

### 9. Unique Values (Allow Null Duplicates)

```json
{
  "field_name": "reference_id",
  "rule_type": "uniqueness_check",
  "description": "Reference IDs must be unique, multiple nulls allowed",
  "enabled": true,
  "rule_config": {
    "allow_null_duplicates": true
  }
}
```

### 10. Data Type Validation

```json
{
  "field_name": "price",
  "rule_type": "datatype_check",
  "description": "Price must be numeric",
  "enabled": true,
  "rule_config": {
    "expected_type": "float"
  }
}
```

---

## Complete Table Example

```json
{
  "table_name": "employees",
  "description": "Employee master data",
  "enabled": true,
  "validation_rules": [
    {
      "field_name": "employee_id",
      "rule_type": "null_check",
      "description": "Employee ID is required",
      "enabled": true,
      "rule_config": {"allow_null": false}
    },
    {
      "field_name": "employee_id",
      "rule_type": "uniqueness_check",
      "description": "Employee IDs must be unique",
      "enabled": true,
      "rule_config": {}
    },
    {
      "field_name": "employee_name",
      "rule_type": "null_check",
      "description": "Employee name is required",
      "enabled": true,
      "rule_config": {"allow_null": false}
    },
    {
      "field_name": "email",
      "rule_type": "pattern_check",
      "description": "Valid company email required",
      "enabled": true,
      "rule_config": {
        "pattern": "^[a-zA-Z0-9._%+-]+@company\\.com$"
      }
    },
    {
      "field_name": "salary",
      "rule_type": "range_check",
      "description": "Salary between 20000 and 500000",
      "enabled": true,
      "rule_config": {"min_value": 20000, "max_value": 500000}
    },
    {
      "field_name": "department",
      "rule_type": "allowed_values",
      "description": "Department must exist",
      "enabled": true,
      "rule_config": {
        "values": ["HR", "Sales", "Engineering", "Finance", "Operations"]
      }
    },
    {
      "field_name": "hire_date",
      "rule_type": "null_check",
      "description": "Hire date is required",
      "enabled": true,
      "rule_config": {"allow_null": false}
    }
  ]
}
```

---

## Common Regex Patterns

### Email
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

### Phone (US Format: 123-456-7890)
```
^\d{3}-\d{3}-\d{4}$
```

### ZIP Code (US)
```
^\d{5}(-\d{4})?$
```

### Date (YYYY-MM-DD)
```
^\d{4}-\d{2}-\d{2}$
```

### Credit Card (16 digits)
```
^\d{16}$
```

### URL
```
^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$
```

### Alphanumeric Only
```
^[a-zA-Z0-9]+$
```

### No Special Characters
```
^[a-zA-Z0-9\s]*$
```

---

## Disabling a Rule Temporarily

To disable a rule without removing it from the config:

```json
{
  "field_name": "field_name",
  "rule_type": "rule_type",
  "enabled": false,
  "rule_config": {}
}
```

---

## Minimal Configuration Template

```json
{
  "validation_config": {
    "version": "1.0",
    "description": "My validation config"
  },
  "database_connection": {
    "db_type": "sqlite",
    "database": "data.db"
  },
  "validation_tables": [
    {
      "table_name": "my_table",
      "enabled": true,
      "validation_rules": []
    }
  ]
}
```

---

## Command Line Examples

### Basic validation
```bash
python validate_data.py -c validation_config.json -d my_database.db
```

### Parallel validation with output
```bash
python validate_data.py -c validation_config.json -d my_database.db --parallel -o report.json
```

### With 8 workers
```bash
python validate_data.py -c validation_config.json -d my_database.db --parallel --workers 8
```

### Verbose mode
```bash
python validate_data.py -c validation_config.json -d my_database.db -v
```

---

## Python Code Examples

### Simple validation with report
```python
from data_validator import DataValidationManager
import sqlite3

conn = sqlite3.connect('test.db')
validator = DataValidationManager('validation_config.json', conn)
validator.validate_all_tables()
validator.print_summary()
validator.save_report_to_file('report.json')
conn.close()
```

### Parallel validation
```python
validator.validate_all_tables(use_parallel=True, max_workers=4)
```

### Single table validation
```python
table_name, results = validator.validate_single_table('customers')
for result in results:
    print(f"{result.field_name}: {'✓ PASS' if result.passed else '✗ FAIL'}")
```

### Custom rules programmatically
```python
from data_validator import ValidationRule, TableValidator

rules = [
    ValidationRule({'field_name': 'id', 'rule_type': 'null_check', 
                   'rule_config': {'allow_null': False}}),
    ValidationRule({'field_name': 'email', 'rule_type': 'pattern_check',
                   'rule_config': {'pattern': '^[^@]+@[^@]+\.[^@]+$'}})
]
validator = TableValidator(conn, 'users', rules)
results = validator.run_all_validations()
```

---

## Tips & Tricks

1. **Test patterns locally** before adding to config using Python:
   ```python
   import re
   pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
   print(re.match(pattern, "test@example.com"))  # True
   ```

2. **Preview rules** - Enable only a couple rules first to verify configuration

3. **Use descriptions** - Add meaningful descriptions to help understand rule purpose

4. **Group rules** - Put all rules for one field together for readability

5. **Handle edge cases** - Test with sample data that has nulls and edge values

---

**Version:** 1.0  
**Last Updated:** April 12, 2026
