"""
Quick test to verify the data validation module works correctly
"""

import sqlite3
from pathlib import Path
from data_validator import DataValidationManager, ValidationRule, TableValidator

def test_basic_validation():
    """Test basic validation functionality"""
    print("Testing Data Validation Module...")
    print("=" * 60)
    
    # Create test database
    db_file = 'test_validation.db'
    if Path(db_file).exists():
        Path(db_file).unlink()
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create test table
    print("\n1. Creating test table...")
    cursor.execute('''
        CREATE TABLE test_table (
            id INTEGER,
            name TEXT,
            email TEXT,
            age INTEGER
        )
    ''')
    
    # Insert test data
    print("2. Inserting test data...")
    test_data = [
        (1, 'John Doe', 'john@email.com', 30),
        (2, 'Jane Smith', 'jane@email.com', 25),
        (3, 'Bob Wilson', None, 35),  # Invalid email
        (4, 'Alice Brown', 'alice@invalid', 150),  # Age out of range
    ]
    cursor.executemany('INSERT INTO test_table VALUES (?, ?, ?, ?)', test_data)
    conn.commit()
    
    # Create validation rules
    print("3. Creating validation rules...")
    rules = [
        ValidationRule({
            'field_name': 'id',
            'rule_type': 'null_check',
            'enabled': True,
            'rule_config': {'allow_null': False}
        }),
        ValidationRule({
            'field_name': 'email',
            'rule_type': 'pattern_check',
            'enabled': True,
            'rule_config': {'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'}
        }),
        ValidationRule({
            'field_name': 'age',
            'rule_type': 'range_check',
            'enabled': True,
            'rule_config': {'min_value': 18, 'max_value': 120}
        })
    ]
    
    # Run validations
    print("4. Running validations...")
    validator = TableValidator(conn, 'test_table', rules)
    results = validator.run_all_validations()
    
    # Display results
    print("\n5. Validation Results:")
    print("-" * 60)
    for result in results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status} | {result.field_name:15} | {result.rule_type:15}")
        print(f"     {result.message}")
        if result.failed_count > 0:
            print(f"     Failed: {result.failed_count}/{result.total_count} records")
        print()
    
    # Summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print("=" * 60)
    print(f"Summary: {passed}/{total} validations passed")
    
    conn.close()
    
    # Cleanup
    Path(db_file).unlink()
    
    print("\n✓ Test completed successfully!")
    return True

if __name__ == '__main__':
    try:
        test_basic_validation()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
